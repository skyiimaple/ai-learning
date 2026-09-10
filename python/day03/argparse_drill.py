import argparse
from pathlib import Path


def build_parser():
    p = argparse.ArgumentParser(description="学生成绩统计 CLI")
    p.add_argument(
        "file",
        nargs="?", #可选位置参数
        default="student.csv",
        help="输入学生成绩文件路径(csv或者json)",
    )
    p.add_argument(
        "--pass-line",
        type=int,
        default=60,
        help="及格分数线(默认60)",
    )
    p.add_argument(
        "-o", "--output",
        default="summary.csv",
        help="汇总输出结果"
    )
    return p

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    print(f"文件路径: {Path(args.file)}")
    print(f"及格分数线: {args.pass_line}")
    print(f"汇总输出结果: {args.output}")