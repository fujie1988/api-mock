import os


ROOT = os.path.dirname(__file__)
RECORD = os.path.abspath(os.path.join(ROOT, 'record'))

if not os.path.exists(RECORD):
    os.mkdir(RECORD)

