from typing import Callable
from .store import EmbeddingStore

class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.
    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # 1. Retrieve top-k relevant chunks
        chunks = self.store.search(question, top_k=top_k)

        # 2. Build prompt with chunks as context
        context = "\n\n".join(f"[{i+1}] {chunk}" for i, chunk in enumerate(chunks))
        prompt = (
            f"Use the following context to answer the question.\n"
            f"If the answer is not contained in the context, say \"I don't know\".\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            f"Answer:"
        )

        # 3. Call LLM and return the answer
        return self.llm_fn(prompt)
