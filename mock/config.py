import codecs
import json
import os
from typing import List
from flask import Response, abort


CONFIG = 'conf.json'

current_dir = os.path.dirname(__file__)
data_dir = os.path.abspath(os.path.join(current_dir, '..'))

'''
config 实例
'''
current_conf = None


class Filter:

    def __init__(self):
        self._dir = None
        self.method = 'GET'
        self.contents = []
        self.code = 200
        self.response = None

    @classmethod
    def from_json_obj(cls, obj):
        _filter = cls()
        for attr_name in _filter.__dict__:
            if attr_name in obj:
                setattr(_filter, attr_name, obj[attr_name])
        return _filter

    def make_response(self):
        resp_dir = os.path.join(self._dir, self.response)
        contents = os.listdir(resp_dir)
        resp_body_file = None
        if 'response_data.json' in contents:
            resp_body_file = os.path.join(resp_dir, 'response_data.json')
        elif 'response_data.bin' in contents:
            resp_body_file = os.path.join(resp_dir, 'response_data.bin')
        else:
            return abort(404, 'resp data not found')
        f = codecs.open(os.path.join(resp_dir, resp_body_file), 'r', 'utf-8')
        res = Response(f.read(), self.code)
        f.close()
        return res


class Config:
    """
    数据配置文件

    格式：
    parent	 	        （可选） 过滤器父配置文件，配置此属性后，过滤器无匹配内容时将继续检查父过滤器的内容。
    filters	 	 	            过滤器数组，内含多组过滤器。此处配置会覆盖父过滤器内容。

         filter{
            contents	 	    全匹配或者正则匹配，触发后继续验证path相关过滤规则。如果path未配置规则，则按照当前匹配情况触发过滤机制。
            response	 	    mock返回文件中的内容。返回json文件等内容，此属性中指定的是json文件路径
            code	    （可选）	mock返回指定http_status_code。指定mock触发后返回的http code
            }

    """
    def __init__(self):
        self.filename = None
        self.parent = None
        self.filters: List[Filter] = []

    @classmethod
    def from_conf_name(cls, conf_name):
        return cls.from_conf_file(os.path.join(data_dir, f'{conf_name}/{CONFIG}'))

    @classmethod
    def from_conf_file(cls, conf_file):
        if not os.path.exists(conf_file):
            raise FileNotFoundError('%s ,conf file not found!' % str(conf_file))

        conf = cls()
        # 保存data目录下的相对路径
        conf.filename = conf_file[len(data_dir)+1:-(len(CONFIG)+1)]

        f = codecs.open(conf_file, 'r', 'utf-8')
        conf_json_obj = json.loads(f.read())
        f.close()

        if 'parent' in conf_json_obj:
            parent_name = conf_json_obj['parent']
            if parent_name:
                conf.parent = Config.from_conf_name(parent_name)

        if 'filters' not in conf_json_obj:
            raise SyntaxError('Can\'t found any filter in conf. %s' % str(conf_file))

        for filter_obj in conf_json_obj['filters']:
            filter_ = Filter.from_json_obj(filter_obj)
            filter_._dir = os.path.dirname(conf_file)
            conf.filters.append(filter_)

        return conf

    def to_string(self):
        conf_json_obj = {}
        if self.parent:
            conf_json_obj['parent'] = self.parent.filename
        conf_json_obj['filters'] = []
        for f in self.filters:
            # 生成filter信息，去掉'_'开头的属性
            conf_json_obj['filters'].append({k: f.__dict__[k] for k in f.__dict__ if not k.startswith('_')})
        return json.dumps(conf_json_obj, ensure_ascii=False, indent=4)

    def save(self, filename):
        f = codecs.open(filename, 'w', 'utf-8')
        f.write(self.to_string())
        f.close()
