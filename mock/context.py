from flask import jsonify

MOCK_MODE = 1
RECORD_MODE = 2


class Application:

    def __init__(self):
        self.conf = None
        self.mode = MOCK_MODE


application = Application()


def make_ok_response():
        return jsonify(
            {
                "code": 1000,
                "result": "ok"
            }
        )

