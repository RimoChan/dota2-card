import json
import random
import logging
import azure.functions as func

from .handler import 召唤


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        参数表 = 提取参数(req)
        return func.HttpResponse(
            召唤(**参数表),
            mimetype='image/svg+xml',
            headers={'Cache-Control': f'max-age=3600'},
        )
    except Exception as e:
        logging.exception(e)
        return response(f'运行错误: {repr(e)}', status_code=422)


def response(x, status_code=200):
    新x = json.dumps(x, ensure_ascii=False)
    return func.HttpResponse(新x, status_code=status_code)


def 提取参数(req: func.HttpRequest) -> dict:
    参数表 = dict(req.params)
    try:
        req_body = req.get_json()
    except ValueError:
        for i, x in req.form.items():
            参数表[i] = json.loads(x)
    else:
        参数表.update(req_body)
    参数表.pop('code', '')
    参数表.pop('clientId', '')
    return 参数表
