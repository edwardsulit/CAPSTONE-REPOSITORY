import pandas as pd
import requests
from io import StringIO
import re
import os
import sys
import tkinter as tk
from tkinter import filedialog


# --- Unit normalization helpers ---
UNIT_ALIASES = {
    'pcs': {'pc','pcs','piece','pieces','unit','units'},
    'box': {'box','boxes','bx'},
    'pack': {'pack','packs','pkt','packet','packets'},
    'kg': {'kg','kilogram','kilograms'},
    'g': {'g','gram','grams'},
    'l': {'l','liter','liters'},
    'ml': {'ml','milliliter','milliliters'},
}

def canonical_unit(text):
    if not isinstance(text, str):
        return pd.NA
    t = text.strip().lower()
    for canon, aliases in UNIT_ALIASES.items():
        if t == canon or t in aliases:
            return canon
    # loose regex catch
    if re.search(r'\bpcs?\b', t): return 'pcs'
    if re.search(r'\bpieces?\b', t): return 'pcs'
    if re.search(r'\bboxes?\b', t): return 'box'
    if re.search(r'\bpacks?\b|\bpkt\b|\bpackets?\b', t): return 'pack'
    if re.search(r'\bkg\b|\bkilograms?\b', t): return 'kg'
    if re.search(r'\bgrams?\b|\bg\b', t): return 'g'
    if re.search(r'\bliters?\b|\bl\b', t): return 'l'
    if re.search(r'\bmilliliters?\b|\bml\b', t): return 'ml'
    return pd.NA

def normalize_units_on_df(df):
    """
    Fill/standardize Unit. If there's no usable Unit column (missing or all NA),
    infer from Description. Also default to 'pcs' when nothing obvious is found.
    """
    df = df.copy()

    # --- 1) find a usable unit source column ---
    unit_source_col = None
    for cand in ['Unit','Units','UOM','uom','unit','units']:
        if cand in df.columns:
            unit_source_col = cand
            break

    def col_is_empty(series):
        if series is None:
            return True
        s = series.astype(str).str.strip().replace({'': pd.NA, 'nan': pd.NA, 'None': pd.NA, 'NULL': pd.NA})
        return s.isna().all()

    need_infer = (unit_source_col is None) or col_is_empty(df[unit_source_col])

    # --- 2) infer from Description if needed ---
    if need_infer and 'Description' in df.columns:
        unit_source_col = 'Unit'  # write inference into 'Unit'
        # Expanded vocabulary: packaging + mass/volume + pharma forms + IU
        # Also matches "5pcs", "500ml", "10mg" (no space).
        pattern = r'''(?ix)
            (?<![A-Za-z])(
                pc|pcs|piece|pieces|unit|units|
                box|boxes|pack|packs|pkt|packet|packets|
                sachet|sachets|vial|vials|amp|ampule|ampoule|
                tube|tubes|bottle|bottles|bot|btl|
                jar|jars|can|cans|tin|tins|
                strip|blister|blisters|
                cap|caps|capsule|capsules|
                tab|tabs|tablet|tablets|
                roll|rolls|pair|pairs|set|sets|
                kg|g|mg|mcg|l|ml|iu
            )(?![A-Za-z])
        '''
        df[unit_source_col] = df['Description'].astype(str).str.extract(pattern)[0]

    # --- 3) if still nothing, bail gracefully ---
    if unit_source_col is None:
        return df, "No unit column found; skipped unit normalization."

    # --- 4) canonicalize tokens to a small set ---
    def canon(u):
        u = canonical_unit(u)  # will map pcs/box/pack/kg/g/l/ml
        if pd.isna(u) and isinstance(u, float):  # just in case
            return pd.NA
        if pd.isna(u):
            return pd.NA

        # extra mappings for pharma forms -> treat as piece-like
        tablety = {'tab','tabs','tablet','tablets'}
        capsuly  = {'cap','caps','capsule','capsules'}
        vials    = {'vial','vials','amp','ampule','ampoule'}
        sachets  = {'sachet','sachets'}
        bottles  = {'bottle','bottles','bot','btl'}
        tubes    = {'tube','tubes'}
        containers = {'jar','jars','can','cans','tin','tins'}
        misc_piece = {'strip','blister','blisters','roll','rolls','pair','pairs','set','sets'}
        dosage = {'mg','mcg','iu'}  # dosage units; treat as piece-like by default

        t = str(u).lower().strip()
        if t in tablety or t in capsuly or t in vials or t in sachets or t in bottles or t in tubes or t in containers or t in misc_piece or t in dosage:
            return 'pcs'
        return t

    df['Unit_std'] = df[unit_source_col].apply(canon)

    # --- 5) optional scaling for g->kg and ml->l only (leave mg/mcg alone) ---
    if 'Qty' in df.columns:
        q = pd.to_numeric(df['Qty'], errors='coerce')
        mask_g  = df['Unit_std'].eq('g')
        mask_ml = df['Unit_std'].eq('ml')
        if mask_g.any():
            df.loc[mask_g, 'Qty'] = q.where(~mask_g, q/1000.0)
            df.loc[mask_g, 'Unit_std'] = 'kg'
        if mask_ml.any():
            df.loc[mask_ml, 'Qty'] = q.where(~mask_ml, q/1000.0)
            df.loc[mask_ml, 'Unit_std'] = 'l'

    # --- 6) default any remaining NA to 'pcs' (typical POS) ---
    if 'Qty' in df.columns:
        mask_na = df['Unit_std'].isna() & pd.to_numeric(df['Qty'], errors='coerce').notna()
        df.loc[mask_na, 'Unit_std'] = 'pcs'
    else:
        df.loc[df['Unit_std'].isna(), 'Unit_std'] = 'pcs'

    df['Unit'] = df['Unit_std']
    df.drop(columns=['Unit_std'], inplace=True)
    return df, "Units normalized (including inference from Description; defaulted missing to 'pcs')."




def load_data_from_source(source):
    """
    Load CSV data from either a file path or URL.
    
    Args:
        source (str): Either a file path or URL to the CSV data
        
    Returns:
        str: CSV content as string
    """
    if source.startswith(('http://', 'https://')):
        print(f"Fetching data from URL: {source}")
        response = requests.get(source)
        response.raise_for_status()
        print("Data fetched successfully from URL!")
        return response.text
    else:
        print(f"Reading data from file: {source}")
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        
        with open(source, 'r', encoding='utf-8') as file:
            content = file.read()
        print("Data loaded successfully from file!")
        return content

def analyze_csv_structure(csv_content):
    """
    Analyze the CSV structure to find the actual data rows and headers.
    """
    lines = csv_content.strip().split('\n')
    print(f"Total lines in file: {len(lines)}")
    
    # Print first 15 lines to understand structure
    print("\nFirst 15 lines of the file:")
    for i, line in enumerate(lines[:15]):
        print(f"Line {i}: {repr(line)}")  # Use repr to see exact content
    
    data_start_row = 0
    header_found = False
    
    # Look for the first row that has multiple comma-separated values
    for i, line in enumerate(lines):
        if line.count(',') >= 3:  # At least 4 columns
            # Check if this looks like a header row
            if any(keyword in line.lower() for keyword in ['date', 'receipt', 'item', 'description', 'qty', 'sales', 'total', 'so', 'code']):
                data_start_row = i
                header_found = True
                print(f"Found header at line {i}: {line}")
                break
            # Or if it looks like data (contains numbers and commas)
            elif re.search(r'\d+[,.]?\d*', line) and ',' in line:
                data_start_row = i
                print(f"Found potential data start at line {i}: {line}")
                break
    
    if not header_found:
        print("No clear header found, looking for any data rows...")
        for i, line in enumerate(lines):
            if ',' in line and len(line.strip()) > 10:  # Has commas and substantial content
                data_start_row = i
                print(f"Using line {i} as data start: {line}")
                break
    
    return data_start_row

def fetch_and_clean_sales_data(source):
    """
    Load CSV data from file path or URL and clean it according to specified requirements.
    Returns (cleaned_df, errors_df).
    """
    csv_content = load_data_from_source(source)

    lines = csv_content.strip().split('\n')
    print(f"Total lines in file: {len(lines)}")
    print("First 10 lines (before skipping):")
    for i, line in enumerate(lines[:10]):
        print(f"Line {i}: {line}")

    # Skip first 5 rows as requested
    if len(lines) > 5:
        csv_from_row_6 = '\n'.join(lines[5:])
        print(f"\nSkipping first 5 rows. Processing from line 6 onwards...")
        remaining_lines = lines[5:]
        for i, line in enumerate(remaining_lines[:5]):
            print(f"Line {i+6}: {line}")
    else:
        print("Warning: File has 5 or fewer lines!")
        csv_from_row_6 = csv_content

    try:
        df_raw = pd.read_csv(StringIO(csv_from_row_6))
        print(f"Successfully read CSV with shape: {df_raw.shape}")
    except Exception as e:
        print(f"CSV read failed: {e}")
        try:
            df_raw = pd.read_csv(StringIO(csv_from_row_6), sep=None, engine='python')
            print(f"Successfully read CSV with auto-separator with shape: {df_raw.shape}")
        except Exception as e2:
            print(f"All CSV read attempts failed: {e2}")
            raise Exception("Could not parse CSV file")

    print("Raw DataFrame columns:", df_raw.columns.tolist())
    print(f"Raw DataFrame shape: {df_raw.shape}")
    print("\nFirst few rows of raw data:")
    print(df_raw.head())

    df_cleaned, errors_df = clean_dataframe_improved(df_raw)
    return df_cleaned, errors_df


def extract_expiration_date(description):
    """
    Extract expiration date from description text and return cleaned description.
    
    Args:
        description (str): Original description text
        
    Returns:
        tuple: (cleaned_description, expiration_date)
    """
    if pd.isna(description) or not isinstance(description, str):
        return description, pd.NA
    
    exp_patterns = [
        # Full date patterns
        r'exp(?:iry|iration)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'best\s+by[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'use\s+by[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'expires?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'bb[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*exp',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*$',  # Date at end of string
        
        # Short code patterns like #EXP20, EXP20, etc.
        r'#?exp\d{2,4}',  # Matches #EXP20, EXP20, EXP2024, etc.
        r'#?bb\d{2,4}',   # Matches #BB20, BB20, etc.
        r'#?use\d{2,4}',  # Matches #USE20, USE20, etc.
        r'exp[:\s]*\d{2,4}',  # Matches EXP: 20, EXP 20, etc.
        r'bb[:\s]*\d{2,4}',   # Matches BB: 20, BB 20, etc.
        
        # Month/year patterns
        r'exp[:\s]*(\d{1,2}[/-]\d{2,4})',  # EXP: 12/24
        r'bb[:\s]*(\d{1,2}[/-]\d{2,4})',   # BB: 12/24
        
        # Standalone expiration indicators
        r'#?exp[:\s]*$',  # Just "EXP" or "#EXP" at end
        r'#?bb[:\s]*$',   # Just "BB" or "#BB" at end
    ]
    
    cleanup_patterns = [
        r'#exp\w*',      # Remove #EXP followed by any word characters
        r'exp\d+',       # Remove EXP followed by digits
        r'bb\d+',        # Remove BB followed by digits
        r'#bb\w*',       # Remove #BB followed by any word characters
        r'exp[:\s]*$',   # Remove trailing EXP
        r'bb[:\s]*$',    # Remove trailing BB
        r'#\s*$',        # Remove trailing #
        r'\s+#\s*',      # Remove # with spaces
    ]
    
    expiration_date = pd.NA
    cleaned_desc = description
    
    # First pass: extract actual dates
    for pattern in exp_patterns[:7]:  # Only the date patterns
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            try:
                date_str = match.group(1)
                # Try to parse the date
                parsed_date = pd.to_datetime(date_str, errors='coerce')
                if pd.notna(parsed_date):
                    expiration_date = parsed_date
                    # Remove the expiration date part from description
                    cleaned_desc = re.sub(pattern, '', cleaned_desc, flags=re.IGNORECASE).strip()
                    break
            except:
                continue
    
    # Second pass: remove all expiration-related patterns (including codes like #EXP20)
    for pattern in exp_patterns:
        cleaned_desc = re.sub(pattern, '', cleaned_desc, flags=re.IGNORECASE).strip()
    
    # Third pass: additional cleanup for any remaining fragments
    for pattern in cleanup_patterns:
        cleaned_desc = re.sub(pattern, '', cleaned_desc, flags=re.IGNORECASE).strip()
    
    # Remove multiple spaces and normalize
    cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc)
    # Remove leading/trailing punctuation and spaces
    cleaned_desc = cleaned_desc.strip(' ,-#:')
    # Remove empty parentheses or brackets that might be left behind
    cleaned_desc = re.sub(r'\(\s*\)', '', cleaned_desc)  # remove empty ()
    cleaned_desc = re.sub(r'\[\s*\]', '', cleaned_desc)  # remove empty []
    # Remove double spaces again after cleanup
    cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc).strip()
    
    # If description becomes empty or too short, keep original but still extract date
    if not cleaned_desc or len(cleaned_desc.strip()) < 2:
        cleaned_desc = description
    
    return cleaned_desc, expiration_date




def project_to_target(df_in, column_mapping, target_columns):
    """
    Map an arbitrary df (using raw/source columns) into the target schema
    using the same column_mapping used for the main dataset.
    Keeps a _row_id if present.
    """
    out = pd.DataFrame()
    for t in target_columns:
        src = column_mapping.get(t)
        if src is not None and src in df_in.columns:
            out[t] = df_in[src]
        else:
            out[t] = pd.NA
    if '_row_id' in df_in.columns:
        out['_row_id'] = df_in['_row_id']
    return out


def remove_incomplete_rows(df):
    """
    Remove rows with missing critical supporting data.
    Focus on rows where financial data exists but supporting data is missing.
    Also returns a dataframe of removed rows with reasons.
    """
    print("\nREMOVING INCOMPLETE ROWS:")
    print("-" * 30)

    df_clean = df.copy()
    errors = []

    initial_count = len(df_clean)

    # Define critical supporting columns that should have data
    supporting_columns = ['Item Code', 'Description']
    financial_columns = ['Sales', 'Cost', 'Profit']

    # Find rows where financial data exists but supporting data is missing
    rows_to_remove = []
    for idx in df_clean.index:
        has_financial_data = any(
            (col in df_clean.columns) and pd.notna(df_clean.loc[idx, col]) and df_clean.loc[idx, col] != 0
            for col in financial_columns
        )
        if has_financial_data:
            missing_supporting = []
            for col in supporting_columns:
                if col in df_clean.columns:
                    value = df_clean.loc[idx, col]
                    if pd.isna(value) or str(value).strip().lower() in ('', 'nan', 'none', 'null'):
                        missing_supporting.append(col)
            if missing_supporting:
                rows_to_remove.append(idx)

    if rows_to_remove:
        removed = df_clean.loc[rows_to_remove].copy()
        removed['error_reason'] = 'financial data present but missing supporting fields'
        removed['error_stage']  = 'remove_incomplete_rows'
        errors.append(removed)
        df_clean = df_clean.drop(rows_to_remove)
        print(f"✓ Removed {len(rows_to_remove)} incomplete rows")
        print(f"  Remaining rows: {len(df_clean)}")
    else:
        print("✓ No incomplete rows found - all data appears complete")

    # Additional check: Remove rows where ALL important columns are empty
    important_columns = ['Item Code', 'Description', 'Qty', 'Sales', 'Cost']
    available_important = [c for c in important_columns if c in df_clean.columns]
    if available_important:
        empty_mask = df_clean[available_important].isna().all(axis=1)
        if empty_mask.any():
            removed2 = df_clean.loc[empty_mask].copy()
            removed2['error_reason'] = 'all important fields empty'
            removed2['error_stage']  = 'remove_incomplete_rows'
            errors.append(removed2)
            df_clean = df_clean.loc[~empty_mask]
            print(f"✓ Removed {int(empty_mask.sum())} completely empty data rows")

    final_count = len(df_clean)
    print(f"\nData validation summary:")
    print(f"  Initial rows: {initial_count}")
    print(f"  Removed rows: {initial_count - final_count}")
    print(f"  Final rows: {final_count}")

    errors_df = pd.concat(errors, ignore_index=True) if errors else pd.DataFrame(columns=list(df.columns) + ['error_reason','error_stage'])
    return df_clean, errors_df


def clean_dataframe_improved(df):
    """
    Clean & standardize dataframe. Tracks and returns all removed rows with reasons.
    """
    print("\n" + "="*50)
    print("CLEANING DATAFRAME")
    print("="*50)

    # Keep a stable row id to trace rows that get removed later
    df_clean = df.copy()
    df_clean['_row_id'] = df_clean.index

    print(f"Starting with {len(df_clean)} rows and {len(df_clean.columns)} columns")
    print("Original columns:", df_clean.columns.tolist())
    print("\nSample of raw data (first 5 rows):")
    print(df_clean.head().to_string())

    # -------- capture removals BEFORE mapping --------
    errors_pre = []

    # 1) Remove summary/total rows
    total_patterns = ['grand total', 'total:', 'subtotal']
    rows_before = len(df_clean)
    for pattern in total_patterns:
        mask = df_clean.astype(str).apply(lambda x: x.str.contains(pattern, case=False, na=False, regex=False)).any(axis=1)
        if mask.any():
            removed = df_clean.loc[mask].copy()
            removed['error_reason'] = f"summary/total row matched '{pattern}'"
            removed['error_stage']  = 'pre-map'
            errors_pre.append(removed)
            df_clean = df_clean.loc[~mask]
    print(f"Removed {rows_before - len(df_clean)} total/summary rows")

    # 2) Remove completely empty rows
    empty_mask_all = df_clean.isna().all(axis=1)
    if empty_mask_all.any():
        removed = df_clean.loc[empty_mask_all].copy()
        removed['error_reason'] = 'completely empty row'
        removed['error_stage']  = 'pre-map'
        errors_pre.append(removed)
        df_clean = df_clean.loc[~empty_mask_all]
    print(f"After removing completely empty rows: {len(df_clean)} rows")

    if len(df_clean) == 0:
        print("WARNING: No data remaining after cleaning!")
        return pd.DataFrame(), pd.DataFrame()

    print(f"\nData after initial cleaning ({len(df_clean)} rows):")
    print(df_clean.head().to_string())

    # -------- mapping into target schema --------
    target_columns = [
        'Date', 'Receipt', 'SO', 'Item Code', 'Description', 'Expiration Date',
        'Qty', 'Unit', 'Discount', 'Sales', 'Cost', 'Profit', 'Payment', 'Cashier ID'
    ]
    column_mapping = map_columns_improved(df_clean, target_columns)

    # Build df_final (in target schema)
    df_final = pd.DataFrame()
    for target_col in target_columns:
        if target_col in column_mapping:
            source_col = column_mapping[target_col]
            df_final[target_col] = df_clean[source_col].copy()
            print(f"✓ Mapped '{source_col}' -> '{target_col}' ({df_clean[source_col].notna().sum()} values)")
        else:
            df_final[target_col] = pd.NA
            print(f"⚠ Created empty column for '{target_col}' (no source found)")
    # carry row id for later error tracking
    df_final['_row_id'] = df_clean['_row_id'].copy()

    # Project early removals into target schema so the error file is consistent
    errors_aligned = []
    for e in errors_pre:
        aligned = project_to_target(e, column_mapping, target_columns)
        aligned['_row_id']     = e['_row_id'].values
        aligned['error_reason'] = e['error_reason'].values
        aligned['error_stage']  = e['error_stage'].values
        errors_aligned.append(aligned)

    # -------- extract expiration dates from descriptions --------
    if 'Description' in df_final.columns:
        print("\nExtracting expiration dates from descriptions...")
        descriptions_with_dates = 0
        for idx in df_final.index:
            original_desc = df_final.loc[idx, 'Description']
            cleaned_desc, exp_date = extract_expiration_date(original_desc)
            df_final.loc[idx, 'Description'] = cleaned_desc
            if pd.notna(exp_date):
                df_final.loc[idx, 'Expiration Date'] = exp_date
                descriptions_with_dates += 1
        print(f"✓ Extracted expiration dates from {descriptions_with_dates} descriptions")

    # -------- unit normalization --------
    df_final, unit_msg = normalize_units_on_df(df_final)
    print(f"✓ {unit_msg}")

    # -------- type cleaning --------
    df_final = clean_data_types_improved(df_final)

    # -------- remove incomplete rows (and collect errors) --------
    df_final, errs_incomplete = remove_incomplete_rows(df_final)

    # -------- drop duplicates (and collect) --------
    errors_post = []
    dupe_subset = [c for c in ['Date','Receipt','SO','Item Code','Qty','Sales','Cost'] if c in df_final.columns]
    before = len(df_final)
    if dupe_subset:
        dup_mask = df_final.duplicated(subset=dupe_subset, keep='first')
    else:
        dup_mask = df_final.duplicated(keep='first')
    if dup_mask.any():
        removed_dup = df_final.loc[dup_mask].copy()
        removed_dup['error_reason'] = 'duplicate row'
        removed_dup['error_stage']  = 'duplicates'
        errors_post.append(removed_dup)
        df_final = df_final.loc[~dup_mask]
    print(f"✓ Removed {before - len(df_final)} duplicate rows")

    # (Optional) remove rows effectively empty across important fields (after type clean)
    important = [c for c in ['Item Code','Description','Qty','Sales','Cost'] if c in df_final.columns]
    if important:
        mask_all_null = df_final[important].isna().all(axis=1)
        if mask_all_null.any():
            removed_empty = df_final.loc[mask_all_null].copy()
            removed_empty['error_reason'] = 'all important fields empty (post-map)'
            removed_empty['error_stage']  = 'post-map'
            errors_post.append(removed_empty)
            df_final = df_final.loc[~mask_all_null]
            print(f"✓ Removed {int(mask_all_null.sum())} rows with all key fields null")

    # -------- assemble all errors --------
    errors_all = []
    if errors_aligned:
        errors_all.append(pd.concat(errors_aligned, ignore_index=True))
    if not errs_incomplete.empty:
        errors_all.append(errs_incomplete)
    if errors_post:
        errors_all.append(pd.concat(errors_post, ignore_index=True))
    errors_all = pd.concat(errors_all, ignore_index=True) if errors_all else pd.DataFrame(columns=target_columns + ['_row_id','error_reason','error_stage'])

    # -------- final summary --------
    print(f"\n✅ Final cleaned DataFrame: {df_final.shape[0]} rows x {df_final.shape[1]} columns")
    if not df_final.empty:
        print("\nSample of final cleaned data:")
        print(df_final.head().to_string())

    # Drop helper id from the cleaned output (keep it in errors)
    if '_row_id' in df_final.columns:
        df_final = df_final.drop(columns=['_row_id'])

    return df_final, errors_all

    

    # --- Unit normalization (also infers Unit from Description if missing) ---
    # --- Unit normalization (also infers Unit from Description if missing) ---
    df_final, unit_msg = normalize_units_on_df(df_final)
    print(f"✓ {unit_msg}")

    # --- Coerce types ---
    df_final = clean_data_types_improved(df_final)

    # --- Remove rows missing critical supporting data ---
    df_final = remove_incomplete_rows(df_final)

    # --- Remove duplicates on key business fields ---
    dupe_subset = [c for c in ['Date','Receipt','SO','Item Code','Qty','Sales','Cost'] if c in df_final.columns]
    before = len(df_final)
    if dupe_subset:
        df_final = df_final.drop_duplicates(subset=dupe_subset, keep='first')
    else:
        df_final = df_final.drop_duplicates(keep='first')
    print(f"✓ Removed {before - len(df_final)} duplicate rows")

    # --- Remove rows effectively empty across important fields ---
    important = [c for c in ['Item Code','Description','Qty','Sales','Cost'] if c in df_final.columns]
    if important:
        mask_all_null = df_final[important].isna().all(axis=1)
        removed = int(mask_all_null.sum())
        if removed:
            df_final = df_final.loc[~mask_all_null].copy()
            print(f"✓ Removed {removed} rows with all key fields null")

    # ----- Final summary -----
    print(f"\n✅ Final cleaned DataFrame: {df_final.shape[0]} rows x {df_final.shape[1]} columns")
    if not df_final.empty:
        print("\nSample of final cleaned data:")
        print(df_final.head().to_string())

    return df_final



def map_columns_improved(df, target_columns):
    """
    Improved column mapping with better pattern matching and fuzzy logic.
    """
    print("\nMAPPING COLUMNS:")
    print("-" * 30)
    
    column_mapping = {}
    available_cols = df.columns.tolist()
    
    mapping_patterns = {
        'Date': ['date','time','datetime','day','created','timestamp','when','dt'],
        'Receipt': ['receipt','rcpt','ticket','trans','transaction','ref','reference','no'],
        'SO': ['so','sales order','order','order no','order number','sales_order','ord'],
        'Item Code': ['item','code','sku','product code','prod code','barcode','item_code','product_code','plu'],
        'Description': ['description','desc','product','item name','name','title','product_name','item_name'],
        'Expiration Date': ['exp','expiry','expiration','best by','use by','expires','bb'],
        'Qty': ['qty','quantity','amount','count','qnty','qnt'],
        'Unit': ['unit','units','uom','pack','packet','packets','box','boxes','pcs','pc','piece','pieces','kg','g','l','ml'],
        'Discount': ['discount','disc','off','reduction','rebate','promo'],
        'Sales': ['sales','total','amount','price','value','revenue','sale','net','gross'],
        'Cost': ['cost','cogs','unit cost','purchase','buy','wholesale'],
        'Profit': ['profit','margin','gain','net profit','gp'],
        'Payment': ['payment','pay','method','type','pay_method','tender'],
        'Cashier ID': ['cashier','user','employee','staff','operator','clerk','cashier_id','user_id','emp'],
    }
    
    print("Available columns:", available_cols)
    print()
    
    for target_col, patterns in mapping_patterns.items():
        best_match = None
        best_score = 0
        
        for col in available_cols:
            if col in column_mapping.values():  # Skip already mapped columns
                continue
                
            col_lower = str(col).lower().strip()
            score = 0
            
            # Exact match gets highest score
            if col_lower in [p.lower() for p in patterns]:
                score = 100
            else:
                # Partial match scoring
                for pattern in patterns:
                    pattern_lower = pattern.lower()
                    if pattern_lower in col_lower:
                        score = max(score, 80)
                    elif col_lower in pattern_lower:
                        score = max(score, 70)
                    elif any(word in col_lower for word in pattern_lower.split()):
                        score = max(score, 50)
                    elif any(word in pattern_lower for word in col_lower.split('_')):
                        score = max(score, 30)
            
            if score > best_score:
                best_score = score
                best_match = col
        
        if best_match and best_score >= 20:
            column_mapping[target_col] = best_match
            print(f"  {target_col} <- '{best_match}' (confidence: {best_score}%)")
        else:
            print(f"  {target_col} <- NO MATCH FOUND (best was '{best_match}' with {best_score}%)")
    
    return column_mapping

def clean_data_types_improved(df):
    """
    Improved data type cleaning with better error handling.
    """
    print("\nCLEANING DATA TYPES:")
    print("-" * 30)

    df_clean = df.copy()

    # Numeric columns: DO NOT include 'Unit' here
    numeric_cols = ['Qty', 'Discount', 'Sales', 'Cost', 'Profit']
    for col in numeric_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()

            df_clean[col] = df_clean[col].astype(str)
            # Remove currency symbols, commas, and other non-numeric chars (keep . and -)
            df_clean[col] = df_clean[col].str.replace(r'[^\d.-]', '', regex=True)
            # Replace empty strings and 'nan' with NaN
            df_clean[col] = df_clean[col].replace(['', 'nan', 'none'], pd.NA)
            # Convert to numeric
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    # Dates
    date_cols = ['Date', 'Expiration Date']
    for col in date_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce', infer_datetime_format=True)
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid dates")

    # Text columns (now includes Unit)
    string_cols = ['Receipt', 'SO', 'Item Code', 'Description', 'Payment', 'Cashier ID', 'Unit']
    for col in string_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].replace(['nan', 'none', 'null', '', 'NaN'], pd.NA)
            # Optional: force lowercase for consistency (Unit already canonicalized earlier)
            if col == 'Unit':
                df_clean[col] = df_clean[col].str.lower()
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    return df_clean

def save_error_report(errors_df, filename='cleaning_errors.xlsx'):
    """
    Save removed rows (with reasons) to an Excel workbook (.xlsx).
    If Excel engine isn't available, or if filename ends with .csv, write CSV instead.
    """
    if errors_df is None or errors_df.empty:
        print("\nNo removed rows to save. Skipping errors file.")
        return None

    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        errors_df.to_csv(filename, index=False)
        print(f"\nErrors CSV saved to '{filename}' ({len(errors_df)} rows).")
        return filename

    try:
        # Requires 'openpyxl' installed
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            errors_df.to_excel(writer, index=False, sheet_name='removed_rows')
        print(f"\nErrors workbook saved to '{filename}' ({len(errors_df)} rows).")
        return filename
    except Exception as e:
        print(f"Could not write Excel file ({e}). Saving CSV fallback.")
        fallback = os.path.splitext(filename)[0] + '.csv'
        errors_df.to_csv(fallback, index=False)
        print(f"Errors CSV saved to '{fallback}' ({len(errors_df)} rows).")
        return fallback


def save_cleaned_data(df, filename='cleaned_sales_data.csv'):
    """
    Save the cleaned dataframe to CSV.
    """
    df.to_csv(filename, index=False)
    print(f"\nCleaned data saved to '{filename}'")
    print(f"Final dataset contains {len(df)} records")

    # Display summary
    print("\nData Summary:")
    print("=" * 50)
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        print(f"{col}: {non_null_count} non-null values")

    print("\nFirst 5 rows of cleaned data:")
    print(df.head())

    return filename


def browse_for_file():
    """
    Open a file dialog to browse and select a CSV file.
    """
    try:
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring dialog to front
        
        print("Opening file browser...")
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select CSV Data File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        # Clean up the root window
        root.destroy()
        
        if file_path:
            print(f"Selected file: {file_path}")
            return file_path
        else:
            print("No file selected.")
            return None
            
    except Exception as e:
        print(f"Error opening file browser: {e}")
        print("File browser not available. Please enter file path manually.")
        return None

def get_data_source():
    """
    Get data source from user input (file path, URL, or file browser).
    """
    print("Data Cleaning Program")
    print("=" * 50)
    print("You can import data from:")
    print("1. Browse for local CSV file")
    print("2. Enter file path manually")
    print("3. Enter URL to CSV file")
    print()
    
    while True:
        choice = input("Choose option (1/2/3) or press Enter to browse: ").strip()
        
        if not choice or choice == '1':
            source = browse_for_file()
            if source:
                return source
            else:
                retry = input("Would you like to try a different method? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
        
        elif choice == '2':
            # Manual file path entry
            source = input("Enter file path: ").strip()
            if not source:
                print("Please enter a valid file path.")
                continue
            if os.path.exists(source):
                print(f"File found: {source}")
                return source
            else:
                print(f"File not found: {source}")
                continue
        
        elif choice == '3':
            # URL entry
            source = input("Enter URL: ").strip()
            if not source:
                print("Please enter a valid URL.")
                continue
            if source.startswith(('http://', 'https://')):
                print(f"URL detected: {source}")
                return source
            else:
                print("Please enter a valid URL starting with http:// or https://")
                continue
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
            continue

# Main execution
if __name__ == "__main__":
    # Default URL for testing
    default_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/testdata-D3IKHaVvsV4pdgUGLj27PXAagiN6WO.csv"
    
    try:
        # Check if source is provided as command line argument
        if len(sys.argv) > 1:
            data_source = sys.argv[1]
            print(f"Using data source from command line: {data_source}")
        else:
            # Interactive mode - ask user for input
            data_source = get_data_source()
            
            if not data_source:
                print("No data source provided. Using default test data...")
                data_source = default_url
        
        # Fetch and clean the data
        
        cleaned_df, errors_df = fetch_and_clean_sales_data(data_source)
        
        # Generate output filename based on input
        if data_source.startswith(('http://', 'https://')):
            output_file = 'cleaned_sales_data_from_url.csv'
        else:
            base_name = os.path.splitext(os.path.basename(data_source))[0]
            output_file = f'cleaned_{base_name}.csv'
        
        # Save the cleaned data
        save_cleaned_data(cleaned_df, output_file)
        
        errors_file = os.path.splitext(output_file)[0] + '_errors.xlsx'      
        save_error_report(errors_df, errors_file)
 
        
        print(f"\n✅ Data cleaning completed successfully!")
        print(f"📁 Output file: {output_file}")
        
        view_sample = input("\nWould you like to view a sample of the cleaned data? (y/n): ").strip().lower()
        if view_sample == 'y':
            print("\nSample of cleaned data:")
            print("=" * 80)
            print(cleaned_df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
