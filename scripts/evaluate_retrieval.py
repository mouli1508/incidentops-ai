import json
import time
from pathlib import Path

from app.knowledge.search import search_knowledge


EVAL_FILE = Path("evals/retrieval_cases.json")
TOP_K = 3


def evaluate_retrieval():
    cases = json.loads(
        EVAL_FILE.read_text(encoding="utf-8")
    )

    if not cases:
        raise ValueError("Evaluation dataset is empty")

    hits = 0
    reciprocal_rank_sum = 0.0
    latencies = []

    print("\nINCIDENTOPS AI - RETRIEVAL EVALUATION")
    print("=" * 60)

    for case in cases:
        start = time.perf_counter()

        results = search_knowledge(
            query=case["question"],
            limit=TOP_K,
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

        retrieved_sources = [
            result["source_uri"]
            for result in results
        ]

        expected = case["expected_source"]

        if expected in retrieved_sources:
            rank = retrieved_sources.index(expected) + 1
            hits += 1
            reciprocal_rank_sum += 1 / rank

            print(
                f"[PASS] {case['id']} "
                f"Expected source at rank {rank}"
            )
        else:
            print(
                f"[FAIL] {case['id']} "
                f"Expected source not in top {TOP_K}"
            )

    total = len(cases)

    recall_at_k = hits / total
    mrr = reciprocal_rank_sum / total
    avg_latency = sum(latencies) / total

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    print(f"Questions evaluated: {total}")
    print(f"Recall@{TOP_K}: {recall_at_k:.2%}")
    print(f"MRR@{TOP_K}: {mrr:.4f}")
    print(f"Average search latency: {avg_latency:.2f} ms")


if __name__ == "__main__":
    evaluate_retrieval()
