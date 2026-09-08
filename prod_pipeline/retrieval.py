from .clients import pinecone_client
from .config import PINECONE_INDEX_NAME
from .llm import embed_text

def search_pinecone(query: str, namespace: str, top_k: int = 5) -> list[dict]:
    index = pinecone_client.Index(PINECONE_INDEX_NAME)
    query_embedding = embed_text(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
    )

    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match["metadata"].get("text", ""),
            "source": match["metadata"].get("source", "unknown"),
            "category": match["metadata"].get("category", "unknown"),
        }
        for match in results["matches"]
    ]
