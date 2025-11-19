from pathlib import Path
import gzip
import shutil

ROOT_DIR = Path("../data/tableau")

# Take a snapshot of files *before* we start so we don't re-process
csv_files = list(ROOT_DIR.rglob("*.csv"))
gz_files  = list(ROOT_DIR.rglob("*.csv.gz"))

print("=== Decompressing existing .csv.gz files ===")
for gz_path in gz_files:
    # .csv.gz -> .csv
    csv_path = gz_path.with_suffix("")  # removes only .gz

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

print("\n=== Compressing existing .csv files ===")
for csv_path in csv_files:
    # For safety, ignore any that were actually .csv.gz originally
    # (rglob('*.csv') doesn't match *.csv.gz, so this is just extra clarity)
    if csv_path.suffix != ".csv":
        continue

    gz_path = csv_path.with_suffix(csv_path.suffix + ".gz")  # .csv.gz

    if gz_path.exists():
        print(f"Skip (already compressed): {gz_path}")
        continue

    orig_size = csv_path.stat().st_size
    orig_mb = orig_size / (1024**2)

    print(f"Compressing {csv_path} ({orig_mb:.2f} MB) -> {gz_path}")

    with csv_path.open("rb") as f_in, gzip.open(gz_path, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

    comp_size = gz_path.stat().st_size
    comp_mb = comp_size / (1024**2)

    print(f"  Done. Compressed size: {comp_mb:.2f} MB "
          f"(saved {(orig_mb - comp_mb):.2f} MB)")
