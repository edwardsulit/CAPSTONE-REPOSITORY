
import pandas as pd
import requests
from io import StringIO
import re
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

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
    if re.search(r'\\bpcs?\\b', t): return 'pcs'
    if re.search(r'\\bpieces?\\b', t): return 'pcs'
    if re.search(r'\\bboxes?\\b', t): return 'box'
    if re.search(r'\\bpacks?\\b|\\bpkt\\b|\\bpackets?\\b', t): return 'pack'
    if re.search(r'\\bkg\\b|\\bkilograms?\\b', t): return 'kg'
    if re.search(r'\\bgrams?\\b|\\bg\\b', t): return 'g'
    if re.search(r'\\bliters?\\b|\\bl\\b', t): return 'l'
    if re.search(r'\\bmilliliters?\\b|\\bml\\b', t): return 'ml'
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
        # Expanded vocabulary
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
        dosage = {'mg','mcg','iu'}

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

    # --- 6) default any remaining NA to 'pcs' ---
    if 'Qty' in df.columns:
        mask_na = df['Unit_std'].isna() & pd.to_numeric(df['Qty'], errors='coerce').notna()
        df.loc[mask_na, 'Unit_std'] = 'pcs'
    else:
        df.loc[df['Unit_std'].isna(), 'Unit_std'] = 'pcs'

    df['Unit'] = df['Unit_std']
    df.drop(columns=['Unit_std'], inplace=True)
    return df, "Units normalized (including inference from Description; defaulted missing to 'pcs')."


def load_data_from_source(source):
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
    lines = csv_content.strip().split('\n')
    data_start_row = 0
    header_found = False
    for i, line in enumerate(lines):
        if line.count(',') >= 3:
            if any(keyword in line.lower() for keyword in ['date', 'receipt', 'item', 'description', 'qty', 'sales', 'total', 'so', 'code']):
                data_start_row = i
                header_found = True
                break
            elif re.search(r'\d+[,.]?\d*', line) and ',' in line:
                data_start_row = i
                break
    if not header_found:
        for i, line in enumerate(lines):
            if ',' in line and len(line.strip()) > 10:
                data_start_row = i
                break
    return data_start_row

def fetch_and_clean_sales_data(source):
    csv_content = load_data_from_source(source)
    lines = csv_content.strip().split('\n')

    # Skip first 5 rows as requested
    if len(lines) > 5:
        csv_from_row_6 = '\n'.join(lines[5:])
    else:
        csv_from_row_6 = csv_content

    try:
        df_raw = pd.read_csv(StringIO(csv_from_row_6))
    except Exception:
        df_raw = pd.read_csv(StringIO(csv_from_row_6), sep=None, engine='python')

    df_cleaned, errors_df = clean_dataframe_improved(df_raw)
    return df_cleaned, errors_df

# ---- Expiration helpers ----
def _normalize_exp_str(date_str):
    """Return YYYY-MM-DD if valid and in sane range (2020-2045), else ''."""
    if not isinstance(date_str, str):
        date_str = str(date_str) if pd.notna(date_str) else ''
    date_str = date_str.strip()
    if not date_str:
        return ''
    # try explicit formats
    fmts = ['%Y-%m-%d','%m/%d/%Y','%m-%d-%Y','%m/%d/%y','%m-%d-%y']
    dt = None
    for f in fmts:
        try:
            dt = datetime.strptime(date_str, f)
            break
        except Exception:
            continue
    if dt is None:
        # last resort pandas
        try:
            dt = pd.to_datetime(date_str, errors='coerce')
        except Exception:
            dt = None
        if pd.isna(dt):
            dt = None
    if dt is None:
        return ''
    if not (2020 <= int(dt.year) <= 2045):
        return ''
    return dt.strftime('%Y-%m-%d')

def extract_expiration_from_description(description):
    """
    Parse expiration strictly from description; return (cleaned_description, exp_str_or_blank).
    Never fabricate.
    """
    if pd.isna(description) or not isinstance(description, str) or not description.strip():
        return description, ""

    text = description
    patterns = [
        r'[#\(\s]?EXP\s*(\d{4}-\d{2}-\d{2})\)?',
        r'[#\(\s]?exp\s*(\d{4}-\d{2}-\d{2})\)?',
        r'(?:exp(?:iry|iration)?|best\s*by|use\s*by|expires?|bb)[:\s\-]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:exp|bb)\b',
        r'\b(\d{4}-\d{2}-\d{2})\b'
    ]

    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if not m:
            continue
        norm = _normalize_exp_str(m.group(1))
        if norm:
            cleaned = re.sub(pat, '', text, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip(' ,-#:()')
            return cleaned or description, norm

    # no valid date found
    cleaned = re.sub(r'\s{2,}', ' ', text).strip(' ,-#:()')
    return cleaned or description, ""

def project_to_target(df_in, column_mapping, target_columns):
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
    df_clean = df.copy()
    errors = []
    initial_count = len(df_clean)
    supporting_columns = ['Item Code', 'Description']
    financial_columns = ['Sales', 'Cost', 'Profit']
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
    errors_df = pd.concat(errors, ignore_index=True) if errors else pd.DataFrame(columns=list(df.columns) + ['error_reason','error_stage'])
    return df_clean, errors_df

def clean_dataframe_improved(df):
    df_clean = df.copy()
    df_clean['_row_id'] = df_clean.index

    errors_pre = []
    total_patterns = ['grand total', 'total:', 'subtotal']
    for pattern in total_patterns:
        mask = df_clean.astype(str).apply(lambda x: x.str.contains(pattern, case=False, na=False, regex=False)).any(axis=1)
        if mask.any():
            removed = df_clean.loc[mask].copy()
            removed['error_reason'] = f"summary/total row matched '{pattern}'"
            removed['error_stage']  = 'pre-map'
            errors_pre.append(removed)
            df_clean = df_clean.loc[~mask]
    empty_mask_all = df_clean.isna().all(axis=1)
    if empty_mask_all.any():
        removed = df_clean.loc[empty_mask_all].copy()
        removed['error_reason'] = 'completely empty row'
        removed['error_stage']  = 'pre-map'
        errors_pre.append(removed)
        df_clean = df_clean.loc[~empty_mask_all]
    if len(df_clean) == 0:
        return pd.DataFrame(), pd.DataFrame()

    target_columns = [
        'Date', 'Receipt', 'SO', 'Item Code', 'Description', 'Expiration Date',
        'Qty', 'Unit', 'Discount', 'Sales', 'Cost', 'Profit', 'Payment', 'Cashier ID'
    ]
    column_mapping = map_columns_improved(df_clean, target_columns)

    df_final = pd.DataFrame()
    for target_col in target_columns:
        if target_col in column_mapping:
            source_col = column_mapping[target_col]
            df_final[target_col] = df_clean[source_col].copy()
        else:
            df_final[target_col] = pd.NA
    df_final['_row_id'] = df_clean['_row_id'].copy()

    # Align removed rows
    errors_aligned = []
    for e in errors_pre:
        aligned = project_to_target(e, column_mapping, target_columns)
        aligned['_row_id']     = e['_row_id'].values
        aligned['error_reason'] = e['error_reason'].values
        aligned['error_stage']  = e['error_stage'].values
        errors_aligned.append(aligned)

    # --- Expiration extraction (STRICT + non-destructive) ---
    # 1) Normalize any pre-existing Expiration Date from the source
    if 'Expiration Date' in df_final.columns:
        df_final['Expiration Date'] = df_final['Expiration Date'].apply(_normalize_exp_str)

    # 2) Extract from Description ONLY to fill blanks
    if 'Description' in df_final.columns:
        filled_from_desc = 0
        for idx in df_final.index:
            original_desc = df_final.at[idx, 'Description']
            cleaned_desc, exp_from_desc = extract_expiration_from_description(original_desc)
            df_final.at[idx, 'Description'] = cleaned_desc
            if (not df_final.at[idx, 'Expiration Date']) and exp_from_desc:
                df_final.at[idx, 'Expiration Date'] = exp_from_desc
                filled_from_desc += 1
        print(f"✓ Filled {filled_from_desc} missing expirations from Description; others left blank")

    # --- Units ---
    df_final, unit_msg = normalize_units_on_df(df_final)
    print(f"✓ {unit_msg}")

    # --- Type cleaning ---
    df_final = clean_data_types_improved(df_final)

    # --- Incomplete rows removal ---
    df_final, errs_incomplete = remove_incomplete_rows(df_final)

    # --- Duplicates ---
    errors_post = []
    dupe_subset = [c for c in ['Date','Receipt','SO','Item Code','Qty','Sales','Cost'] if c in df_final.columns]
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

    # --- Remove rows empty across key fields ---
    important = [c for c in ['Item Code','Description','Qty','Sales','Cost'] if c in df_final.columns]
    if important:
        mask_all_null = df_final[important].isna().all(axis=1)
        if mask_all_null.any():
            removed_empty = df_final.loc[mask_all_null].copy()
            removed_empty['error_reason'] = 'all important fields empty (post-map)'
            removed_empty['error_stage']  = 'post-map'
            errors_post.append(removed_empty)
            df_final = df_final.loc[~mask_all_null]

    # --- Assemble errors ---
    errors_all = []
    if errors_aligned:
        errors_all.append(pd.concat(errors_aligned, ignore_index=True))
    if not errs_incomplete.empty:
        errors_all.append(errs_incomplete)
    if errors_post:
        errors_all.append(pd.concat(errors_post, ignore_index=True))
    errors_all = pd.concat(errors_all, ignore_index=True) if errors_all else pd.DataFrame(columns=target_columns + ['_row_id','error_reason','error_stage'])

    # Final normalization: ensure Expiration Date is string YYYY-MM-DD or blank
    if 'Expiration Date' in df_final.columns:
        df_final['Expiration Date'] = df_final['Expiration Date'].apply(lambda x: _normalize_exp_str(x))

    if '_row_id' in df_final.columns:
        df_final = df_final.drop(columns=['_row_id'])

    print(f"✅ Final cleaned DataFrame: {df_final.shape[0]} rows x {df_final.shape[1]} columns")
    return df_final, errors_all

def map_columns_improved(df, target_columns):
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
    for target_col, patterns in mapping_patterns.items():
        best_match = None
        best_score = 0
        for col in available_cols:
            if col in column_mapping.values():
                continue
            col_lower = str(col).lower().strip()
            score = 0
            if col_lower in [p.lower() for p in patterns]:
                score = 100
            else:
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
    return column_mapping

def clean_data_types_improved(df):
    df_clean = df.copy()
    numeric_cols = ['Qty', 'Discount', 'Sales', 'Cost', 'Profit']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
            df_clean[col] = df_clean[col].str.replace(r'[^\d.-]', '', regex=True)
            df_clean[col] = df_clean[col].replace(['', 'nan', 'none'], pd.NA)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Expiration Date: keep blanks as blanks; valid dates -> YYYY-MM-DD strings
    if 'Expiration Date' in df_clean.columns:
        df_clean['Expiration Date'] = df_clean['Expiration Date'].apply(lambda x: _normalize_exp_str(x))

    # Date: standard to datetime (ok if NaT)
    if 'Date' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')

    # Text columns
    string_cols = ['Receipt', 'SO', 'Item Code', 'Description', 'Payment', 'Cashier ID', 'Unit']
    for col in string_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].replace(['nan', 'none', 'null', '', 'NaN'], pd.NA)
            if col == 'Unit':
                df_clean[col] = df_clean[col].str.lower()
    return df_clean

def save_error_report(errors_df, filename='cleaning_errors.xlsx'):
    if errors_df is None or errors_df.empty:
        print('\nNo removed rows to save. Skipping errors file.')
        return None
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        errors_df.to_csv(filename, index=False)
        print(f"\nErrors CSV saved to '{filename}' ({len(errors_df)} rows).")
        return filename
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            errors_df.to_excel(writer, index=False, sheet_name='removed_rows')
        print(f"\nErrors workbook saved to '{filename}' ({len(errors_df)} rows)." )
        return filename
    except Exception as e:
        print(f"Could not write Excel file ({e}). Saving CSV fallback.")
        fallback = os.path.splitext(filename)[0] + '.csv'
        errors_df.to_csv(fallback, index=False)
        print(f"Errors CSV saved to '{fallback}' ({len(errors_df)} rows)." )
        return fallback

def save_cleaned_data(df, filename='cleaned_sales_data.csv'):
    df_out = df.copy()
    # ensure expiration is string for CSV
    if 'Expiration Date' in df_out.columns:
        df_out['Expiration Date'] = df_out['Expiration Date'].astype(str).replace({'NaT':'', 'nan':''})
    df_out.to_csv(filename, index=False)
    print(f"\nCleaned data saved to '{filename}'")
    print(f"Final dataset contains {len(df_out)} records")
    return filename

def browse_for_file():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            title="Select CSV Data File",
            filetypes=[("CSV files", "*.csv"),("All files", "*.*")],
            initialdir=os.getcwd()
        )
        root.destroy()
        return file_path if file_path else None
    except Exception:
        return None

def get_data_source():
    print("Data Cleaning Program")
    print("=" * 50)
    print("1. Browse for local CSV file")
    print("2. Enter file path manually")
    print("3. Enter URL to CSV file")
    while True:
        choice = input("Choose option (1/2/3) or press Enter to browse: ").strip()
        if not choice or choice == '1':
            source = browse_for_file()
            if source:
                return source
            retry = input("Would you like to try a different method? (y/n): ").strip().lower()
            if retry != 'y':
                return None
        elif choice == '2':
            source = input("Enter file path: ").strip()
            if source and os.path.exists(source):
                return source
            print("File not found.")
        elif choice == '3':
            source = input("Enter URL: ").strip()
            if source.startswith(('http://', 'https://')):
                return source
            print("Please enter a valid URL.")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

# Main execution
if __name__ == "__main__":
    default_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/testdata-D3IKHaVvsV4pdgUGLj27PXAagiN6WO.csv"
    try:
        if len(sys.argv) > 1:
            data_source = sys.argv[1]
            print(f"Using data source from command line: {data_source}")
        else:
            data_source = get_data_source()
            if not data_source:
                print("No data source provided. Using default test data...")
                data_source = default_url
        cleaned_df, errors_df = fetch_and_clean_sales_data(data_source)
        if data_source.startswith(('http://', 'https://')):
            output_file = 'cleaned_sales_data_from_url.csv'
        else:
            base_name = os.path.splitext(os.path.basename(data_source))[0]
            output_file = f'cleaned_{base_name}.csv'
        save_cleaned_data(cleaned_df, output_file)
        errors_file = os.path.splitext(output_file)[0] + '_errors.xlsx'
        save_error_report(errors_df, errors_file)
        print(f"\n✅ Data cleaning completed successfully!")
        print(f"📁 Output file: {output_file}")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
