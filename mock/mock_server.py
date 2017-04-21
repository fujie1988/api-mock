import logging
import socket
from threading import Thread

from flask import Flask, request, abort, redirect, url_for
from flask_cors import CORS
from werkzeug.serving import ThreadedWSGIServer

from mock.blueprints.api import api
from mock.blueprints.api_mock import api_mock
from mock.blueprints.ui import ui

from mock.config import Config
from mock import context

import os

current_dir = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('mock')


class MockServer:
    """
    模拟接口服务
    使用flask在默认的9090端口启动，模拟线上接口，同时支持通过api动态修改接口数据。

    """
    def __init__(self, conf=None, record_mode=False):
        self.debug = False
        self.port = 9090
        self.server = None
        self.app = Flask('MOCK', static_folder=os.path.join(current_dir, 'static'))

        # 支持跨域请求
        CORS(self.app)

        # 生成过滤器实例
        if conf:
            context.application.conf = Config.from_conf_name(conf)
            logger.info(f'Load config from file: {conf}')
        else:
            context.application.conf = Config()
            logger.info(f'Create empty config')

        # 设置mock server 当前工作模式
        context.application.mode = context.MOCK_MODE if not record_mode else context.RECORD_MODE

        self.app.register_blueprint(api)
        self.app.register_blueprint(api_mock)
        self.app.register_blueprint(ui)

        print('APP static', self.app.static_folder)

        @self.app.route('/')
        def index():
            # 设置默认页面为UI首页
            return redirect(url_for('ui.index'))

    def start(self, block=False):
        """
        使用ThreadedWSGIServer启动服务

        """
        if self.debug:
            from werkzeug.debug import DebuggedApplication
            self.app = DebuggedApplication(self.app, True)
        self.server = server = ThreadedWSGIServer(host='0.0.0.0', port=self.port, app=self.app)

        def run_server():
            mode_name = 'mock'
            if context.application.mode == context.RECORD_MODE:
                mode_name = 'record'
            logger.info(f'MockServer start at {self.get_ip()}:{self.port} in {mode_name} mode')
            try:
                server.serve_forever()
            except InterruptedError:
                server.shutdown()
                server.server_close()
            logger.info('MockServer shutdown')

        if block:
            run_server()
        else:
            wsgi_thread = Thread(target=run_server)
            wsgi_thread.start()

    def stop(self):
        """
        停止服务

        """
        if self.server is None:
            return
        self.server.shutdown()
        self.server.server_close()
        logger.info('MockServer stop')

    def get_ip(self):
        """
        获取当前设备在网络中的ip地址

        :return: IP地址字符串
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 80))
        return s.getsockname()[0]

