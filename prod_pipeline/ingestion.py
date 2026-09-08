from .clients import pinecone_client
from .config import (
    PINECONE_INDEX_NAME,
    PROPOSALS_NAMESPACE,
    KNOWLEDGE_NAMESPACE,
)
from .data import PAST_PROPOSALS, COMPANY_KNOWLEDGE
from .llm import embed_text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start = end - overlap

    return chunks

def _ingest_collection(documents: list[dict], namespace: str) -> None:
    index = pinecone_client.Index(PINECONE_INDEX_NAME)

    for document in documents:
        chunks = chunk_text(document["text"], chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            index.upsert(
                vectors=[{
                    "id": f"{document['id']}-chunk-{i}",
                    "values": embed_text(chunk),
                    "metadata": {
                        "text": chunk,
                        "source": document["title"],
                        "category": document["category"],
                        "chunk_index": i,
                    },
                }],
                namespace=namespace,
            )

        print(f"  Ingested: {document['title']} ({len(chunks)} chunks)")

def ingest_documents() -> None:
    print("Ingesting past proposals...")
    _ingest_collection(PAST_PROPOSALS, PROPOSALS_NAMESPACE)

    print("\nIngesting company knowledge...")
    _ingest_collection(COMPANY_KNOWLEDGE, KNOWLEDGE_NAMESPACE)

    print("\nIngestion complete.")
