import time

from .clients import claude_client, openai_client
from .config import (
    CLAUDE_MODEL,
    EMBEDDING_MODEL,
    COST_PER_INPUT_TOKEN,
    COST_PER_OUTPUT_TOKEN,
)

def embed_text(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding

def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> dict:
    start = time.time()
    response = claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    elapsed = time.time() - start

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (
        input_tokens * COST_PER_INPUT_TOKEN
        + output_tokens * COST_PER_OUTPUT_TOKEN
    )

    return {
        "content": response.content[0].text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
        "latency": elapsed,
    }
