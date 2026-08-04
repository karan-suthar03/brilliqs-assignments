"""Generate a CSV to feed the pipeline.

    python scripts/generate_csv.py --rows 1000
    python scripts/generate_csv.py --rows 5000000 --out data/big.csv
    python scripts/generate_csv.py --messy

Standard library only, so it runs anywhere and the same seed always produces
the same file.
"""

import argparse
import csv
import random
from pathlib import Path

FIRST = ["Ann", "Bob", "Priya", "Rahul", "Sara", "Ivan", "Mei", "Omar",
         "Nina", "Karan", "Leila", "Tom", "Aisha", "Diego", "Yuki"]
LAST = ["Patil", "Sharma", "Lowe", "Okafor", "Kim", "Rossi", "Silva",
        "Nakamura", "Haddad", "Fernandes", "Novak", "Chen"]
CITY = ["Pune", "Mumbai", "Bengaluru", "Delhi", "Tokyo", "Berlin",
        "Nairobi", "Lisbon", "Toronto", "Osaka"]
JOB = ["Engineer", "Analyst", "Teacher, early years", "Designer",
       "Data Engineer", "Nurse", "Accountant", "Chef"]

HEADERS = ["id", "first_name", "last_name", "email", "city", "pincode",
           "job", "salary", "joined_on", "notes"]

# Deliberately awkward variants of the same columns, used by --messy.
MESSY_HEADERS = ["ID", "First Name", "LAST-NAME", "e.mail", "City", "Pincode",
                 "Job Title", "Salary", "Joined On", "Notes"]


def row(index: int, rng: random.Random) -> list:
    first = rng.choice(FIRST)
    last = rng.choice(LAST)
    return [
        index,
        first,
        last,
        f"{first.lower()}.{last.lower()}{index}@example.com",
        rng.choice(CITY),
        # Zero-padded on purpose: it is a string, and anything that infers
        # types will quietly turn it into 411.
        f"{rng.randint(1, 99999):05d}",
        rng.choice(JOB),
        rng.randint(300000, 2500000),
        f"20{rng.randint(15, 25)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "" if index % 5 == 0 else "joined via referral",
    ]


def generate(path: Path, rows: int, seed: int, messy: bool) -> Path:
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)

    # utf-8-sig writes the BOM Excel produces, which is exactly what the
    # handler has to cope with.
    encoding = "utf-8-sig" if messy else "utf-8"

    with open(path, "w", newline="", encoding=encoding) as handle:
        writer = csv.writer(handle)
        writer.writerow(MESSY_HEADERS if messy else HEADERS)

        for index in range(1, rows + 1):
            record = row(index, rng)
            if messy:
                if index % 1000 == 0:
                    record[4] = "पुणे"
                if index % 1500 == 0:
                    record.append("unexpected extra field")
            writer.writerow(record)

    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=Path("data/users.csv"))
    parser.add_argument("--seed", type=int, default=42,
                        help="same seed gives the same file")
    parser.add_argument("--messy", action="store_true",
                        help="BOM, spaced headers, non-Latin text, ragged rows")
    args = parser.parse_args()

    path = generate(args.out, args.rows, args.seed, args.messy)
    print(f"{path}  {args.rows:,} rows  {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
