
import pandas as pd
import requests
from io import StringIO
import re
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


# ==============================================
# Helpers: Units
# ==============================================
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
    (Combines logic from both versions.)
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

    need_infer = (unit_source_col is None) or col_is_empty(df.get(unit_source_col))

    # --- 2) infer from Description if needed ---
    if need_infer and 'Description' in df.columns:
        unit_source_col = 'Unit'  # write inference into 'Unit'
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

# ==============================================
# Input loading
# ==============================================
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
    print(f"Total lines in file: {len(lines)}")
    print("\nFirst 15 lines of the file:")
    for i, line in enumerate(lines[:15]):
        print(f"Line {i}: {repr(line)}")
    data_start_row = 0
    header_found = False
    for i, line in enumerate(lines):
        if line.count(',') >= 3:
            if any(keyword in line.lower() for keyword in ['date', 'receipt', 'item', 'description', 'qty', 'sales', 'total', 'so', 'code']):
                data_start_row = i
                header_found = True
                print(f"Found header at line {i}: {line}")
                break
            elif re.search(r'\d+[,.]?\d*', line) and ',' in line:
                data_start_row = i
                print(f"Found potential data start at line {i}: {line}")
                break
    if not header_found:
        print("No clear header found, looking for any data rows...")
        for i, line in enumerate(lines):
            if ',' in line and len(line.strip()) > 10:
                data_start_row = i
                print(f"Using line {i} as data start: {line}")
                break
    return data_start_row

# ==============================================
# Expiration parsing (merged strict + cleanup)
# ==============================================
def _normalize_exp_str(date_str):
    """Return YYYY-MM-DD if valid and in sane range (2020-2045), else ''."""
    if not isinstance(date_str, str):
        date_str = str(date_str) if pd.notna(date_str) else ''
    date_str = date_str.strip()
    if not date_str:
        return ''
    fmts = ['%Y-%m-%d','%m/%d/%Y','%m-%d-%Y','%m/%d/%y','%m-%d-%y']
    dt = None
    for f in fmts:
        try:
            dt = datetime.strptime(date_str, f)
            break
        except Exception:
            continue
    if dt is None:
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
    return pd.Timestamp(dt).strftime('%Y-%m-%d')

def extract_expiration_from_description(description):
    """
    Extract expiration strictly from description; return (cleaned_description, yyyy-mm-dd or pd.NA).
    Never fabricate. Cleans out EXP/BB fragments from the text.
    """
    if pd.isna(description) or not isinstance(description, str) or not description.strip():
        return description, pd.NA

    text = description

    patterns = [
        r'[#\(\s]?EXP\s*(\d{4}-\d{2}-\d{2})\)?',
        r'[#\(\s]?exp\s*(\d{4}-\d{2}-\d{2})\)?',
        r'(?:exp(?:iry|iration)?|best\s*by|use\s*by|expires?|bb)[:\s\-]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:exp|bb)\b',
        r'\b(\d{4}-\d{2}-\d{2})\b'
    ]

    cleaned = text
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if not m:
            continue
        norm = _normalize_exp_str(m.group(1))
        if norm:
            cleaned = re.sub(pat, '', text, flags=re.IGNORECASE)
            break

    # Remove general EXP/BB fragments even if no valid date
    cleanup_patterns = [
        r'#exp\w*', r'exp\d+', r'bb\d+', r'#bb\w*', r'exp[:\s]*$', r'bb[:\s]*$', r'#\s*$', r'\s+#\s*'
    ]
    for cp in cleanup_patterns:
        cleaned = re.sub(cp, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,-#:()')
    norm_final = _normalize_exp_str(m.group(1)) if 'm' in locals() and m else ''
    return (cleaned if cleaned else description, pd.NA if not norm_final else norm_final)

# ==============================================
# Core cleaning pipeline
# ==============================================
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
    print("\nREMOVING INCOMPLETE ROWS:")
    print("-" * 30)

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
        print(f"✓ Removed {len(rows_to_remove)} incomplete rows")
        print(f"  Remaining rows: {len(df_clean)}")
    else:
        print("✓ No incomplete rows found - all data appears complete")

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

    # Placeholder/header rows & non-item adjustments clean (from CLEAN.py)
    num_cols = [c for c in ['Qty', 'Sales', 'Cost', 'Profit'] if c in df_clean.columns]
    if {'Item Code', 'Description'}.issubset(df_clean.columns) and len(num_cols) > 0:
        ic   = df_clean['Item Code'].astype('string').str.strip()
        desc = df_clean['Description'].astype('string').str.strip()

        ic_digits_only = ic.str.fullmatch(r'\d+')
        ic_non_numeric = ic.notna() & ~ic_digits_only
        account_like   = ic.str.contains(r'^(account|customer|member)\s*:?', case=False, na=False)
        desc_blank     = desc.isna() | (desc == '')
        numeric_zeros  = (
            df_clean[num_cols]
            .apply(pd.to_numeric, errors='coerce')
            .fillna(0)
            .eq(0)
            .all(axis=1)
        )
        placeholder_mask = numeric_zeros & (ic_non_numeric | desc_blank | account_like)

        if placeholder_mask.any():
            removed3 = df_clean.loc[placeholder_mask].copy()
            removed3['error_reason'] = 'placeholder/non-item row (e.g., header like "Account : ...")'
            removed3['error_stage']  = 'remove_incomplete_rows'
            errors.append(removed3)
            df_clean = df_clean.loc[~placeholder_mask]
            print(f"✓ Removed {int(placeholder_mask.sum())} placeholder/non-item rows")

    fin_cols = [c for c in ['Sales', 'Cost', 'Profit'] if c in df_clean.columns]
    if fin_cols:
        fin_zero = (
            df_clean[fin_cols]
            .apply(pd.to_numeric, errors='coerce')
            .fillna(0)
            .eq(0)
            .all(axis=1)
        )
        desc_l = (
            df_clean['Description'].astype('string').str.lower().str.strip()
            if 'Description' in df_clean.columns else
            pd.Series('', index=df_clean.index, dtype='string')
        )
        ic_l = (
            df_clean['Item Code'].astype('string').str.lower().str.strip()
            if 'Item Code' in df_clean.columns else
            pd.Series('', index=df_clean.index, dtype='string')
        )

        kw_desc  = r'(sales\s*discount|^discount$|less\s*discount|void|cancel|round(?:ing|[-\s]*off)?|change|senior|pwd|rebate|price\s*adj|adjustment)'
        kw_codes = r'^(sd|disc|discount|void|sc|pwd|rebate)$'

        is_adjustment = desc_l.str.contains(kw_desc, na=False) | ic_l.str.match(kw_codes, na=False)
        adj_mask = fin_zero & is_adjustment

        if adj_mask.any():
            removed_adj = df_clean.loc[adj_mask].copy()
            removed_adj['error_reason'] = 'non-item adjustment (e.g., Sales Discount/VOID/rounding)'
            removed_adj['error_stage']  = 'remove_incomplete_rows'
            errors.append(removed_adj)
            df_clean = df_clean.loc[~adj_mask]
            print(f"✓ Removed {int(adj_mask.sum())} non-item adjustment rows")

    final_count = len(df_clean)
    print(f"\nData validation summary:")
    print(f"  Initial rows: {initial_count}")
    print(f"  Removed rows: {initial_count - final_count}")
    print(f"  Final rows: {final_count}")

    errors_df = (
        pd.concat(errors, ignore_index=True)
        if errors
        else pd.DataFrame(columns=list(df_clean.columns) + ['error_reason', 'error_stage'])
    )
    return df_clean, errors_df

def map_columns_improved(df, target_columns):
    print("\nMAPPING COLUMNS:")
    print("-" * 30)
    column_mapping = {}
    available_cols = df.columns.tolist()
    print("Available columns:", available_cols, "\n")
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
            print(f"  {target_col} <- '{best_match}' (confidence: {best_score}%)")
        else:
            print(f"  {target_col} <- NO MATCH FOUND (best was '{best_match}' with {best_score}%)")
    return column_mapping

def _parse_money_series(s: pd.Series) -> pd.Series:
    """
    Parse money-like strings to numbers, handling:
      - (1,234.56)  -> -1234.56
      - 1,234.56-   -> -1234.56
      - 1,234.56 CR -> -1234.56   (DR stays positive)
      - 1.234,56 (EU) -> 1234.56
    Returns float dtype with NaN for unparseable.
    """
    if s is None:
        return pd.Series(dtype='float64')

    x = s.astype(str).str.strip()

    # normalize accounting negatives
    x = x.str.replace(r'^\(([^)]+)\)$', r'-\1', regex=True)           # (123.45) -> -123.45
    x = x.str.replace(r'^\s*([0-9.,]+)\s*-\s*$', r'-\1', regex=True)  # 123.45-  -> -123.45

    # handle CR/DR markers (prefer CR as negative)
    has_cr = x.str.contains(r'\bCR\b', case=False, regex=True)
    x = x.str.replace(r'\b[CD]R\b', '', regex=True, case=False).str.strip()
    x = x.mask(has_cr, '-' + x)  # make negative if CR

    # keep only digits, comma, dot, minus
    x = x.str.replace(r'[^\d,.\-]', '', regex=True)

    # If there is exactly one comma and no dot, treat comma as decimal
    def _commas_to_decimal(t):
        if t.count(',') == 1 and t.count('.') == 0:
            t = t.replace('.', '')    # (defensive: remove thousand dots if any)
            t = t.replace(',', '.')   # decimal comma -> dot
            return t
        # Otherwise, drop all commas as thousand separators
        return t.replace(',', '')
    x = x.apply(_commas_to_decimal)

    return pd.to_numeric(x, errors='coerce')


def clean_data_types_improved(df):
    print("\nCLEANING DATA TYPES:")
    print("-" * 30)
    df_clean = df.copy()

    # --- numeric columns with accounting-aware parser ---
    numeric_cols = ['Qty', 'Discount', 'Sales', 'Cost', 'Profit']
    for col in numeric_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            if col == 'Qty':
                # quantities rarely have CR/DR, so simpler parse
                df_clean[col] = pd.to_numeric(
                    df_clean[col]
                        .astype(str)  # <-- close the paren
                        .str.replace(r'[^\d.\-]', '', regex=True)
                        .replace(
                            {'': pd.NA, 'nan': pd.NA, 'none': pd.NA, 'NaN': pd.NA, 'None': pd.NA},
                            regex=False
                        ),
                    errors='coerce'
)

            else:
                df_clean[col] = _parse_money_series(df_clean[col])
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    # --- dates ---
    if 'Date' in df_clean.columns:
        original_count = df_clean['Date'].notna().sum()
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce', infer_datetime_format=True)
        epoch_mask = df_clean['Date'] == pd.Timestamp('1970-01-01')
        if epoch_mask.any():
            df_clean.loc[epoch_mask, 'Date'] = pd.NaT
        cleaned_count = df_clean['Date'].notna().sum()
        print(f"  Date: {original_count} -> {cleaned_count} valid dates")

    if 'Expiration Date' in df_clean.columns:
        df_clean['Expiration Date'] = df_clean['Expiration Date'].apply(
            lambda x: pd.NA if (x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and x.strip()=='')) else _normalize_exp_str(str(x))
        ).apply(lambda x: pd.NA if (isinstance(x, str) and x.strip()=='') else x)

    # --- text columns ---
    string_cols = ['Receipt', 'SO', 'Item Code', 'Description', 'Payment', 'Cashier ID', 'Unit']
    for col in string_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            df_clean[col] = (
                df_clean[col].astype(str).str.strip()
                .replace(['nan','none','null','','NaN','None','NULL'], pd.NA)
            )
            if col == 'Unit':
                df_clean[col] = df_clean[col].str.lower()
            if col == 'Item Code':
                df_clean[col] = df_clean[col].str.strip().str.upper()
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    # --- recompute Profit if missing ---
    if {'Sales','Cost'}.issubset(df_clean.columns):
        calc_profit = pd.to_numeric(df_clean['Sales'], errors='coerce') - pd.to_numeric(df_clean['Cost'], errors='coerce')
        if 'Profit' not in df_clean.columns or df_clean['Profit'].isna().any():
            df_clean['Profit'] = df_clean['Profit'].fillna(calc_profit)

    return df_clean




def classify_txn_type(row):
    # default
    t = "SALE"
    desc = str(row.get('Description', '') or '').lower()
    code = str(row.get('Item Code', '') or '').lower()
    qty  = pd.to_numeric(row.get('Qty', pd.NA), errors='coerce')

    # adjustments keywords (if they survived filters)
    if re.search(r'(discount|void|round(?:ing|[-\s]*off)|price\s*adj|adjustment|rebate|change|senior|pwd)', desc):
        return "ADJUSTMENT"

    # returns: negative qty or obvious words
    if (pd.notna(qty) and qty < 0) or re.search(r'(return|refund|rtn|rtv)', desc):
        return "RETURN"

    return t

def _row_hash_fn(r):
    keys = [
        str(r.get('Date', '')).strip(),
        str(r.get('Receipt', '')).strip(),
        str(r.get('SO', '')).strip(),
        str(r.get('Item Code', '')).strip(),
        str(r.get('Qty', '')).strip(),
        str(r.get('Sales', '')).strip(),
        str(r.get('Cost', '')).strip(),
    ]
    concat = '|'.join(keys)
    # short, deterministic string id:
    return pd.util.hash_pandas_object(pd.Series(concat)).astype(str).iloc[0]






def clean_dataframe_improved(df):
    print("\n" + "="*50)
    print("CLEANING DATAFRAME")
    print("="*50)

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
        mask = df_clean.astype(str).apply(
            lambda x: x.str.contains(pattern, case=False, na=False, regex=False)
        ).any(axis=1)
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

    df_final = pd.DataFrame()
    for target_col in target_columns:
        if target_col in column_mapping:
            source_col = column_mapping[target_col]
            df_final[target_col] = df_clean[source_col].copy()
            print(f"✓ Mapped '{source_col}' -> '{target_col}' ({df_clean[source_col].notna().sum()} values)")
        else:
            df_final[target_col] = pd.NA
            print(f"⚠ Created empty column for '{target_col}' (no source found)")
    df_final['_row_id'] = df_clean['_row_id'].copy()

    # Project early removals into target schema so the error file is consistent
    errors_aligned = []
    for e in errors_pre:
        aligned = project_to_target(e, column_mapping, target_columns)
        aligned['_row_id']      = e['_row_id'].values
        aligned['error_reason'] = e['error_reason'].values
        aligned['error_stage']  = e['error_stage'].values
        errors_aligned.append(aligned)

    # -------- extract expiration dates from descriptions --------
    if 'Description' in df_final.columns:
        print("\nExtracting expiration dates from descriptions...")
        descriptions_with_dates = 0
        for idx in df_final.index:
            original_desc = df_final.loc[idx, 'Description']
            cleaned_desc, exp_date = extract_expiration_from_description(original_desc)
            df_final.loc[idx, 'Description'] = cleaned_desc
            if pd.notna(exp_date) and str(exp_date).strip() != '':
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
    errors_all = pd.concat(errors_all, ignore_index=True) if errors_all else pd.DataFrame(
        columns=target_columns + ['_row_id','error_reason','error_stage']
    )

    # --- Fill-down for Receipt and SO (carry values into blanks) ---
    for c in ('Receipt', 'SO'):
        if c in df_final.columns:
            df_final[c] = (
                df_final[c]
                .astype('string')
                .replace({'': pd.NA, 'nan': pd.NA, 'NaN': pd.NA, 'None': pd.NA})
                .ffill()
            )
    if not errors_all.empty:
        for c in ('Receipt', 'SO'):
            if c in errors_all.columns:
                errors_all[c] = (
                    errors_all[c]
                    .astype('string')
                    .replace({'': pd.NA, 'nan': pd.NA, 'NaN': pd.NA, 'None': pd.NA})
                    .ffill()
                )

    # -------- final summary --------
    print(f"\n✅ Final cleaned DataFrame: {df_final.shape[0]} rows x {df_final.shape[1]} columns")
    if not df_final.empty:
        print("\nSample of final cleaned data:")
        print(df_final.head().to_string())

        # Drop helper id from the cleaned output (keep it in errors)
    if '_row_id' in df_final.columns:
        df_final = df_final.drop(columns=['_row_id'])

    # --- deterministic RowHash for idempotent loads ---
    df_final['RowHash'] = df_final.apply(_row_hash_fn, axis=1)

    # --- classify transaction type (optional but useful) ---
    df_final['TxnType'] = df_final.apply(classify_txn_type, axis=1)

    return df_final, errors_all


# ==============================================
# I/O helpers
# ==============================================
def save_error_report(errors_df, filename='cleaning_errors.xlsx'):
    if errors_df is None or errors_df.empty:
        print("\nNo removed rows to save. Skipping errors file.")
        return None
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        errors_df.to_csv(filename, index=False)
        print(f"\nErrors CSV saved to '{filename}' ({len(errors_df)} rows)." )
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
        df_out['Expiration Date'] = df_out['Expiration Date'].astype(str).replace({'NaT':'', 'nan':'', 'None':''})
    df_out.to_csv(filename, index=False)
    print(f"\nCleaned data saved to '{filename}'")
    print(f"Final dataset contains {len(df_out)} records")

    # Optional summary
    print("\nData Summary:")
    print("=" * 50)
    for col in df_out.columns:
        non_null_count = df_out[col].replace(['', 'nan'], pd.NA).notna().sum()
        print(f"{col}: {non_null_count} non-null values")
    return filename

def browse_for_file():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        print("Opening file browser...")
        file_path = filedialog.askopenfilename(
            title="Select CSV Data File",
            filetypes=[("CSV files", "*.csv"),("All files", "*.*")],
            initialdir=os.getcwd()
        )
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

# ==============================================
# Driver
# ==============================================
def fetch_and_clean_sales_data(source):
    csv_content = load_data_from_source(source)

    # --- Header sniff ---
    header_row = analyze_csv_structure(csv_content)   # index of header
    lines = csv_content.strip().split('\n')
    print(f"Detected header at line: {header_row}")
    csv_from_header = '\n'.join(lines[header_row:])

    try:
        df_raw = pd.read_csv(StringIO(csv_from_header))
        print(f"Successfully read CSV with shape: {df_raw.shape}")
    except Exception as e:
        print(f"CSV read failed: {e}")
        try:
            df_raw = pd.read_csv(StringIO(csv_from_header), sep=None, engine='python')
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

if __name__ == "__main__":
    # Default sample URL (kept for local tests)
    default_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/testdata-D3IKHaVvsV4pdgUGLj27PXAagiN6WO.csv"
    NON_INTERACTIVE = os.getenv("NON_INTERACTIVE", "0") == "1"

    # IMPORTANT: Set this once in your shell/env:
    #   Local pgAdmin first:
    #   export DATABASE_URL="postgresql://postgres:admin@localhost:5432/CAPSTONE"
    #
    #   Neon later (example):
    #   export DATABASE_URL="postgresql://USER:PASSWORD@YOURHOST.neon.tech/CAPSTONE?sslmode=require"

    try:
        # -------- source selection (interactive for local, env/CLI for servers) --------
        if len(sys.argv) > 1:
            data_source = sys.argv[1]
            print(f"Using data source from command line: {data_source}")
        elif NON_INTERACTIVE:
            print("Running in NON_INTERACTIVE mode...")
            data_source = default_url
        else:
            data_source = get_data_source()
            if not data_source:
                print("No data source provided. Using default test data...")
                data_source = default_url

        # -------- CLEAN --------
        cleaned_df, errors_df = fetch_and_clean_sales_data(data_source)

        # Save local artifacts (handy for debugging / audit)
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

        # -------- LOAD (Postgres CAPSTONE) --------
        # Use the original filename/URL (good for ops.etl_runs)
        file_name_for_run = data_source if data_source else output_file

        print("\n⏩ Loading cleaned data into Postgres (CAPSTONE)...")
        # If you haven't run create_schemas_tables.sql yet, run it once manually,
        # OR pass ensure_schema_once=True below to let the loader create it.
        run_id = run_full_load(
            file_name=file_name_for_run,
            cleaned_df=cleaned_df,
            errors_df=errors_df,
            ensure_schema_once=False   # set to True ONLY the first time if you didn't run the SQL
        )
        print(f"✅ ETL load completed. run_id = {run_id}")

        # Optional preview (skip in NON_INTERACTIVE mode)
        if not NON_INTERACTIVE:
            view_sample = input("\nView a sample of the cleaned data? (y/n): ").strip().lower()
            if view_sample == 'y':
                print("\nSample of cleaned data:")
                print("=" * 80)
                print(cleaned_df.head(10).to_string1(index=False))

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
