"""自定义异常模块"""


class AppException(Exception):
    """业务异常，统一返回格式 {"code", "message", "data"}"""

    def __init__(self, code: int = 400, message: str = "操作失败"):
        self.code = code
        self.message = message
