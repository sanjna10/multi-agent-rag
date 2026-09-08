import os
from dotenv import load_dotenv

load_dotenv()

CLAUDE_MODEL = "claude-haiku-4-5"
EMBEDDING_MODEL = "text-embedding-3-small"

MAX_COST_PER_RFP = 2.00
MAX_REVISION_CYCLES = 2
MIN_QUALITY_SCORE = 7

COST_PER_INPUT_TOKEN = 3.0 / 1_000_000
COST_PER_OUTPUT_TOKEN = 15.0 / 1_000_000

PROPOSALS_NAMESPACE = "past-proposals"
KNOWLEDGE_NAMESPACE = "company-knowledge"

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
