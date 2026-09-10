import argparse
import sys
from pathlib import Path

# day03 脚本用扁平 import（from stats_core），把该目录加入 path
DAY03 = Path(__file__).resolve().parent.parent / "day03"
if str(DAY03) not in sys.path:
    sys.path.insert(0, str(DAY03))

from errors import AppError  # noqa: E402
from io_load import load_students  # noqa: E402
from stats_core import summarize  # noqa: E402


def build_parser():
    p = argparse.ArgumentParser(description="统计某个文件夹下所有文件")
    p.add_argument("dir", nargs="?", default="data", help="统计的目录")
    p.add_argument("--pass_line", type=int, default=60, help="及格线")
    p.add_argument("--output", type=Path, default="summary.json", help="输出文件")
    p.add_argument(
        "--merge",
        action="store_true",
        help="合并所有文件后再统计（默认每个文件夹统计一次）",
    )
    return p


def find_score_files(folder: Path):
    files = []
    for pat in ("*.csv", "*.json"):
        files.extend(folder.glob(pat))
    return sorted(files)


def main(argv=None):
    """
    统计某个文件夹下所有文件
    """
    args = build_parser().parse_args(argv)
    folder = Path(args.dir)
    if not folder.is_dir():
        print(f"目录不存在: {folder}", file=sys.stderr)
        return 1

    files = find_score_files(folder)
    if not files:
        print(f"没有找到*.json或*.csv的成绩文件「{folder}」", file=sys.stderr)
        return 1

    try:
        # 根据合并参数决定是否合并统计
        if args.merge:
            # 合并所有文件后再统计
            all_students = []
            for file in files:
                students = load_students(file)
                all_students.extend(students)
            result = summarize(all_students, args.pass_line)
            print(
                f"[{file.name}] 人数={result['count']} 平均={result['avg']} 最高={result['top_name']}"
            )
        else:
            # 单独统计每个文件夹
            for file in files:
                students = load_students(file)
                result = summarize(students, args.pass_line)
                print(
                    f"[{file.name}] 人数={result['count']} 平均={result['avg']} 最高={result['top_name']}"
                )
    except AppError as e:
        print(f"业务错误: {e}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
