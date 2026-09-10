from pathlib import Path

root = Path(__file__).resolve().parent.parent
print("根目录:", root)


day02 = root / "day02"
for p in day02.iterdir():
    print("iterdir:", p.name, "dir?" if p.is_dir() else "file")

print("--- glob *.csv ---")
for p in day02.glob("*.csv"):
    print(p)

print("--- rglob ---")
for p in root.rglob("students.csv"):
    print(p)


def find_score_files(folder: Path):
    files = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)


print("--- day01+day02 成绩文件 ---")
for p in find_score_files(root / "day01") + find_score_files(root / "day02"):
    print(p.suffix, p)
