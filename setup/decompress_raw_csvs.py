from pathlib import Path
import gzip
import shutil

ROOT_DIR = Path("../data/raw")

for gz_path in ROOT_DIR.rglob("*.csv.gz"):
    # Target decompressed file
    csv_path = gz_path.with_suffix("")  # removes only the last suffix, so .csv.gz -> .csv

    # Skip if the .csv already exists
    if csv_path.exists():
        print(f"Skip (already decompressed): {csv_path}")
        continue

    comp_size = gz_path.stat().st_size
    comp_mb = comp_size / (1024**2)

    print(f"Decompressing {gz_path} ({comp_mb:.2f} MB) -> {csv_path}")

    with gzip.open(gz_path, "rb") as f_in, csv_path.open("wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    new_size = csv_path.stat().st_size
    new_mb = new_size / (1024**2)

    print(f"  Done. Decompressed size: {new_mb:.2f} MB "
          f"(expanded {(new_mb - comp_mb):.2f} MB)")