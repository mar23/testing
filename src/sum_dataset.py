import csv
import re

def sum_all_numbers_in_csv(file_path):
    total_sum = 0.0
    count = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row_idx, row in enumerate(reader, 1):
                for col_idx, cell in enumerate(row):
                    # Hledání čísel (celých i desetických) v textu buňky
                    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", cell)
                    for num in numbers:
                        try:
                            total_sum += float(num)
                            count += 1
                        except ValueError:
                            continue
                            
        print(f"Zpracováno celkem {count} čísel.")
        print(f"Celkový součet: {total_sum}")
        return total_sum

    except FileNotFoundError:
        print(f"Chyba: Soubor {file_path} nebyl nalezen. Nezapomeňte jej nejprve stáhnout z LEXIS.")
        return None
    except Exception as e:
        print(f"Došlo k chybě při zpracování: {e}")
        return None

if __name__ == "__main__":
    # Cesta k souboru v relativní cestě z src/ do datasets/
    DATASET_FILE = "../datasets/benchmark_dataset.csv"
    sum_all_numbers_in_csv(DATASET_FILE)
