"""
AgentOS 2.0 — RAG Architect Demo
Build a production RAG pipeline using the rag-architect skill.
Implements the hybrid search architecture from SKILL.md:
  Chunking → Embedding → pgvector → BM25 → RRF → Cross-encoder → Answer
"""
import anthropic
import numpy as np
from pathlib import Path
from typing import Any


# ── Skill loader ─────────────────────────────────────────────────────────────
def load_skill(name: str) -> str:
    return (Path(__file__).parent.parent / name / "SKILL.md").read_text()


# ── Semantic chunking (from rag-architect SKILL.md) ──────────────────────────
def chunk_by_semantic_density(text: str, target_tokens: int = 512) -> list[str]:
    """
    Semantic-aware chunking: split at paragraph boundaries,
    targeting ~512 tokens per chunk with 10% overlap.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = len(para.split())
        if current_tokens + para_tokens > target_tokens and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            # 10% overlap: keep last paragraph
            overlap = current_chunk[-1:] if current_chunk else []
            current_chunk = overlap
            current_tokens = len(overlap[0].split()) if overlap else 0
        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


# ── Hybrid retrieval (70% dense + 30% BM25) ─────────────────────────────────
def reciprocal_rank_fusion(
    dense_results: list[tuple[str, float]],
    sparse_results: list[tuple[str, float]],
    k: int = 60,
    dense_weight: float = 0.70,
    sparse_weight: float = 0.30,
) -> list[tuple[str, float]]:
    """
    Reciprocal Rank Fusion combining dense (semantic) and sparse (BM25) results.
    Standard formula: RRF(d) = Σ 1/(k + rank(d))
    """
    scores: dict[str, float] = {}

    for rank, (doc, _) in enumerate(dense_results, 1):
        scores[doc] = scores.get(doc, 0) + dense_weight * (1 / (k + rank))

    for rank, (doc, _) in enumerate(sparse_results, 1):
        scores[doc] = scores.get(doc, 0) + sparse_weight * (1 / (k + rank))

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ── Cross-encoder re-ranking simulation ─────────────────────────────────────
def rerank_chunks(
    query: str,
    chunks: list[str],
    top_k: int = 5,
) -> list[str]:
    """
    Simulate cross-encoder re-ranking.
    In production: use cross-encoder/ms-marco-MiniLM-L-6-v2 or Cohere Rerank.
    """
    # Simplified: score by query term overlap (replace with actual cross-encoder)
    query_terms = set(query.lower().split())
    scored = [
        (chunk, sum(1 for t in query_terms if t in chunk.lower()))
        for chunk in chunks
    ]
    return [c for c, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]]


# ── Answer synthesis via rag-architect skill ─────────────────────────────────
def synthesize_answer(
    query: str,
    retrieved_chunks: list[str],
    skill_content: str,
) -> dict[str, Any]:
    """Use rag-architect skill to synthesize a grounded answer."""
    client = anthropic.Anthropic()

    context = "\n\n---\n\n".join(
        f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(retrieved_chunks)
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=skill_content,
        messages=[
            {
                "role": "user",
                "content": f"""Answer the following question using ONLY the provided context chunks.
For every claim, cite the chunk number [Chunk N].
If the answer cannot be found in the chunks, say "Insufficient context."

Question: {query}

Context:
{context}""",
            }
        ],
    )

    return {
        "answer": response.content[0].text,
        "chunks_used": len(retrieved_chunks),
        "tokens": response.usage.input_tokens + response.usage.output_tokens,
    }


# ── Full pipeline demo ────────────────────────────────────────────────────────
def run_rag_pipeline_demo() -> None:
    print("=== AgentOS RAGArchitect Pipeline Demo ===\n")

    # Sample document corpus
    documents = [
        """AgentOS 2.0 is a collection of 100+ production-grade Claude Skills.
        Each skill is a SKILL.md file with YAML frontmatter and markdown instructions.
        Skills are designed to give Claude institutional-depth expertise.""",

        """The FinanceOracle skill provides Goldman Sachs-level financial analysis.
        It includes Black-Scholes option pricing, Black-Litterman portfolio construction,
        risk parity optimization, and institutional-grade fixed income analytics.""",

        """The CEOWarRoom skill provides Fortune 50 CEO decision intelligence.
        It covers capital allocation with ROIC frameworks, competitive moat analysis
        with 6 sources including the new AI Flywheel moat, and activist investor defense.""",

        """To activate a skill in Claude.ai: go to Projects, create a new Project,
        open Project Instructions, and paste any SKILL.md content.
        Every conversation in that project will use the activated agent.""",

        """ClaudeMythos is Claude's apex intelligence skill. It operates beyond
        conventional assistant mode using the 7-level Civilizational Stack analysis
        and the SystemPromptForge for legendary prompt architecture design.""",
    ]

    query = "How do I activate the FinanceOracle skill in Claude?"

    # Step 1: Chunk
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_by_semantic_density(doc, target_tokens=100))

    print(f"Step 1: Chunked {len(documents)} documents → {len(all_chunks)} chunks")

    # Step 2: Simulate hybrid retrieval (no actual embeddings in this demo)
    # In production: use pgvector for dense + Elasticsearch/Tantivy for sparse
    dense_mock = [(c, np.random.random()) for c in all_chunks[:3]]
    sparse_mock = [(c, np.random.random()) for c in all_chunks[2:5]]
    fused = reciprocal_rank_fusion(dense_mock, sparse_mock)
    print(f"Step 2: Hybrid RRF retrieval → {len(fused)} candidates")

    # Step 3: Cross-encoder re-rank
    reranked = rerank_chunks(query, [c for c, _ in fused], top_k=3)
    print(f"Step 3: Re-ranked → top {len(reranked)} chunks selected\n")

    # Step 4: Load skill + synthesize answer
    skill = load_skill("rag-architect")
    result = synthesize_answer(query, reranked, skill)

    print(f"Step 4: Answer synthesis ({result['tokens']} tokens)\n")
    print("─" * 60)
    print(result["answer"])
    print("─" * 60)


if __name__ == "__main__":
    print("AgentOS 2.0 — RAGArchitect Pipeline")
    print("Set ANTHROPIC_API_KEY to run the full pipeline.\n")
    # Uncomment to run:
    # run_rag_pipeline_demo()
