import os
import anthropic
from openai import OpenAI
from pinecone import Pinecone
from langfuse import Langfuse
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

pii_analyzer = AnalyzerEngine()
pii_anonymizer = AnonymizerEngine()
