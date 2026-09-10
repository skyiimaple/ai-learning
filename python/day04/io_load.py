import sys
from pathlib import Path

from errors import AppError, FileFormatError, InputNotFoundError, ScoreParseError

# day03 用扁平 import，把 day03 目录加入 path
DAY03 = Path(__file__).resolve().parent.parent / "day03"
if str(DAY03) not in sys.path:
    sys.path.insert(0, str(DAY03))
from loaders import load_students as _load_students  # noqa: E402


def load_students(path: Path):
    path = Path(path)
    if not path.exists():
        raise InputNotFoundError(f"找不到: {path}")
    try:
        return _load_students(path)
    except FileNotFoundError as e:
        raise InputNotFoundError(str(e)) from e
    except ValueError as e:
        # Day03 里分数/类型问题多是 ValueError
        msg = str(e)
        if "不支持的文件类型" in msg:
            raise FileFormatError(msg) from e
        if "分数不是整数" in msg:
            raise ScoreParseError(msg) from e
        raise AppError(msg) from e


