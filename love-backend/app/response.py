def success_response(data=None, message="操作成功"):
    return {"code": 200, "message": message, "data": data}


def error_response(code=400, message="操作失败"):
    return {"code": code, "message": message, "data": None}
