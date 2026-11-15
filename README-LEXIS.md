# Benchmark na IT4I / LEXIS (přes rozšíření LEXIS ve VS Code)

Vše se dělá rozšířením **LEXIS Platform** (VS Code) a jeho CLI `lexis`
(`~/.vscode/extensions/lexis-platform.lexis-platform-<verze>/bin/lexis`).
Přihlášení drží CLI, takže jedno přihlášení platí pro VS Code, terminál i AI agenty.

## Co je v LEXIS vytvořeno

| Co | Hodnota |
|---|---|
| Projekt | `testproject` (vybraný pro tuto složku) |
| Výpočetní zdroj | `ATR-26-1`, Karolina, partition `qcpu_exp` (max. 1 h, 128 jader/uzel) |
| Úložiště | `iRODS IT4I / ATR-26-1` |
| Vstupní dataset | „Benchmark input“ `1155d39a-e142-11f1-889f-421fe4d7e0dd` (obsahuje `benchmark_dataset.csv`) |
| Jobscript dataset | „benchmark_sum jobscript“ `16950574-e142-11f1-8c76-421fe4d7e0dd` (`run_sum.sh`) |
| Workflow | `testproject_benchmark_sum` (šablona JobScript, `fileName=run_sum.sh`, walltime 600 s) |
| Výstup | složka `output` jobu → dataset „Benchmark sum results“ (přístup project) |

Definice workflow je v [.lexis/jobscripts/benchmark_sum.json](.lexis/jobscripts/benchmark_sum.json)
(formát `lexis jobscript create --from`).

Ověřeno během `cli-testproject-20261115T221636868` (15. 11. 2026): stav succeeded,
výstupní dataset `6ae51772-e142-11f1-b2d3-421fe4d7e0dd` obsahuje `result.txt`
(200 čísel, součet 57568.0) a `commit.txt` (`ae4f9b3…`).

## Výběr projektu

- VS Code: LEXIS view → první řádek **Switch Project…** (nebo položka LEXIS ve stavovém řádku).
- Terminál: `lexis project list`, pak `lexis project use <shortname>` (platí pro složku).
- Zda má projekt výpočetní čas a kde: `lexis project placements <shortname>`
  (cluster, partition, zdroj a povolené šablony – potřebujete `JobScript`)
  a `lexis project storages <shortname>` pro úložiště.
- Projekt bez výpočetního zdroje: **Request Computing Resources…** (pravé tlačítko na projekt),
  do cizího projektu **Request Access to a Project…**.

## Spuštění znovu

- VS Code: LEXIS view → projekt → Workflows → `testproject_benchmark_sum` → **Run Workflow…**.
  Výsledek: pravé tlačítko na běh → **Download Output Dataset of Run…**; logy **Show Logs of Run**.
- Terminál:

```bash
lexis workflow run testproject_benchmark_sum --project testproject
lexis watch testproject_benchmark_sum/<run-id>
lexis logs testproject_benchmark_sum/<run-id>
lexis run datasets testproject_benchmark_sum/<run-id>
lexis dataset download <id-vystupniho-datasetu>
```

Změna `run_sum.sh`: nahrát znovu jako dataset typu `jobscript`
(`lexis dataset upload run_sum.sh --project testproject --storage "iRODS IT4I/ATR-26-1" --type jobscript`),
přepsat `script.id` v JSON a vytvořit workflow znovu (`lexis jobscript create --from …`),
nebo ve VS Code pravým tlačítkem na skript → **Create Job Script Workflow…**.

## Co dělá run_sum.sh

- Najde `benchmark_dataset.csv` – LEXIS staguje vstupní dataset do `input/<název datasetu>/`.
- Naklonuje https://github.com/mar23/testing.git, pevný commit
  `ae4f9b326353159cf78612e5ace9b20ba242f455` (pro nejnovější kód nastavit `REPO_REVISION=main`).
- Připraví `../datasets/benchmark_dataset.csv`, kterou veřejný `src/sum_dataset.py` očekává, a spustí ho.
- Do `output/` uloží `result.txt` a `commit.txt`; job skončí chybou, když Python nevypíše „Celkový součet:“
  (veřejný skript při chybě vrací exit status 0).
- Uzel potřebuje `git`, `python3` a HTTPS přístup na GitHub.

Součet zahrnuje VŠECHNA čísla v CSV včetně sloupce id: 200 čísel, součet 57568.0
(jen sloupec value = 52518).
