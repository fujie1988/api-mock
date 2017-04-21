from mock import mock_server
from proxy import proxy_server
import fire


def mock(conf=None, record=False):
    mock_server.MockServer(conf=conf, record_mode=record).start(block=True)


def proxy(conf=None):
    proxy_server.start(conf=conf)


if __name__ == '__main__':
    fire.Fire()

