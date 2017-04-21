from mock.config import Config
from mock import context
from flask import Response, Blueprint, request, jsonify

"""
实现控制API
"""

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/conf', methods=['GET', 'POST'])
def conf():
    """
    设置当前生效的mock数据组

    """
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'conf' in data:
            context.application.conf = Config.from_conf_name(data['conf'])
            return context.make_ok_response()
    elif request.method == 'GET':
        return Response(context.application.conf.to_string(), content_type='application/json')


@api.route('/requests')
def requests():
    req_list = []
    for _ in range(20):
      req_list.append({
        "url": "http://some.req/path",
        "code": 200,
        "resp_body": "resp-body"
      })
    return jsonify(req_list)
