from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from time import perf_counter
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / 'apps' / 'web' / '.env', override=False)
load_dotenv(ROOT / '.env', override=False)
for path in (ROOT, ROOT / 'apps' / 'api'):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from src.application.services.rag_answer_service import RAGAnswerService
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder


def get_env(name: str, fallback=None) -> str:
    val = os.getenv(name, fallback)
    return val.strip() if isinstance(val, str) else ''

api_key = get_env('IBM_API_KEY') or get_env('WATSONX_API_KEY') or get_env('WATSONX_APIKEY')
project_id = get_env('PROJECT_ID') or get_env('WATSONX_PROJECT_ID')
url = get_env('IBM_URL') or get_env('WATSONX_URL') or 'https://us-south.ml.cloud.ibm.com'
if not url.startswith('https://'):
    url = 'https://' + url

result = {
    'ibm_watsonx_ai_version': None,
    'env': {
        'GRANITE_MODEL_ID': get_env('GRANITE_MODEL_ID'),
        'WATSONX_MODEL_ID': get_env('WATSONX_MODEL_ID'),
        'MODEL_ID': get_env('MODEL_ID'),
        'IBM_URL': get_env('IBM_URL') or get_env('WATSONX_URL'),
        'PROJECT_ID_SET': bool(project_id),
    },
    'watsonx_url': url,
    'project_id_present': bool(project_id),
    'available_granite_models': [],
    'retrieval': {},
    'candidates': [],
}

try:
    import ibm_watsonx_ai
    result['ibm_watsonx_ai_version'] = getattr(ibm_watsonx_ai, '__version__', None)
except Exception as exc:
    result['ibm_watsonx_ai_version'] = f'ERROR: {type(exc).__name__}: {exc}'

creds = Credentials(api_key=api_key, url=url)
api_client = APIClient(credentials=creds, project_id=project_id)
try:
    model_specs = api_client.foundation_models.get_model_specs()
except Exception as exc:
    result['model_listing_error'] = f'{type(exc).__name__}: {exc}'
    model_specs = {'resources': []}
resources = model_specs.get('resources', [])
for item in resources:
    model_id = item.get('model_id')
    if not isinstance(model_id, str) or 'granite' not in model_id.lower():
        continue
    functions = item.get('functions')
    if isinstance(functions, list):
        functions = [f.get('id') if isinstance(f, dict) else f for f in functions]
    result['available_granite_models'].append({
        'model_id': model_id,
        'label': item.get('label'),
        'task_ids': item.get('task_ids'),
        'functions': functions,
        'lifecycle': item.get('lifecycle'),
        'short_description': item.get('short_description'),
        'long_description': item.get('long_description'),
    })
result['available_granite_models'].sort(key=lambda x: x['model_id'])

service = RAGAnswerService()
query = 'What are the eligibility requirements for the Startup India Seed Fund Scheme?'
try:
    start = perf_counter()
    retrieval_results = service.retrieval_client.retrieve(query=query, top_k=service.settings.top_k, similarity_threshold=service.settings.similarity_threshold)
    result['retrieval'] = {
        'query': query,
        'count': len(retrieval_results),
        'top_k': service.settings.top_k,
        'similarity_threshold': service.settings.similarity_threshold,
        'latency_seconds': perf_counter() - start,
        'results': [],
    }
    for item in retrieval_results:
        preview = item.content
        if isinstance(preview, str):
            preview = preview.strip().replace('\n', ' ')[:200]
        result['retrieval']['results'].append({
            'chunk_id': item.metadata.get('chunk_id'),
            'score': item.score,
            'grant_name': item.metadata.get('grant_name'),
            'organization': item.metadata.get('organization'),
            'source_document': item.metadata.get('file_name') or item.metadata.get('source_document') or item.metadata.get('document_name'),
            'page_number': item.metadata.get('page_number'),
            'content_preview': preview,
        })
    builder = GroundedPromptBuilder()
    prompt = builder.build_prompt(query, retrieval_results)
    result['retrieval']['prompt_length'] = len(prompt)
    result['retrieval']['prompt_prefix'] = prompt[:500]
except Exception as exc:
    result['retrieval_error'] = f'{type(exc).__name__}: {exc}'
    retrieval_results = []
    prompt = ''

# Candidate selection: choose Granite models that expose chat or generation and exclude specialized TTM models
candidates = []
for entry in result['available_granite_models']:
    mid = entry['model_id']
    if 'ttm' in mid:
        continue
    functions = entry.get('functions') or []
    if isinstance(functions, str):
        functions = [functions]
    lower_functions = {f.lower() for f in functions if isinstance(f, str)}
    entry['lower_functions'] = sorted(lower_functions)
    if not lower_functions.intersection({'text_chat', 'text_generation', 'generation', 'chat'}):
        continue
    candidates.append(entry)

for entry in candidates:
    model_id = entry['model_id']
    functions = entry.get('lower_functions', [])
    cand = {
        'model_id': model_id,
        'functions': functions,
        'chat_supported': 'text_chat' in functions or 'chat' in functions,
        'generate_supported': 'text_generation' in functions or 'generation' in functions,
        'generate_text_supported': 'text_generation' in functions or 'generation' in functions,
        'chat_test': None,
        'generate_test': None,
        'generate_text_test': None,
    }
    result['candidates'].append(cand)
    try:
        client = ModelInference(model_id=model_id, credentials=creds, project_id=project_id, params={'temperature': 0.1}, validate=False)
        if cand['chat_supported']:
            messages = [
                {'role': 'system', 'content': 'You are GrantAI, an AI assistant for Indian Government grant discovery and funding guidance. Answer the user\'s question only using the retrieved Government grant context below. Do not invent grant or scheme details.'},
                {'role': 'user', 'content': prompt},
            ]
            try:
                start = perf_counter()
                resp = client.chat(messages=messages)
                elapsed = perf_counter() - start
                text = None
                if isinstance(resp, str):
                    text = resp
                elif isinstance(resp, dict):
                    if 'choices' in resp and isinstance(resp['choices'], list) and resp['choices']:
                        first = resp['choices'][0]
                        if isinstance(first, dict):
                            msg = first.get('message')
                            if isinstance(msg, dict):
                                text = msg.get('content')
                    if text is None:
                        text = resp.get('generated_text') or resp.get('output')
                if text is None:
                    text = ''
                cand['chat_test'] = {
                    'status': 'SUCCESS',
                    'latency_seconds': elapsed,
                    'answer': text,
                    'answer_length': len(text),
                    'response_repr': repr(resp)[:2000],
                }
            except Exception as exc:
                cand['chat_test'] = {'status': 'FAILURE', 'error': f'{type(exc).__name__}: {exc}'}
        if cand['generate_supported']:
            try:
                start = perf_counter()
                resp = client.generate(prompt=prompt)
                elapsed = perf_counter() - start
                cand['generate_test'] = {'status': 'SUCCESS', 'latency_seconds': elapsed, 'answer': str(resp), 'answer_length': len(str(resp)), 'response_repr': repr(resp)[:2000]}
            except Exception as exc:
                cand['generate_test'] = {'status': 'FAILURE', 'error': f'{type(exc).__name__}: {exc}'}
        if cand['generate_text_supported']:
            try:
                start = perf_counter()
                resp = client.generate_text(prompt=prompt, params={'temperature': 0.1})
                elapsed = perf_counter() - start
                cand['generate_text_test'] = {'status': 'SUCCESS', 'latency_seconds': elapsed, 'answer': str(resp), 'answer_length': len(str(resp)), 'response_repr': repr(resp)[:2000]}
            except Exception as exc:
                cand['generate_text_test'] = {'status': 'FAILURE', 'error': f'{type(exc).__name__}: {exc}'}
    except Exception as exc:
        cand['chat_test'] = {'status': 'FAILURE', 'error': f'Client init failed: {type(exc).__name__}: {exc}'}
        cand['generate_test'] = {'status': 'FAILURE', 'error': f'Client init failed: {type(exc).__name__}: {exc}'}
        cand['generate_text_test'] = {'status': 'FAILURE', 'error': f'Client init failed: {type(exc).__name__}: {exc}'}

out_path = ROOT / 'prompt8c_live_probe_results.json'
with out_path.open('w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(out_path)
