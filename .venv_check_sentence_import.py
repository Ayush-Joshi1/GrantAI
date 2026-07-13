import importlib
try:
    m = importlib.import_module('sentence_transformers')
    print('OK', getattr(m, '__file__', 'builtin'))
except Exception as e:
    print('ERR', e)
