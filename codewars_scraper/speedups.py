try:
    json = __import__("ujson")
except ImportError:
    json = __import__("json")
