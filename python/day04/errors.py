class AppError(Exception):
    """业务可预期错误的基类（给用户看的）"""


class FileFormatError(AppError):
    """扩展名不支持 / 内容格式不对"""


class ScoreParseError(AppError):
    """分数无法转成 int"""


class InputNotFoundError(AppError):
    """输入路径不存在"""
