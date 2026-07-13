from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
# Add project root and apps/api to sys.path (matching test scripts)
for p in (ROOT, ROOT / 'apps' / 'api'):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from apps.api.src.application.services.rag_answer_service import RAGAnswerService
from apps.api.src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder


def run():
    result = {'query': None, 'retrieval': {}, 'prompt': {}, 'granite': {}, 'answer': {}, 'errors': []}
    query = "What are the eligibility requirements for the Startup India Seed Fund Scheme?"
    result['query'] = query
    service = None
    try:
        service = RAGAnswerService()
    except Exception as exc:
        result['errors'].append(f'RAGAnswerService init error: {type(exc).__name__}: {exc}')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Retrieve explicitly to collect retrieval metadata
    try:
        t0 = perf_counter()
        retrieval_results = service.retrieval_client.retrieve(query=query, top_k=service.settings.top_k, similarity_threshold=service.settings.similarity_threshold)
        retrieval_latency = perf_counter() - t0
        result['retrieval']['count'] = len(retrieval_results)
        result['retrieval']['latency_seconds'] = retrieval_latency
        result['retrieval']['results'] = []
        for item in retrieval_results:
            content_preview = ''
            try:
                content_preview = (item.content or '')[:1000]
            except Exception:
                content_preview = ''
            result['retrieval']['results'].append({
                'chunk_id': item.metadata.get('chunk_id'),
                'score': getattr(item, 'score', None),
                'grant_name': item.metadata.get('grant_name'),
                'organization': item.metadata.get('organization'),
                'source_document': item.metadata.get('file_name') or item.metadata.get('source_document') or item.metadata.get('document_name'),
                'page_number': item.metadata.get('page_number'),
                'content_preview': content_preview,
            })
    except Exception as exc:
        result['errors'].append(f'Retrieval error: {type(exc).__name__}: {exc}')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Build prompt
    try:
        builder = GroundedPromptBuilder()
        prompt = builder.build_prompt(query, retrieval_results)
        result['prompt']['length'] = len(prompt)
        result['prompt']['prefix'] = prompt[:1000]
    except Exception as exc:
        result['errors'].append(f'Prompt build error: {type(exc).__name__}: {exc}')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Call production path
    try:
        t0 = perf_counter()
        rag_result = service.answer(query)
        total_latency = perf_counter() - t0
        # Granite latency captured on client if available
        granite_latency = None
        try:
            client = service.granite_client
            granite_latency = getattr(client, 'last_generation_latency_seconds', None)
        except Exception:
            granite_latency = None

        result['granite']['model_id'] = service.granite_client._get_env_value('GRANITE_MODEL_ID', 'WATSONX_MODEL_ID', 'MODEL_ID') or 'ibm/granite-8b-code-instruct'
        result['granite']['inference_method'] = 'chat'
        result['answer']['text'] = rag_result.answer
        result['answer']['length'] = len(rag_result.answer) if rag_result.answer else 0
        result['answer']['sources'] = [s.__dict__ for s in rag_result.sources]
        result['timing'] = {
            'retrieval_latency_seconds': result['retrieval']['latency_seconds'],
            'granite_generation_latency_seconds': granite_latency,
            'total_latency_seconds': total_latency,
        }
    except Exception as exc:
        result['errors'].append(f'RAG answer error: {type(exc).__name__}: {exc}')

    out_path = ROOT / 'production_gate_result.json'
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(out_path)


if __name__ == '__main__':
    run()
