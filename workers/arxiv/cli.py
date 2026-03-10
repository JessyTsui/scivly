from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .client import ArxivClient
from .dedup import deduplicate_papers
from .filters import apply_hard_filters
from .models import ScoringProfile
from .scorer import DEFAULT_CATEGORY_KEYWORDS, MetadataScorer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch, filter, deduplicate, and score recent arXiv papers.")
    parser.add_argument("--categories", nargs="+", default=[], help="arXiv categories, for example cs.CL cs.AI")
    parser.add_argument("--days", type=int, default=1, help="How many recent days to query")
    parser.add_argument("--query", default=None, help="Optional full-text arXiv search query")
    parser.add_argument("--keyword", action="append", default=[], help="Additional profile keyword")
    parser.add_argument("--theme", action="append", default=[], help="Additional profile theme")
    parser.add_argument(
        "--tracked-author",
        action="append",
        default=[],
        help="Tracked author name for profile-fit and prestige boosts",
    )
    parser.add_argument("--max-results", type=int, default=25, help="Maximum number of raw arXiv entries to fetch")
    parser.add_argument("--output", default=None, help="Optional JSON file path")
    return parser


def build_profile(args: argparse.Namespace) -> ScoringProfile:
    inferred_keywords: list[str] = []
    for category in args.categories:
        inferred_keywords.extend(DEFAULT_CATEGORY_KEYWORDS.get(category, []))
    if args.query:
        inferred_keywords.append(args.query)

    keywords = list(dict.fromkeys([*args.keyword, *inferred_keywords]))
    themes = list(dict.fromkeys(args.theme or args.categories))
    return ScoringProfile(
        name="cli-default",
        categories=args.categories,
        keywords=keywords,
        themes=themes,
        tracked_authors=args.tracked_author,
    )


def serialize_result(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False)


async def run(args: argparse.Namespace) -> dict[str, Any]:
    if not args.categories and not args.query:
        raise ValueError("Pass at least one --categories value or provide --query")

    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=args.days)
    profile = build_profile(args)

    async with ArxivClient() as client:
        fetched = await client.search(
            categories=args.categories,
            date_from=date_from,
            date_to=now,
            query=args.query,
            max_results=args.max_results,
        )

    dedup_records = deduplicate_papers(fetched)
    deduped_papers = [record.paper for record in dedup_records]
    filtered_papers, rejected = apply_hard_filters(deduped_papers)

    scorer = MetadataScorer(profile=profile)
    scoring_results = scorer.score_papers(filtered_papers)
    score_lookup = {result.paper_id: result for result in scoring_results}
    dedup_lookup = {record.paper.arxiv_id: record for record in dedup_records}
    papers_payload = []
    for result in scoring_results:
        record = dedup_lookup[result.paper_id]
        papers_payload.append(
            {
                "paper": record.paper.model_dump(mode="json"),
                "score": result.model_dump(mode="json"),
                "dedup": {
                    "canonical_id": record.canonical_id,
                    "merged_versions": record.merged_versions,
                    "source_ids": record.source_ids,
                },
            }
        )

    summary = {
        "fetched": len(fetched),
        "deduplicated": len(dedup_records),
        "passed_filters": len(filtered_papers),
        "rejected": len(rejected),
        "query_window": {
            "date_from": date_from.isoformat(),
            "date_to": now.isoformat(),
        },
    }
    if score_lookup:
        top_result = max(score_lookup.values(), key=lambda result: result.total_score)
        summary["top_paper_id"] = top_result.paper_id
        summary["top_score"] = top_result.total_score

    return {
        "summary": summary,
        "profile": profile.model_dump(mode="json"),
        "papers": papers_payload,
        "rejections": [result.model_dump(mode="json") for result in rejected],
    }


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    payload = asyncio.run(run(args))
    rendered = serialize_result(payload)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
