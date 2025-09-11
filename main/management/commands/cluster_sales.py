import io
import os
import sys
import json
import time
import textwrap
import traceback
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

# Optional imports guarded so the command still loads if not present.
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
except Exception as e:
    KMeans = None
    StandardScaler = None
    silhouette_score = None

def safe_print(msg: str):
    try:
        print(msg)
    except Exception:
        # Fallback for odd terminals
        sys.stdout.write((msg or "") + "\n")
        sys.stdout.flush()

def read_csv_interactive() -> pd.DataFrame:
    """
    Interactive CSV loader with retry if no source is provided.
    """
    safe_print("")
    safe_print("Data Cleaning Program")
    safe_print("==================================================")
    safe_print("1. Browse for local CSV file")
    safe_print("2. Enter file path manually")
    safe_print("3. Enter URL to CSV file")

    while True:
        choice = input("Choose option (1/2/3) or press Enter to browse: ").strip()

        # Default: same as browse (option 1)
        if choice == "" or choice == "1":
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.update()
                file_path = filedialog.askopenfilename(
                    title="Select cleaned CSV",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                root.destroy()

                if file_path:
                    safe_print(f"✔ Selected file: {file_path}")
                    return pd.read_csv(file_path)
                else:
                    safe_print("No file selected.")
            except Exception:
                safe_print("⚠️  Browse dialog not available.")
                # fall through to retry below

        elif choice == "2":
            manual = input("Enter full path to CSV: ").strip().strip('"').strip("'")
            if manual and os.path.exists(manual):
                safe_print(f"✔ Using: {manual}")
                return pd.read_csv(manual)
            else:
                safe_print("Invalid or missing path.")

        elif choice == "3":
            url = input("Paste CSV URL: ").strip()
            if url:
                try:
                    import requests
                    safe_print("⬇️  Downloading CSV...")
                    r = requests.get(url, timeout=60)
                    r.raise_for_status()
                    try:
                        text = r.content.decode("utf-8")
                    except UnicodeDecodeError:
                        text = r.content.decode("latin-1")
                    safe_print("✔ Downloaded CSV from URL.")
                    return pd.read_csv(io.StringIO(text))
                except Exception as e:
                    safe_print(f"Failed to fetch CSV: {e}")
            else:
                safe_print("No URL provided.")

        # Ask if they want to retry
        retry = input("No source provided. Try another method? (y/n): ").strip().lower()
        if retry != "y":
            safe_print("No source provided. Exiting.")
            raise CommandError("No source provided.")

def auto_kmeans_with_silhouette(X_scaled, k_min=2, k_max=8, n_init=10, random_state=42):
    """
    Try k in [k_min, k_max], pick the one with the best silhouette score.
    Returns (best_k, best_model, scores_dict).
    """
    best_k = None
    best_score = -1.0
    best_model = None
    scores = {}

    for k in range(k_min, k_max + 1):
        model = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
        labels = model.fit_predict(X_scaled)
        # Silhouette requires > 1 label and < n_samples unique labels
        if len(set(labels)) <= 1 or len(set(labels)) >= len(labels):
            scores[k] = float("nan")
            continue
        score = silhouette_score(X_scaled, labels)
        scores[k] = float(score)
        if score > best_score:
            best_k = k
            best_score = score
            best_model = model

    if best_model is None:
        # Fallback to k=3
        safe_print("⚠️  Could not compute silhouette reliably; defaulting to k=3.")
        best_model = KMeans(n_clusters=3, n_init=n_init, random_state=42).fit(X_scaled)
        best_k = 3
        scores[3] = float("nan")

    return best_k, best_model, scores

class Command(BaseCommand):
    help = "Interactively load a cleaned CSV (browse/path/URL), run K-Means clustering (descriptive analytics), and save labeled output."

    def handle(self, *args, **options):
        # Dependency checks
        if KMeans is None or StandardScaler is None or silhouette_score is None:
            raise CommandError(
                "scikit-learn is required. Install with:\n  pip install scikit-learn"
            )

        try:
            df = read_csv_interactive()
        except Exception as e:
            raise CommandError(str(e))

        if df.empty:
            raise CommandError("The CSV appears to be empty.")

        # Keep an id/key column if present, to reattach later (optional)
        possible_keys = ["id", "receipt", "so", "item_code"]
        id_cols = [c for c in possible_keys if c in df.columns]

        # 1) Select numeric features
        try:
            feat_df = choose_features(df)
        except Exception as e:
            raise CommandError(str(e))

        # 2) Fill NAs with 0 (simple descriptive analytics assumption)
        feat_df_filled = feat_df.fillna(0)

        # 3) Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feat_df_filled.values)

        # 4) Auto-pick k using silhouette
        safe_print("🔎 Selecting number of clusters (k) using silhouette score...")
        best_k, best_model, scores = auto_kmeans_with_silhouette(X_scaled)
        safe_print(f"✔ Best k: {best_k}")
        safe_print(f"ℹ️  Silhouette scores: {json.dumps(scores, indent=2)}")

        labels = best_model.labels_

        # 5) Attach cluster labels to original df
        out_df = df.copy()
        out_df["cluster"] = labels

        # 6) Produce quick per-cluster summary (means of numeric columns)
        summary = (
            out_df.groupby("cluster")[feat_df.columns]
            .mean(numeric_only=True)
            .reset_index()
            .sort_values("cluster")
        )

        counts = out_df["cluster"].value_counts().sort_index()

        # 7) Save outputs
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"clustered_{ts}.csv"
        summary_name = f"cluster_summary_{ts}.csv"

        out_df.to_csv(out_name, index=False)
        summary.to_csv(summary_name, index=False)

        # 8) Print a readable report
        safe_print("")
        safe_print("====== CLUSTERING REPORT ======")
        safe_print(f"Chosen k: {best_k}")
        safe_print("Counts per cluster:")
        for cl, cnt in counts.items():
            safe_print(f"  - cluster {cl}: {cnt}")

        safe_print("\nCluster-wise feature means (first few columns):")
        # Show up to 8 columns in terminal for readability
        cols_to_show = list(summary.columns[: min(9, len(summary.columns))])
        safe_print(summary[cols_to_show].to_string(index=False))

        safe_print("\nFeature columns used:")
        safe_print(", ".join(feat_df.columns))

        safe_print("\nSilhouette score table:")
        for k in sorted(scores.keys()):
            safe_print(f"  k={k}: {scores[k]}")

        safe_print("\nOutputs saved:")
        safe_print(f"  - Labeled data: {os.path.abspath(out_name)}")
        safe_print(f"  - Cluster summary: {os.path.abspath(summary_name)}")

        # Optional tip if they want to keep specific columns
        if id_cols:
            safe_print(
                "\nTip: You had potential ID columns detected "
                f"({', '.join(id_cols)}). They are included in the labeled output for traceability."
            )

        safe_print("\n✅ Done.")
