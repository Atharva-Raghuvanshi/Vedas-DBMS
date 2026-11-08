"""Download the Hugging Face dataset siddharthjadhav6565/vedas to data/raw/
and print 20 sample rows so the format can be inspected before loading.

Uses only the Python standard library (urllib) - no new dependencies.

Run:  ./venv/Scripts/python.exe scripts/download_dataset.py
"""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from veda_parser import parse, validate

URL = ("https://huggingface.co/datasets/siddharthjadhav6565/vedas/"
       "resolve/main/veda.txt")
RAW = Path(__file__).resolve().parent.parent / "data" / "raw" / "veda.txt"


def main():
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists() and RAW.stat().st_size > 0:
        print(f"already downloaded: {RAW} ({RAW.stat().st_size:,} bytes)")
    else:
        print(f"downloading {URL} ...")
        urllib.request.urlretrieve(URL, RAW)
        print(f"saved {RAW.stat().st_size:,} bytes to {RAW}")

    records = parse(RAW)
    print(f"\nparsed {len(records)} mantras from the full file")
    problems = validate(records)
    print(f"verse-number gaps detected: {problems}")

    print("\n20 sample rows (first 10 and last 10):")
    sample = records[:10] + records[-10:]
    for r in sample:
        print(f"  {r['mandala']}.{r['hymn']}.{r['verse']:>2}  "
              f"{r['deity'][:18]:18} {r['rishi'][:28]:28} "
              f"{r['text'][:52]}...")


if __name__ == "__main__":
    main()
