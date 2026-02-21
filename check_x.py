import csv

FILENAME = "project1_output_marked.csv"

with open(FILENAME, newline="", encoding="utf-8") as f:
    r = csv.reader(f)
    header = next(r, None)

    print("--- Rows where 3rd column is X ---")
    print("HEADER:", header)

    found = False
    for i, row in enumerate(r, start=2):
        if len(row) >= 3 and row[2].strip().upper() == "X":
            print(f"Line {i}: {row}")
            found = True

    if not found:
        print("(No X rows found)")
