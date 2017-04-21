from mitmproxy import controller, options, master
from mitmproxy import addons
from mitmproxy.proxy import ProxyServer, ProxyConfig
from mitmproxy.http import HTTPFlow, HTTPResponse
import os
import json
import codecs
import socket
import logging


logger = logging.getLogger()


class MyMaster(master.Master):

    def __init__(self, opts, server):
        super().__init__(opts, server)
        self.conf = None
        self.addons.add(*addons.default_addons())

    def run(self, conf=None):
        if conf and os.path.exists(conf):
            self.conf = json.loads(codecs.open(conf).read())
            print(f'Read conf from {conf}\n')
        else:
            print('* Not load any config\n')
        try:
            print(f'MockServerLab start on {get_ip()}:8080\n\n请在被测设备上设置代理服务器地址')
            master.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()
        print('\n\nMockServer shutdown\n')

    @controller.handler
    def request(self, f: HTTPFlow):
        print("[PROXY] Request", f.request.url)
        if not self.conf:
            return
        if 'hosts' not in self.conf:
            return
        for h in self.conf['hosts']:
            if h in f.request.host:
                f.request.host = 'localhost'
                f.request.scheme = 'http'
                f.request.port = 9090
                f.request.path = '/mock/' + h + f.request.path
                print('redirect', f.request.url)
                break

    @controller.handler
    def response(self, f):
        # print("response", f)
        pass

    @controller.handler
    def error(self, f):
        print("error", f)

    @controller.handler
    def log(self, l):
        # print("log", l.msg)
        pass


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    return s.getsockname()[0]


def start(conf=None):
    ca_dir = os.path.expanduser(options.CA_DIR)
    if not os.path.exists(ca_dir):
        os.mkdir(ca_dir)
    '''
    此处增加 ssl_insecure=True, add_upstream_certs_to_client_chain=True
    因为测试环境下某个https是自己签名的,默认会验证失败。
    因此关闭服务端证书校验
    '''
    opts = options.Options(ssl_insecure=True, add_upstream_certs_to_client_chain=True)
    config = ProxyConfig(opts)
    server = ProxyServer(config)
    m = MyMaster(opts, server)
    m.run(conf)

