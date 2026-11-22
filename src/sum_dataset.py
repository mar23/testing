"""Vypočítá změny ve sloupci value mezi sousedními záznamy CSV a statistiku hodnot."""

import argparse
import csv
import statistics
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path



def read_records(file_path):
    """Načte dvojice (id, value) ze vstupního CSV v pořadí souboru."""
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
    return records


def generate_differences(file_path, output_path):
    """Zachová pořadí vstupu; rozdíl = aktuální value - předchozí value."""
    records = read_records(file_path)
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


def describe_values(file_path, output_path):
    """Nová funkce: souhrnná statistika sloupce value včetně největšího růstu a poklesu."""
    records = read_records(file_path)
    if not records:
        raise ValueError("Vstupní CSV neobsahuje žádné záznamy.")
    values = [value for _, value in records]
    low = min(records, key=lambda record: record[1])
    high = max(records, key=lambda record: record[1])
    steps = [(current[0], current[1] - previous[1]) for previous, current in zip(records, records[1:])]
    # Jen sum/len a Decimal.sqrt: funguje i se starším python3 na výpočetních uzlech (bez statistics.fmean).
    mean = sum(values) / len(values)
    deviation = (sum((value - mean) ** 4 for value in values) / len(values)).sqrt()
    rows = [
        ("pocet_zaznamu", len(values), ""),
        ("soucet", sum(values), ""),
        ("prumer", round(mean, 3), ""),
        ("median", statistics.median(values), ""),
        ("smerodatna_odchylka", round(deviation, 3), ""),
        ("minimum", low[1], low[0]),
        ("maximum", high[1], high[0]),
    ]
    if steps:
        rise = max(steps, key=lambda step: step[1])
        fall = min(steps, key=lambda step: step[1])
        rows += [("nejvetsi_rust", rise[1], rise[0]), ("nejvetsi_pokles", fall[1], fall[0])]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["metrika", "hodnota", "id"])
        writer.writerows(rows)

    print("Statistika value:")
    for name, value, record_id in rows:
        print(f"  {name}: {value}" + (f" (id {record_id})" if record_id else ""))
    print(f"Statistika CSV: {output_path}")
    return dict((name, value) for name, value, _ in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="../datasets/benchmark_dataset.csv",
                        help="Vstupní CSV se sloupci id,value.")
    parser.add_argument("--output", default="output/differences.csv",
                        help="Cesta k výstupnímu CSV (výchozí: output/differences.csv).")
    parser.add_argument("--stats-output", default=None,
                        help="Cesta ke statistice (výchozí: statistics.csv vedle --output).")
    args = parser.parse_args()
    stats_output = args.stats_output or Path(args.output).with_name("statistics.csv")
    try:
        generate_differences(args.input, args.output)
        describe_values(args.input, stats_output)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Chyba: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
