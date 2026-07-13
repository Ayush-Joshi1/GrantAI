from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / 'apps' / 'api'):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from apps.api.src.infrastructure.ibm.granite_client import GraniteClient

client = GraniteClient(settings={})
response = client._build_inference_client().generate(prompt='hello')
print(type(response))
print(response)
print('repr', repr(response))
if isinstance(response, dict):
    print('dict keys', list(response.keys()))
    if 'results' in response and isinstance(response['results'], list):
        print('results type', type(response['results'][0]))
        print('results item', response['results'][0])
        if hasattr(response['results'][0], 'keys'):
            print('result keys', list(response['results'][0].keys()))
elif hasattr(response, 'to_dict'):
    print('to_dict', response.to_dict())
for attr_name in ['generated_text', 'result', 'results', 'choices', 'output', 'data']:
    if hasattr(response, attr_name):
        print(attr_name, getattr(response, attr_name))
