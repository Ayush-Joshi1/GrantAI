# `prompts/rag`

Why it exists:
- Templates that enforce citation behavior and grounded answers.
- Output formatting rules for “answer + evidence” responses used by chat and eligibility explainers.
- Prompt builders that convert retrieved evidence into grounded prompts for downstream LLM inference.

Current assets:
- `grounded_prompt_builder.py`: reusable prompt formatter for grounded Granite prompts.

