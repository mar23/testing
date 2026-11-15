"""Vypočítá změny ve sloupci value mezi sousedními záznamy CSV."""

import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


def generate_differences(file_path, output_path):
    """Zachová pořadí vstupu; rozdíl = aktuální value - předchozí value."""
    records = []
    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames or not {"id", "value"}.issubset(reader.fieldnames):
            raise ValueError("Vstupní CSV musí obsahovat sloupce id a value.")
        for row_number, row in enumerate(reader, start=2):
            try:
                value = Decimal(row["value"])
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise ValueError(f"Řádek {row_number}: value není platné číslo.") from exc
            if not value.is_finite():
                raise ValueError(f"Řádek {row_number}: value musí být konečné číslo.")
            if not row["id"]:
                raise ValueError(f"Řádek {row_number}: chybí id.")
            records.append((row["id"], value))

    output_path = Path(output_path)
    if Path(file_path).resolve() == output_path.resolve():
        raise ValueError("Výstupní soubor musí být odlišný od vstupního CSV.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["previous_id", "id", "previous_value", "value", "difference"])
        for previous, current in zip(records, records[1:]):
            writer.writerow([previous[0], current[0], previous[1], current[1],
                             current[1] - previous[1]])

    count = max(len(records) - 1, 0)
    print(f"Zpracováno záznamů: {len(records)}")
    print(f"Vygenerováno rozdílů: {count}")
    if records:
        print(f"Rozdíl poslední − první hodnota: {records[-1][1] - records[0][1]}")
    print(f"Výstupní CSV: {output_path}")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="../datasets/benchmark_dataset.csv",
                        help="Vstupní CSV se sloupci id,value.")
    parser.add_argument("--output", default="output/differences.csv",
                        help="Cesta k výstupnímu CSV (výchozí: output/differences.csv).")
    args = parser.parse_args()
    try:
        generate_differences(args.input, args.output)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Chyba: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
