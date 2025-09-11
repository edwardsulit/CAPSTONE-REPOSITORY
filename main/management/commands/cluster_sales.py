import io
import os
import json
from datetime import datetime
from io import StringIO

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

# === scikit-learn bits ===
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ---------- PROMPT HELPERS ----------
try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

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
    print("Data Clustering")
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

def _load_csv_from_source(source: str) -> pd.DataFrame:
    """Load CSV into a DataFrame from a path or URL (keeps your prompt’s logic)."""
    if source.startswith(("http://", "https://")):
        import requests  # lazy import
        print(f"⬇️  Fetching CSV from URL: {source}")
        r = requests.get(source, timeout=60)
        r.raise_for_status()
        # try utf-8 then latin-1 (same approach you use elsewhere)
        try:
            txt = r.content.decode("utf-8")
        except UnicodeDecodeError:
            txt = r.content.decode("latin-1")
        return pd.read_csv(StringIO(txt))
    else:
        print(f"\n📄 Reading CSV from file: {source}")
        # Try utf-8, fallback latin-1 for Windows exports
        try:
            return pd.read_csv(source, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(source, encoding="latin-1")


# ---------- CLUSTERING HELPERS ----------
def _choose_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=["number"]).copy()
    # drop all-null or constant columns
    drop = []
    for c in num.columns:
        s = num[c]
        if s.isna().all() or s.dropna().nunique() <= 1:
            drop.append(c)
    if drop:
        num = num.drop(columns=drop, errors="ignore")
    if num.shape[1] == 0:
        raise CommandError("No suitable numeric columns to cluster on.")
    return num

def _auto_kmeans(X_scaled, k_min=2, k_max=8, n_init=10, random_state=42):
    best_k, best_score, best_model = None, -1.0, None
    scores = {}
    for k in range(k_min, k_max + 1):
        m = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
        labels = m.fit_predict(X_scaled)
        if len(set(labels)) <= 1 or len(set(labels)) >= len(labels):
            scores[k] = float("nan")
            continue
        sc = silhouette_score(X_scaled, labels)
        scores[k] = float(sc)
        if sc > best_score:
            best_k, best_score, best_model = k, sc, m
    if best_model is None:
        print("⚠️  Silhouette selection failed; defaulting to k=3.")
        best_k = 3
        best_model = KMeans(n_clusters=3, n_init=n_init, random_state=random_state).fit(X_scaled)
        scores[3] = float("nan")
    return best_k, best_model, scores


# ---------- DJANGO MANAGEMENT COMMAND ----------
class Command(BaseCommand):
    help = "Load a cleaned CSV via the same prompt flow as CLEAN_merged.py, run K-Means clustering, and save outputs."

    def handle(self, *args, **options):
        # 1) Ask for CSV source using your exact prompt flow
        src = get_data_source()   # identical UX to your cleaner  :contentReference[oaicite:2]{index=2}
        if not src:
            raise CommandError("No source provided. Exiting.")

        # 2) Load CSV
        df = _load_csv_from_source(src)
        if df.empty:
            raise CommandError("The CSV appears to be empty.")

        # 3) Select features (all numeric)
        feat_df = _choose_numeric_features(df).fillna(0)

        # 4) Scale + pick k with silhouette
        scaler = StandardScaler()
        Xs = scaler.fit_transform(feat_df.values)
        print("🔎 Selecting number of clusters (k) using silhouette score…")
        best_k, model, scores = _auto_kmeans(Xs)
        print(f"\n✔ Best k: {best_k}")
        print(f"ℹ️  Silhouette scores: {json.dumps(scores, indent=2)}")

        labels = model.labels_

        # 5) Attach labels to original data
        out = df.copy()
        out["cluster"] = labels

        # 6) Per-cluster summary (means of numeric cols)
        summary = (
            out.groupby("cluster")[feat_df.columns]
            .mean(numeric_only=True)
            .reset_index()
            .sort_values("cluster")
        )

        # 7) Build human-readable insights per cluster
        insights = []
        # Choose key business-facing columns if present in summary; otherwise fallback to top numeric cols used
        preferred = [c for c in ["Qty", "Sales", "Cost", "Profit", "Discount"] if c in summary.columns]
        key_cols = preferred if preferred else list(summary.columns[1:])  # exclude 'cluster'

        # Global means across clusters for relative thresholds
        global_means = {c: summary[c].mean() for c in key_cols}

        for _, row in summary.iterrows():
            cid = int(row["cluster"])
            parts = []
            for col in key_cols:
                val = row[col]
                if pd.isna(val):
                    continue
                gm = global_means.get(col, None)
                if gm is None or gm == 0 or pd.isna(gm):
                    parts.append(f"Avg {col}")
                    continue
                if val > gm * 1.2:
                    parts.append(f"High {col}")
                elif val < gm * 0.8:
                    parts.append(f"Low {col}")
                else:
                    parts.append(f"Avg {col}")
            insight_text = ", ".join(parts) if parts else "No major differences"
            insights.append({"cluster": cid, "cluster_insight": insight_text})

        insights_df = pd.DataFrame(insights).sort_values("cluster").reset_index(drop=True)

        # 8) Join insights back to each row in the clustered dataset
        insight_map = dict(zip(insights_df["cluster"], insights_df["cluster_insight"]))
        out["cluster_insight"] = out["cluster"].map(insight_map)

        # 9) Save outputs next to manage.py (cwd)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        clustered_name = f"clustered_{ts}.csv"
        summary_name = f"cluster_summary_{ts}.csv"
        insights_name = f"cluster_insights_{ts}.csv"

        out.to_csv(clustered_name, index=False)
        summary.to_csv(summary_name, index=False)
        insights_df.to_csv(insights_name, index=False)

        # 10) Print short report
        counts = out["cluster"].value_counts().sort_index()
        print("\n====== CLUSTERING REPORT ======")
        print(f"Chosen k: {best_k}")
        print("Counts per cluster:")
        for c, n in counts.items():
            print(f"  - cluster {c}: {n}")

        print("\nOutputs saved:")
        print(f"  - Labeled data (+ insights): {os.path.abspath(clustered_name)}")
        print(f"  - Cluster summary:           {os.path.abspath(summary_name)}")
        print(f"  - Cluster insights:          {os.path.abspath(insights_name)}")

        print("\n✅ Done.")
