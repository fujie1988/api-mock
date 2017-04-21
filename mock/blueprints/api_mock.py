from flask import Blueprint, request, abort, Response, stream_with_context
from mock import context
from mock.config import Filter
from mock import path_helper
import codecs
import requests
import os
import json
import logging
import genson
import traceback


api_mock = Blueprint('mock', __name__, url_prefix='/mock')

'''
记录的id，用于防止记录数据重名
'''
record_id = 0

logger = logging.getLogger('api_mock')


@api_mock.route('/')
@api_mock.route('/<path:path>', methods=['GET', 'POST'])
def index(path=''):
    if context.application.mode == context.MOCK_MODE:
        return mock_request()
    elif context.application.mode == context.RECORD_MODE:
        return record_request()
    else:
        return abort(404)


def _check_filter(url, filter_):
    for content in filter_.contents:
        if content not in url:
            return False
    return True


def mock_request():
    url = request.url
    conf = context.application.conf
    for filter_ in conf.filters:
        if _check_filter(url, filter_):
            return filter_.make_response()
    # parent's filters
    # 暂时不支持递归
    if conf.parent:
        for filter_ in conf.parent.filters:
            if _check_filter(url, filter_):
                return filter_.make_response()
    return abort(404)


def record_request():
    url = request.scheme + '://' + request.url[len('http://localhost/mock/'):]
    method = request.method
    data = request.get_data() or request.form or None
    headers = dict()
    for name, value in request.headers:
        if not value or name == 'Cache-Control' or name == 'Host':
            continue
        headers[name] = value
    r = requests.request(method, url, headers=headers, data=data, cookies=request.cookies, stream=True, verify=False)
    resp_headers = []
    for name, value in r.headers.items():
        if name.lower() in ('content-length',
                            'connection',
                            'content-encoding',
                            'transfer-encoding'):
            continue
        resp_headers.append((name, value))
    try:
        dir_name = save_record(method, url, headers, data, r.status_code, resp_headers, r.content)
        add_filter_from_record(method, url, r.status_code, dir_name)
    except Exception:
        logger.error('Save record filed')
        traceback.print_exc()
    return Response(r, status=r.status_code, headers=resp_headers)


def save_record(method, url, headers, data, resp_code, resp_headers, resp_data):
    global record_id
    record_id += 1
    host_and_path = url[url.find('://')+3:url.find('?')]
    dir_name = str(record_id) + '.' + host_and_path[host_and_path.find('/')+1:].replace('/', '.')
    dir_path = os.path.join(path_helper.RECORD, dir_name)
    os.mkdir(dir_path)

    # 保存请求url及header
    request_info = {
        'url': url,
        'headers': headers,
        'method': method
    }
    req_file = codecs.open(os.path.join(dir_path, 'request.json'), 'w', 'utf-8')
    req_file.write(json.dumps(request_info, indent=4, ensure_ascii=False))
    req_file.close()

    # 保存请求body
    if data:
        if 'Content-Type' in headers and headers['Content-Type'].find('json') > 0:
            req_data_file = codecs.open(os.path.join(dir_path, 'request_data.json'), 'w', 'utf-8')
            req_data_file.write(json.dumps(json.loads(data.decode()), indent=4, ensure_ascii=False))
            req_data_file.close()
        else:
            req_data_file = codecs.open(os.path.join(dir_path, 'request_data.bin'), 'wb')
            req_data_file.write(data)
            req_data_file.close()

    # 保存响应code及header
    response_info = {
        'code': resp_code,
        'headers': resp_headers
    }

    resp_file = codecs.open(os.path.join(dir_path, 'response.json'), 'w', 'utf-8')
    resp_file.write(json.dumps(response_info, indent=4, ensure_ascii=False))
    resp_file.close()

    # 保存响应body
    if resp_data:
        resp_h_dict = dict(resp_headers)
        if 'Content-Type' in resp_h_dict and resp_h_dict['Content-Type'].find('json') > 0:
            resp_data_file_path = os.path.join(dir_path, 'response_data.json')
            resp_data_file = codecs.open(resp_data_file_path, 'w', 'utf-8')
            resp_data_file.write(json.dumps(json.loads(resp_data.decode()), indent=4, ensure_ascii=False))
            resp_data_file.close()
            create_json_schema(resp_data_file_path)
        else:
            resp_data_file = codecs.open(os.path.join(dir_path, 'response_data.bin'), 'wb')
            resp_data_file.write(resp_data)
            resp_data_file.close()

    return dir_name


def create_json_schema(response_json_file_path):
    json_obj = json.loads(codecs.open(response_json_file_path, 'r', 'utf-8').read())
    schema = genson.Schema()
    schema.add_object(json_obj)
    schema_file_path = os.path.join(os.path.dirname(response_json_file_path), 'schema.json')
    schema_file = codecs.open(schema_file_path, 'w', 'utf-8')
    schema_file.write(schema.to_json(ensure_ascii=False, indent=4))
    schema_file.close()


def add_filter_from_record(method, url, resp_code, response_record_name):
    filter_ = Filter()
    filter_.method = method
    filter_.contents.append(url)
    filter_.code = resp_code
    filter_.response = response_record_name
    context.application.conf.filters.append(filter_)
