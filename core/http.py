
from copy import deepcopy

from fastapi.responses import JSONResponse


class ErrorCode:

    success = {'code': 0, 'status': 0, 'msg': 'success', 'http_status': 200}
    param_error = {'code': 1001, 'status': 1, 'msg': 'param error', 'http_status': 400}
    internal_error = {'code': 1002, 'status': 1, 'msg': 'internal error', 'http_status': 500}

    class User:

        account_not_exist = {'code': 21001, 'status': 1, 'msg': '账户不存在', 'http_status': 400}
        password_error = {'code': 21002, 'status': 1, 'msg': '密码错误', 'http_status': 400}
        account_exist = {'code': 21003, 'status': 1, 'msg': '账户已存在', 'http_status': 400}


def get_common_response(
        error_code: dict,
        data: dict = None,
        extra: dict = None
):
    """
    get_common_response
    :return:
    """
    ec = deepcopy(error_code)
    ec['data'] = data
    if extra:
        ec.update(extra)
    http_status = ec.pop('http_status')
    return JSONResponse(ec, status_code=http_status)
