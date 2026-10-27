import os

_mqlib = os.path.join(os.path.dirname(__file__), "fixtures", "bin", "MQLib")
if os.path.exists(_mqlib):
    os.environ.setdefault("MQLIB_PATH", os.path.abspath(_mqlib))
