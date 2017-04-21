from mock.config import Config
from flask import Response, redirect, render_template, Blueprint, jsonify
import os
import json


ui = Blueprint('ui', __name__, url_prefix='/ui', template_folder='../templates', static_folder='../static')


@ui.route('/')
def index():
    return render_template('index.html')


@ui.route('/records')
def request():
    return Response(
        json.dumps([{'message': 'a'}, {'message': 'b'}, {'message': 'c'}]),
        headers=(('Access-Control-Allow-Origin', 'http://localhost:8080'),))

