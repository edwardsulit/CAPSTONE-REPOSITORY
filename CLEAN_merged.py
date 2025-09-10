# CLEAN.py — strict expiration-from-description + 'NA' export
# -----------------------------------------------------------
import os
import re
import sys
from io import StringIO
from datetime import datetime

import pandas as pd
import requests

# Optional (only used if you choose "Browse")
try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


# =============================
# Unit normalization helpers
# =============================
UNIT_ALIASES = {
    "pcs": {"pc", "pcs", "piece", "pieces", "unit", "units"},
    "box": {"box", "boxes", "bx"},
    "pack": {"pack", "packs", "pkt", "packet", "packets"},
    "kg": {"kg", "kilogram", "kilograms"},
    "g": {"g", "gram", "grams"},
    "l": {"l", "liter", "liters"},
    "ml": {"ml", "milliliter", "milliliters"},
}

def canonical_unit(text):
    if not isinstance(text, str):
        return pd.NA
    t = text.strip().lower()
    for canon, aliases in UNIT_ALIASES.items():
        if t == canon or t in aliases:
            return canon
    # loose regex catch
    if re.search(r"\bpcs?\b", t): return "pcs"
    if re.search(r"\bpieces?\b", t): return "pcs"
    if re.search(r"\bboxes?\b", t): return "box"
    if re.search(r"\bpacks?\b|\bpkt\b|\bpackets?\b", t): return "pack"
    if re.search(r"\bkg\b|\bkilograms?\b", t): return "kg"
    if re.search(r"\bgrams?\b|\bg\b", t): return "g"
    if re.search(r"\bliters?\b|\bl\b", t): return "l"
    if re.search(r"\bmilliliters?\b|\bml\b", t): return "ml"
    return pd.NA

def normalize_units_on_df(df):
    """
    Fill/standardize Unit. If there's no usable Unit column (missing or all NA),
    infer from Description. Also default to 'pcs' when nothing obvious is found.
    """
    df = df.copy()

    # 1) find a usable unit source column
    unit_source_col = None
    for cand in ["Unit", "Units", "UOM", "uom", "unit", "units"]:
        if cand in df.columns:
            unit_source_col = cand
            break

    def col_is_empty(series):
        if series is None:
            return True
        s = (
            series.astype(str)
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "NULL": pd.NA})
        )
        return s.isna().all()

    need_infer = (unit_source_col is None) or col_is_empty(df[unit_source_col])

    # 2) infer from Description if needed
    if need_infer and "Description" in df.columns:
        unit_source_col = "Unit"  # write inference into 'Unit'
        # Expanded vocabulary (also matches tokens without spaces like "500ml")
        pattern = r"""(?ix)
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
        """
        df[unit_source_col] = df["Description"].astype(str).str.extract(pattern)[0]

    if unit_source_col is None:
        return df, "No unit column found; skipped unit normalization."

    # 3) canonicalize tokens to a small set
    def canon(u):
        u = canonical_unit(u)  # will map pcs/box/pack/kg/g/l/ml
        if pd.isna(u):
            return pd.NA

        # extra mappings for pharma forms -> treat as piece-like
        tablety = {"tab", "tabs", "tablet", "tablets"}
        capsuly = {"cap", "caps", "capsule", "capsules"}
        vials   = {"vial", "vials", "amp", "ampule", "ampoule"}
        sachets = {"sachet", "sachets"}
        bottles = {"bottle", "bottles", "bot", "btl"}
        tubes   = {"tube", "tubes"}
        containers = {"jar", "jars", "can", "cans", "tin", "tins"}
        misc_piece = {"strip", "blister", "blisters", "roll", "rolls", "pair", "pairs", "set", "sets"}
        dosage = {"mg", "mcg", "iu"}  # dosage units; default to piece-like

        t = str(u).lower().strip()
        if (
            t in tablety or t in capsuly or t in vials or t in sachets or
            t in bottles or t in tubes or t in containers or t in misc_piece or t in dosage
        ):
            return "pcs"
        return t

    df["Unit_std"] = df[unit_source_col].apply(canon)

    # 4) optional scaling for g->kg and ml->l only (leave mg/mcg alone)
    if "Qty" in df.columns:
        q = pd.to_numeric(df["Qty"], errors="coerce")
        mask_g  = df["Unit_std"].eq("g")
        mask_ml = df["Unit_std"].eq("ml")
        if mask_g.any():
            df.loc[mask_g, "Qty"] = q.where(~mask_g, q / 1000.0)
            df.loc[mask_g, "Unit_std"] = "kg"
        if mask_ml.any():
            df.loc[mask_ml, "Qty"] = q.where(~mask_ml, q / 1000.0)
            df.loc[mask_ml, "Unit_std"] = "l"

    # 5) default any remaining NA to 'pcs'
    if "Qty" in df.columns:
        mask_na = df["Unit_std"].isna() & pd.to_numeric(df["Qty"], errors="coerce").notna()
        df.loc[mask_na, "Unit_std"] = "pcs"
    else:
        df.loc[df["Unit_std"].isna(), "Unit_std"] = "pcs"

    df["Unit"] = df["Unit_std"]
    df.drop(columns=["Unit_std"], inplace=True)
    return df, "Units normalized (including inference from Description; defaulted missing to 'pcs')."


# =============================
# Input helpers (URL/path/browse)
# =============================
def load_data_from_source(source: str) -> str:
    """Return CSV text from URL or local file path."""
    if source.startswith(("http://", "https://")):
        print(f"Fetching data from URL: {source}")
        resp = requests.get(source)
        resp.raise_for_status()
        print("Data fetched successfully from URL!")
        return resp.text
    else:
        print(f"Reading data from file: {source}")
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            txt = f.read()
        print("Data loaded successfully from file!")
        return txt

def browse_for_file() -> str | None:
    if not TK_AVAILABLE:
        print("Browse not available on this environment.")
        return None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        fp = filedialog.askopenfilename(
            title="Select CSV Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.getcwd(),
        )
        root.destroy()
        return fp if fp else None
    except Exception:
        return None

def get_data_source() -> str | None:
    print("Data Cleaning Program")
    print("=" * 50)
    print("1. Browse for local CSV file")
    print("2. Enter file path manually")
    print("3. Enter URL to CSV file")
    while True:
        choice = input("Choose option (1/2/3) or press Enter to browse: ").strip()
        if not choice or choice == "1":
            src = browse_for_file()
            if src:
                return src
            retry = input("No file selected. Try another method? (y/n): ").strip().lower()
            if retry != "y":
                return None
        elif choice == "2":
            src = input("Enter file path: ").strip()
            if src and os.path.exists(src):
                return src
            print("File not found.")
        elif choice == "3":
            src = input("Enter URL: ").strip()
            if src.startswith(("http://", "https://")):
                return src
            print("Please enter a valid URL.")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


# =============================
# Expiration helpers (STRICT)
# =============================
def _normalize_exp_str(date_str):
    """Return YYYY-MM-DD if valid and in sane range (2020–2045), else ''."""
    if not isinstance(date_str, str):
        date_str = str(date_str) if pd.notna(date_str) else ""
    date_str = date_str.strip()
    if not date_str:
        return ""
    # try explicit formats first
    fmts = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]
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
            dt = pd.to_datetime(date_str, errors="coerce")
        except Exception:
            dt = None
        if pd.isna(dt):
            dt = None
    if dt is None:
        return ""
    if not (2020 <= int(dt.year) <= 2045):
        return ""
    return dt.strftime("%Y-%m-%d")

def extract_expiration_from_description(description: str) -> tuple[str, str]:
    """
    Parse expiration strictly from Description; return (cleaned_description, exp_str_or_blank).
    Never fabricate an expiration.
    """
    if pd.isna(description) or not isinstance(description, str) or not description.strip():
        return description, ""

    text = description
    patterns = [
        r"[#\(\s]?EXP\s*(\d{4}-\d{2}-\d{2})\)?",
        r"[#\(\s]?exp\s*(\d{4}-\d{2}-\d{2})\)?",
        r"(?:exp(?:iry|iration)?|best\s*by|use\s*by|expires?|bb)[:\s\-]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:exp|bb)\b",
        r"\b(\d{4}-\d{2}-\d{2})\b",
    ]

    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if not m:
            continue
        norm = _normalize_exp_str(m.group(1))
        if norm:
            cleaned = re.sub(pat, "", text, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ,-#:()")
            return cleaned or description, norm

    cleaned = re.sub(r"\s{2,}", " ", text).strip(" ,-#:()")
    return cleaned or description, ""


# =============================
# Core cleaning pipeline
# =============================
def project_to_target(df_in, column_mapping, target_columns):
    out = pd.DataFrame()
    for t in target_columns:
        src = column_mapping.get(t)
        if src is not None and src in df_in.columns:
            out[t] = df_in[src]
        else:
            out[t] = pd.NA
    if "_row_id" in df_in.columns:
        out["_row_id"] = df_in["_row_id"]
    return out

def remove_incomplete_rows(df):
    """
    Remove rows with missing critical supporting data.
    Focus on rows where financial data exists but supporting data is missing.
    """
    df_clean = df.copy()
    errors = []

    supporting_columns = ["Item Code", "Description"]
    financial_columns = ["Sales", "Cost", "Profit"]

    rows_to_remove = []
    for idx in df_clean.index:
        has_financial_data = any(
            (col in df_clean.columns)
            and pd.notna(df_clean.loc[idx, col])
            and df_clean.loc[idx, col] != 0
            for col in financial_columns
        )
        if has_financial_data:
            missing_supporting = []
            for col in supporting_columns:
                if col in df_clean.columns:
                    value = df_clean.loc[idx, col]
                    if pd.isna(value) or str(value).strip().lower() in ("", "nan", "none", "null"):
                        missing_supporting.append(col)
            if missing_supporting:
                rows_to_remove.append(idx)

    if rows_to_remove:
        removed = df_clean.loc[rows_to_remove].copy()
        removed["error_reason"] = "financial data present but missing supporting fields"
        removed["error_stage"] = "remove_incomplete_rows"
        errors.append(removed)
        df_clean = df_clean.drop(rows_to_remove)

    important_columns = ["Item Code", "Description", "Qty", "Sales", "Cost"]
    available_important = [c for c in important_columns if c in df_clean.columns]
    if available_important:
        empty_mask = df_clean[available_important].isna().all(axis=1)
        if empty_mask.any():
            removed2 = df_clean.loc[empty_mask].copy()
            removed2["error_reason"] = "all important fields empty"
            removed2["error_stage"] = "remove_incomplete_rows"
            errors.append(removed2)
            df_clean = df_clean.loc[~empty_mask]

    errors_df = (
        pd.concat(errors, ignore_index=True)
        if errors
        else pd.DataFrame(columns=list(df.columns) + ["error_reason", "error_stage"])
    )
    return df_clean, errors_df

def _parse_money_series(s: pd.Series) -> pd.Series:
    """Parse various money-like strings to numeric (handles () negatives, CR/DR, commas)."""
    if s is None:
        return pd.Series(dtype="float64")

    x = s.astype(str).str.strip()

    # accounting negatives
    x = x.str.replace(r"^\(([^)]+)\)$", r"-\1", regex=True)          # (123.45) -> -123.45
    x = x.str.replace(r"^\s*([0-9.,]+)\s*-\s*$", r"-\1", regex=True) # 123.45-  -> -123.45

    # CR/DR markers
    has_cr = x.str.contains(r"\bCR\b", case=False, regex=True)
    x = x.str.replace(r"\b[CD]R\b", "", regex=True, case=False).str.strip()
    x = x.mask(has_cr, "-" + x)

    # keep digits, dot, comma, minus
    x = x.str.replace(r"[^\d,.\-]", "", regex=True)

    # if one comma and no dot -> treat comma as decimal
    def _commas_to_decimal(t):
        if t.count(",") == 1 and t.count(".") == 0:
            t = t.replace(".", "")
            t = t.replace(",", ".")
            return t
        return t.replace(",", "")

    x = x.apply(_commas_to_decimal)
    return pd.to_numeric(x, errors="coerce")

def _recover_sales_if_empty(df_final, df_clean, column_mapping):
    """Fill df_final['Sales'] if mapping produced an empty column (line amounts only)."""
    if "Sales" not in df_final.columns:
        return df_final
    if df_final["Sales"].notna().any():
        return df_final

    # EARLY GRAB: if the raw data literally has a Sales-like column, use it
    literal_candidates = {
        "sales", "sale", "sales amount", "sales_amt",
        "line amount", "line total", "extended", "ext amount",
    }
    for col in df_clean.columns:
        if str(col).strip().lower() in literal_candidates:
            parsed = _parse_money_series(df_clean[col])
            if parsed.notna().sum() > 0:
                df_final["Sales"] = parsed
                print(f"🔎 Recovered Sales from raw column '{col}' ({parsed.notna().sum()} values).")
                return df_final

    # Fallback: other line-amount names
    candidates = re.compile(
        r"(sales?(?!\s*tax)|sale\s*amount|sales?\s*(amount|value|price)|"
        r"line\s*(amount|total)|extended|ext|net\s*(amount|total|sales?)|"
        r"line\s*price|unit\s*price)",
        re.I,
    )
    reserved = set(v for v in column_mapping.values() if v is not None)

    best_col, best_series, best_non_null = None, None, -1
    for col in df_clean.columns:
        if col in reserved:
            continue
        if not candidates.search(str(col)):
            continue
        parsed = _parse_money_series(df_clean[col])
        nn = parsed.notna().sum()
        if nn > best_non_null:
            best_col, best_series, best_non_null = col, parsed, nn

    if best_series is not None and best_non_null > 0:
        df_final["Sales"] = best_series
        print(f"🔎 Recovered Sales from raw column '{best_col}' ({best_non_null} values).")
        return df_final

    # Last resort ONLY if every receipt has <= 1 line (so Payment == line)
    if "Payment" in df_final.columns and "Receipt" in df_final.columns:
        line_counts = df_final.groupby("Receipt", dropna=False).size()
        if (line_counts <= 1).all():
            pay = _parse_money_series(df_final["Payment"])
            if pay.notna().any():
                df_final["Sales"] = pay
                print("🔎 Recovered Sales from 'Payment' (single-line receipts only).")
                return df_final
        else:
            print("⚠ Skipped Payment fallback: multiple lines per receipt detected.")

    print("⚠ Could not recover Sales from raw columns.")
    return df_final

def _drop_summary_rows_after_map(df: pd.DataFrame) -> pd.DataFrame:
    """Remove receipt-level summary rows that slipped through mapping."""
    if df.empty:
        return df

    def _is_blank(s):
        return s.isna() | (s.astype(str).str.strip() == "")

    # rows that literally say "total / subtotal / grand total"
    is_total_word = pd.Series(False, index=df.index)
    for c in ("Description", "Item Code", "Receipt", "SO"):
        if c in df.columns:
            is_total_word |= df[c].astype(str).str.strip().str.lower().isin(
                ["total", "subtotal", "grand total"]
            )

    qty = pd.to_numeric(df.get("Qty"), errors="coerce") if "Qty" in df.columns else pd.Series(index=df.index, dtype="float64")
    num_cols = [c for c in ["Qty", "Discount", "Sales", "Cost", "Profit"] if c in df.columns]
    has_any_numeric = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in num_cols}).notna().any(axis=1)

    ic   = df.get("Item Code")
    desc = df.get("Description")

    mask = (
        (( _is_blank(ic) if ic is not None else True) &
         (( _is_blank(desc) if desc is not None else True) | is_total_word))
        & qty.isna()                  # no line quantity
        & has_any_numeric             # but has numeric totals present
    )

    n = int(mask.sum())
    if n:
        print(f"✓ Dropped {n} summary/total rows after mapping.")
        return df.loc[~mask].copy()
    return df

def clean_data_types_improved(df):
    """
    Improved data type cleaning with better error handling.
    Includes: convert epoch 1970-01-01 dates to NaT.
    """
    print("\nCLEANING DATA TYPES")
    print("-" * 30)
    df_clean = df.copy()

    # Numeric columns
    numeric_cols = ["Qty", "Discount", "Sales", "Cost", "Profit"]
    for col in numeric_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            if col == "Qty":
                df_clean[col] = pd.to_numeric(
                    df_clean[col].astype(str)
                    .str.replace(r"[^\d.\-]", "", regex=True)
                    .replace({"": pd.NA, "nan": pd.NA, "none": pd.NA, "NaN": pd.NA, "None": pd.NA}),
                    errors="coerce",
                )
            else:
                df_clean[col] = _parse_money_series(df_clean[col])
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    # Dates — treat 1970-01-01 as missing (common when raw has 0)
    date_cols = ["Date", "Expiration Date"]
    for col in date_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce", infer_datetime_format=True)
            epoch_mask = df_clean[col] == pd.Timestamp("1970-01-01")
            if epoch_mask.any():
                df_clean.loc[epoch_mask, col] = pd.NaT
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid dates")

    # Text columns (includes Unit)
    string_cols = ["Receipt", "SO", "Item Code", "Description", "Payment", "Cashier ID", "Unit"]
    for col in string_cols:
        if col in df_clean.columns:
            original_count = df_clean[col].notna().sum()
            df_clean[col] = (
                df_clean[col].astype(str).str.strip()
                .replace(["nan", "none", "null", "", "NaN", "None", "NULL"], pd.NA)
            )
            if col == "Unit":
                df_clean[col] = df_clean[col].str.lower()
            cleaned_count = df_clean[col].notna().sum()
            print(f"  {col}: {original_count} -> {cleaned_count} valid values")

    return df_clean

def map_columns_improved(df, target_columns):
    """
    Improved column mapping with pattern matching and fuzzy-ish scoring.
    """
    print("\nMAPPING COLUMNS")
    print("-" * 30)
    column_mapping = {}
    available_cols = df.columns.tolist()

    mapping_patterns = {
        "Date": ["date", "time", "datetime", "day", "created", "timestamp", "when", "dt"],
        "Receipt": ["receipt", "rcpt", "ticket", "trans", "transaction", "ref", "reference", "no"],
        "SO": ["so", "sales order", "order", "order no", "order number", "sales_order", "ord"],
        "Item Code": ["item", "code", "sku", "product code", "prod code", "barcode", "item_code", "product_code", "plu"],
        "Description": ["description", "desc", "product", "item name", "name", "title", "product_name", "item_name"],
        "Expiration Date": ["exp", "expiry", "expiration", "best by", "use by", "expires", "bb"],
        "Qty": ["qty", "quantity", "amount", "count", "qnty", "qnt"],
        "Unit": ["unit", "units", "uom", "pack", "packet", "packets", "box", "boxes", "pcs", "pc", "piece", "pieces", "kg", "g", "l", "ml"],
        "Discount": ["discount", "disc", "off", "reduction", "rebate", "promo"],
        "Sales": ["sales", "total", "amount", "price", "value", "revenue", "sale", "net", "gross"],
        "Cost": ["cost", "cogs", "unit cost", "purchase", "buy", "wholesale"],
        "Profit": ["profit", "margin", "gain", "net profit", "gp"],
        "Payment": ["payment", "pay", "method", "type", "pay_method", "tender"],
        "Cashier ID": ["cashier", "user", "employee", "staff", "operator", "clerk", "cashier_id", "user_id", "emp"],
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
                    pl = pattern.lower()
                    if pl in col_lower:
                        score = max(score, 80)
                    elif col_lower in pl:
                        score = max(score, 70)
                    elif any(word in col_lower for word in pl.split()):
                        score = max(score, 50)
                    elif any(word in pl for word in col_lower.split("_")):
                        score = max(score, 30)
            if score > best_score:
                best_score = score
                best_match = col

        # prefer literal 'Sales' if present
        if target_col == "Sales":
            preferred_aliases = {
                "sales", "sale", "sales amount", "sales_amt",
                "line amount", "line total", "extended", "ext amount",
            }
            exact = [c for c in available_cols if str(c).strip().lower() in preferred_aliases]
            if exact:
                best_match = exact[0]
                best_score = 101

        if best_match and best_score >= 20:
            column_mapping[target_col] = best_match
            print(f"  {target_col} <- '{best_match}'")
        else:
            print(f"  {target_col} <- NO MATCH")

    return column_mapping

def _drop_pre_map_totals(df):
    total_patterns = [r"\bgrand\s*total\b", r"\bsub\s*total\b", r"\btotal\b"]
    rows_before = len(df)
    for pattern in total_patterns:
        mask = df.astype(str).apply(
            lambda x: x.str.contains(pattern, case=False, na=False, regex=True)
        ).any(axis=1)
        if mask.any():
            df = df.loc[~mask]
    removed = rows_before - len(df)
    if removed:
        print(f"Removed {removed} total/summary rows (pre-map).")
    return df

def clean_dataframe_improved(df):
    """
    Clean & standardize dataframe. Tracks and returns all removed rows with reasons.
    """
    print("\n" + "=" * 50)
    print("CLEANING DATAFRAME")
    print("=" * 50)

    df_clean = df.copy()
    df_clean["_row_id"] = df_clean.index

    # capture early removals BEFORE mapping
    errors_pre = []

    # 1) Remove summary/total rows
    rows_before = len(df_clean)
    df_tmp = _drop_pre_map_totals(df_clean.copy())
    if len(df_tmp) < rows_before:
        removed = df_clean.loc[~df_clean.index.isin(df_tmp.index)].copy()
        removed["error_reason"] = "summary/total row"
        removed["error_stage"] = "pre-map"
        errors_pre.append(removed)
        df_clean = df_tmp

    # 2) Remove completely empty rows
    empty_mask_all = df_clean.isna().all(axis=1)
    if empty_mask_all.any():
        removed = df_clean.loc[empty_mask_all].copy()
        removed["error_reason"] = "completely empty row"
        removed["error_stage"] = "pre-map"
        errors_pre.append(removed)
        df_clean = df_clean.loc[~empty_mask_all]

    if len(df_clean) == 0:
        print("WARNING: No data remaining after cleaning!")
        return pd.DataFrame(), pd.DataFrame()

    # --- mapping into target schema ---
    target_columns = [
        "Date", "Receipt", "SO", "Item Code", "Description", "Expiration Date",
        "Qty", "Unit", "Discount", "Sales", "Cost", "Profit", "Payment", "Cashier ID",
    ]
    column_mapping = map_columns_improved(df_clean, target_columns)

    # Build df_final (in target schema)
    df_final = pd.DataFrame()
    for target_col in target_columns:
        if target_col in column_mapping:
            src = column_mapping[target_col]
            df_final[target_col] = df_clean[src].copy()
            print(f"✓ Mapped '{src}' -> '{target_col}'")
        else:
            df_final[target_col] = pd.NA
            print(f"⚠ Created empty column for '{target_col}' (no source found)")
    df_final["_row_id"] = df_clean["_row_id"].copy()

    # Drop any remaining summary rows that slipped through
    df_final = _drop_summary_rows_after_map(df_final)

    # Recover Sales if mapping missed it
    df_final = _recover_sales_if_empty(df_final, df_clean, column_mapping)

    # Project early removals into target schema so the error file is consistent
    errors_aligned = []
    for e in errors_pre:
        aligned = project_to_target(e, column_mapping, target_columns)
        aligned["_row_id"] = e["_row_id"].values
        aligned["error_reason"] = e["error_reason"].values
        aligned["error_stage"] = e["error_stage"].values
        errors_aligned.append(aligned)

    # -------- Expiration extraction (STRICT + non-destructive) --------
    # 1) Normalize any pre-existing Expiration Date from the source
    if "Expiration Date" in df_final.columns:
        df_final["Expiration Date"] = df_final["Expiration Date"].apply(_normalize_exp_str)

    # 2) Extract from Description ONLY to fill blanks
    if "Description" in df_final.columns:
        filled_from_desc = 0
        for idx in df_final.index:
            original_desc = df_final.at[idx, "Description"]
            cleaned_desc, exp_from_desc = extract_expiration_from_description(original_desc)
            df_final.at[idx, "Description"] = cleaned_desc
            if (not df_final.at[idx, "Expiration Date"]) and exp_from_desc:
                df_final.at[idx, "Expiration Date"] = exp_from_desc
                filled_from_desc += 1
        print(f"✓ Filled {filled_from_desc} missing expirations from Description; others left blank")

    # -------- Unit normalization --------
    df_final, unit_msg = normalize_units_on_df(df_final)
    print(f"✓ {unit_msg}")

    # -------- Type cleaning --------
    df_final = clean_data_types_improved(df_final)

    # -------- Remove incomplete rows (and collect errors) --------
    df_final, errs_incomplete = remove_incomplete_rows(df_final)

    # -------- Drop duplicates (and collect) --------
    errors_post = []
    dupe_subset = [c for c in ["Date", "Receipt", "SO", "Item Code", "Qty", "Sales", "Cost"] if c in df_final.columns]
    dup_mask = df_final.duplicated(subset=dupe_subset, keep="first") if dupe_subset else df_final.duplicated(keep="first")
    if dup_mask.any():
        removed_dup = df_final.loc[dup_mask].copy()
        removed_dup["error_reason"] = "duplicate row"
        removed_dup["error_stage"] = "duplicates"
        errors_post.append(removed_dup)
        df_final = df_final.loc[~dup_mask]
        print(f"✓ Removed {int(dup_mask.sum())} duplicate rows")

    # (Optional) remove rows effectively empty across important fields (after type clean)
    important = [c for c in ["Item Code", "Description", "Qty", "Sales", "Cost"] if c in df_final.columns]
    if important:
        mask_all_null = df_final[important].isna().all(axis=1)
        if mask_all_null.any():
            removed_empty = df_final.loc[mask_all_null].copy()
            removed_empty["error_reason"] = "all important fields empty (post-map)"
            removed_empty["error_stage"] = "post-map"
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
        columns=target_columns + ["_row_id", "error_reason", "error_stage"]
    )

    # --- Fill-down for Receipt and SO (carry values into blanks) ---
    for c in ("Receipt", "SO"):
        if c in df_final.columns:
            df_final[c] = (
                df_final[c]
                .astype("string")
                .replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "None": pd.NA})
                .ffill()
            )
    if not errors_all.empty:
        for c in ("Receipt", "SO"):
            if c in errors_all.columns:
                errors_all[c] = (
                    errors_all[c]
                    .astype("string")
                    .replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "None": pd.NA})
                    .ffill()
                )

    # --- Final normalization: ensure Expiration Date is YYYY-MM-DD or blank ---
    if "Expiration Date" in df_final.columns:
        df_final["Expiration Date"] = df_final["Expiration Date"].apply(lambda x: _normalize_exp_str(x))

    # Drop helper id from cleaned output (keep it in errors)
    if "_row_id" in df_final.columns:
        df_final = df_final.drop(columns=["_row_id"])

    print(f"\n✅ Final cleaned DataFrame: {df_final.shape[0]} rows x {df_final.shape[1]} columns")
    if not df_final.empty:
        print("\nSample of final cleaned data:")
        print(df_final.head().to_string())

    return df_final, errors_all


# =============================
# Save helpers
# =============================
def save_error_report(errors_df, filename="cleaning_errors.xlsx"):
    """Save removed rows (with reasons) to .xlsx; fallback to .csv if needed."""
    if errors_df is None or errors_df.empty:
        print("\nNo removed rows to save. Skipping errors file.")
        return None

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".csv":
        errors_df.to_csv(filename, index=False)
        print(f"\nErrors CSV saved to '{filename}' ({len(errors_df)} rows).")
        return filename

    try:
        # Requires openpyxl installed
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            errors_df.to_excel(writer, index=False, sheet_name="removed_rows")
        print(f"\nErrors workbook saved to '{filename}' ({len(errors_df)} rows).")
        return filename
    except Exception as e:
        print(f"Could not write Excel file ({e}). Saving CSV fallback.")
        fallback = os.path.splitext(filename)[0] + ".csv"
        errors_df.to_csv(fallback, index=False)
        print(f"Errors CSV saved to '{fallback}' ({len(errors_df)} rows).")
        return fallback

def save_cleaned_data(df, filename="cleaned_sales_data.csv"):
    """
    Save the cleaned dataframe to CSV.
    Very important: show literal 'NA' for rows without any expiration.
    """
    df_out = df.copy()

    # Ensure Expiration Date is a string column and show 'NA' when missing
    if "Expiration Date" in df_out.columns:
        # normalize any residual date-like to YYYY-MM-DD or ''
        df_out["Expiration Date"] = df_out["Expiration Date"].apply(_normalize_exp_str)
        # convert missing/blank to literal 'NA'
        df_out["Expiration Date"] = (
            df_out["Expiration Date"]
            .astype("string")
            .replace({"NaT": pd.NA, "nan": pd.NA, "": pd.NA, None: pd.NA})
            .fillna("NA")
        )

    df_out.to_csv(filename, index=False)
    print(f"\nCleaned data saved to '{filename}'")
    print(f"Final dataset contains {len(df_out)} records")

    # Quick summary
    print("\nData Summary:")
    print("=" * 50)
    for col in df_out.columns:
        non_null_count = df_out[col].notna().sum()
        print(f"{col}: {non_null_count} non-null values")

    print("\nFirst 5 rows of cleaned data:")
    print(df_out.head())

    return filename


# =============================
# Orchestrator for fetch+clean
# =============================
def fetch_and_clean_sales_data(source):
    """
    Load CSV data from file path or URL and clean it.
    Returns (cleaned_df, errors_df).
    """
    csv_text = load_data_from_source(source)

    # Many exports have 5 header lines to skip
    lines = csv_text.strip().split("\n")
    if len(lines) > 5:
        csv_from_row_6 = "\n".join(lines[5:])
        print("Skipping first 5 lines…")
    else:
        csv_from_row_6 = csv_text

    # Parse CSV
    try:
        df_raw = pd.read_csv(StringIO(csv_from_row_6))
        print(f"Successfully read CSV with shape: {df_raw.shape}")
    except Exception as e:
        print(f"Standard CSV read failed ({e}); retrying with auto-separator…")
        df_raw = pd.read_csv(StringIO(csv_from_row_6), sep=None, engine="python")
        print(f"Auto-separator CSV read OK, shape: {df_raw.shape}")

    print("Raw columns:", list(df_raw.columns))
    cleaned_df, errors_df = clean_dataframe_improved(df_raw)
    return cleaned_df, errors_df


# =============================
# Main
# =============================
if __name__ == "__main__":
    # Allow passing a path/URL as an argument; else interactive prompt
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        src = get_data_source()

    if not src:
        print("No source provided. Exiting.")
        sys.exit(0)

    cleaned, errs = fetch_and_clean_sales_data(src)

    # Save outputs
    if not cleaned.empty:
        save_cleaned_data(cleaned, filename="cleaned_sales_data.csv")
    if errs is not None and not errs.empty:
        save_error_report(errs, filename="cleaning_errors.xlsx")

    print("\nAll done.")
