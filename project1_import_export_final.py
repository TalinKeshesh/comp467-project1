"""
Project 1: Baselight -> Xytech import/export

Behavior:
- Aggregates frames per corrected facility folder across the whole Baselight export
  (folders printed ONCE, ranges computed globally per folder).
- Does NOT sort folders alphabetically (preserves first-seen order).
- CSV output: Header Path,Frames,Mark and ONE ROW PER segment (range or single frame).

Extra Credit (EC):
- After the CSV is made, you (the student) may type X's into the 3rd column (Mark).
- IMPORTANT: Don't put X's into the file that gets overwritten.
  This script writes:  project1_output.csv
  For EC, it reads:    project1_output_marked.csv  (if it exists)
  So your workflow is:
    1) Run script once -> project1_output.csv created
    2) Copy it -> project1_output_marked.csv
    3) Add X's in the 3rd column of project1_output_marked.csv
    4) Run script again -> it will print X rows from the marked file

Inputs expected in the same folder as this script:
  - Baselight_export_spring2026.txt
  - Xytech_spring2026.txt

Outputs:
  - project1_output.csv
"""

from pathlib import Path
import csv
import re

XYTECH_FILE = Path("Xytech_spring2026.txt")
BASELIGHT_FILE = Path("Baselight_export_spring2026.txt")

OUT_CSV = Path("project1_output.csv")
MARKED_CSV = Path("project1_output_marked.csv")  # <-- EC file you edit


def parse_xytech_locations(path: Path) -> list[str]:
    locations = []
    in_locations = False

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.lower().startswith("location"):
            in_locations = True
            continue

        if in_locations:
            if line.lower().startswith("notes"):
                break
            if line.startswith("/"):
                locations.append(line)

    return locations


def baselight_subpath(baselight_folder: str) -> str:
    parts = baselight_folder.strip().split("/")
    # ['', 'baselightfilesystem1', 'SuperMarioBros', ...]
    if len(parts) >= 3 and parts[1].startswith("baselightfilesystem"):
        return "/" + "/".join(parts[2:])
    return "/" + "/".join(parts[1:])


def map_to_xytech(baselight_folder: str, xy_locations: list[str]) -> str | None:
    """Strict suffix match only."""
    sub = baselight_subpath(baselight_folder)
    for loc in xy_locations:
        if loc.endswith(sub):
            return loc
    return None


def parse_baselight_line(line: str) -> tuple[str, list[int]]:
    tokens = line.split()
    folder = tokens[0]
    frames: list[int] = []

    for tok in tokens[1:]:
        if tok.isdigit():
            frames.append(int(tok))
        else:
            m = re.match(r"(\d+)", tok)
            if m:
                frames.append(int(m.group(1)))

    return folder, frames


def frames_to_segments(frames: list[int]) -> tuple[list[str], int, int]:
    frames = sorted(set(frames))
    segments: list[str] = []
    singles = 0
    ranges = 0

    if not frames:
        return segments, singles, ranges

    start = prev = frames[0]

    for f in frames[1:]:
        if f == prev + 1:
            prev = f
        else:
            if start == prev:
                segments.append(str(start))
                singles += 1
            else:
                segments.append(f"{start}-{prev}")
                ranges += 1
            start = prev = f

    # flush last segment
    if start == prev:
        segments.append(str(start))
        singles += 1
    else:
        segments.append(f"{start}-{prev}")
        ranges += 1

    return segments, singles, ranges


def print_rows_with_x_third_col(csv_path: Path) -> None:
    """
    Extra Credit:
    Print rows where the 3rd column (Mark) is exactly 'X'.
    """
    if not csv_path.exists():
        print(f"\n(EC) Marked file not found: {csv_path}")
        print("(EC) Create it by copying: cp project1_output.csv project1_output_marked.csv")
        return

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        print("\n--- Rows where 3rd column is 'X' (Extra Credit) ---")
        print("HEADER:", header)

        found = False
        for line_no, row in enumerate(reader, start=2):  # header is line 1
            if len(row) >= 3 and row[2].strip().upper() == "X":
                print(f"Line {line_no}: {row}")
                found = True

        if not found:
            print("(No X rows found)")


def main() -> None:
    xy_locations = parse_xytech_locations(XYTECH_FILE)

    baselight_lines_read = 0
    csv_rows_written = 0

    # Aggregate frames per corrected folder (preserve first-seen order)
    frames_by_folder: dict[str, list[int]] = {}
    folder_order: list[str] = []

    for raw in BASELIGHT_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        baselight_lines_read += 1

        b_folder, frames = parse_baselight_line(line)
        corrected = map_to_xytech(b_folder, xy_locations)
        out_folder = corrected if corrected else f"X {b_folder}"

        if out_folder not in frames_by_folder:
            frames_by_folder[out_folder] = []
            folder_order.append(out_folder)

        frames_by_folder[out_folder].extend(frames)

    # Write CSV + print per folder
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Path", "Frames", "Mark"])  # <- Mark column included (blank by default)

        for folder in folder_order:
            segments, ind_ct, range_ct = frames_to_segments(frames_by_folder[folder])
            print(f"{folder} Individual: {ind_ct} Ranges: {range_ct}")

            for seg in segments:
                writer.writerow([folder, seg, ""])  # <- blank Mark column
                csv_rows_written += 1

    print(f"\nBaselight lines read: {baselight_lines_read}")
    print(f"CSV data rows written (excluding header): {csv_rows_written}")

    # EC: read the *marked* file so your X's don't get overwritten
    print_rows_with_x_third_col(MARKED_CSV)


if __name__ == "__main__":
    main()
