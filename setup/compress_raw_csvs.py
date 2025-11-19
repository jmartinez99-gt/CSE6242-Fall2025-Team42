from pathlib import Path
import gzip
import shutil

ROOT_DIR = Path("../data/raw")
MAX_SIZE_BYTES = 50 * 1024 * 1024       # 50 MB

for csv_path in ROOT_DIR.rglob("*.csv"):
    # Skip files that are already compressed
    if csv_path.suffix == ".gz":
        continue

    gz_path = csv_path.with_suffix(csv_path.suffix + ".gz")

    # Skip recompressing if .gz already exists
    if gz_path.exists():
        print(f"Skip (already compressed): {gz_path}")
        continue

    orig_size = csv_path.stat().st_size
    orig_mb = orig_size / (1024**2)

    # if orig_size <= MAX_SIZE_BYTES:
    #     print(f"Skip (small enough): {csv_path} ({orig_mb:.2f} MB)")
    #     continue

    print(f"Compressing {csv_path} ({orig_mb:.2f} MB) -> {gz_path}")

    with csv_path.open("rb") as f_in, gzip.open(gz_path, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)

    comp_size = gz_path.stat().st_size
    comp_mb = comp_size / (1024**2)

    print(f"  Done. Compressed size: {comp_mb:.2f} MB "
          f"(saved {(orig_mb - comp_mb):.2f} MB)")