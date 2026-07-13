from __future__ import annotations
import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / 'apps' / 'api'):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from apps.api.src.application.services.rag_answer_service import RAGAnswerService
from apps.api.src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder

QUERIES = [
    "I have an AI startup in Pune. What grants may be relevant?",
    "What grants are available for biotechnology startups?",
    "I need ₹50 lakh for an MVP. Which funding schemes may be relevant?",
    "Which grants support women founders?",
    "What documents are required for Startup India Seed Fund?",
    "What are the eligibility requirements for the Startup India Seed Fund Scheme?",
    "Which schemes support technology startups?",
    "Tell me the weather in Pune tomorrow.",
]


def run():
    service = RAGAnswerService()
    results = []
    for q in QUERIES:
        entry = {'query': q}
        t0 = perf_counter()
        try:
            res = service.answer(q)
            total = perf_counter() - t0
            client = service.granite_client
            granite_latency = getattr(client, 'last_generation_latency_seconds', None)
            # retrieval metadata: re-run retrieval to capture metadata (service.answer already did it, but we re-run retrieval to capture scores)
            try:
                t_retr = perf_counter()
                retrieval_results = service.retrieval_client.retrieve(query=q, top_k=service.settings.top_k, similarity_threshold=service.settings.similarity_threshold)
                retrieval_latency = perf_counter() - t_retr
                retrieval_info = []
                for item in retrieval_results:
                    retrieval_info.append({
                        'chunk_id': item.metadata.get('chunk_id'),
                        'score': getattr(item, 'score', None),
                        'grant_name': item.metadata.get('grant_name'),
                        'organization': item.metadata.get('organization'),
                        'source_document': item.metadata.get('file_name') or item.metadata.get('source_document') or item.metadata.get('document_name'),
                        'page_number': item.metadata.get('page_number'),
                        'content_preview': (item.content or '')[:1000],
                    })
            except Exception as exc:
                retrieval_info = []
                retrieval_latency = None
                entry.setdefault('errors', []).append(f'retrieval error: {type(exc).__name__}: {exc}')

            entry.update({
                'retrieval_count': len(retrieval_info),
                'retrieval_latency_seconds': retrieval_latency,
                'retrieval_results': retrieval_info,
                'prompt_length': len(GroundedPromptBuilder().build_prompt(q, retrieval_results)),
                'answer_text': res.answer,
                'answer_length': len(res.answer) if res.answer else 0,
                'answer_sources': [s.__dict__ for s in res.sources],
                'granite_model_id': service.granite_client._get_env_value('GRANITE_MODEL_ID', 'WATSONX_MODEL_ID', 'MODEL_ID') or 'ibm/granite-8b-code-instruct',
                'inference_method': 'chat',
                'granite_latency_seconds': granite_latency,
                'total_latency_seconds': total,
            })
        except Exception as exc:
            entry['error'] = f'{type(exc).__name__}: {exc}'
        results.append(entry)
    out = ROOT / 'eight_query_results.json'
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(out)

if __name__ == '__main__':
    run()
