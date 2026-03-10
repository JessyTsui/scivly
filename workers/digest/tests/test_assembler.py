"""Digest assembler tests."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from workers.common.pipeline import Pipeline
from workers.common.task import TaskPayload, TaskType
from workers.digest.assembler import DigestAssembler
from workers.digest.steps import AssembleDigestStep, DeliverDigestStep



def test_digest_assembler_groups_and_limits_papers() -> None:
    assembler = DigestAssembler(max_papers_per_section=2)
    papers = [
        {
            "paper_id": "p1",
            "title": "Vision Language Planning",
            "one_line_summary": "Planner for multimodal agents.",
            "total_score": 82.0,
            "primary_category": "cs.AI",
            "categories": ["cs.AI", "cs.RO"],
            "matched_rules": ["topic:agents"],
        },
        {
            "paper_id": "p2",
            "title": "Long Context Benchmark",
            "one_line_summary": "Evaluation suite for long-context models.",
            "total_score": 77.0,
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "matched_rules": ["topic:benchmarks"],
        },
        {
            "paper_id": "p3",
            "title": "Third AI Paper",
            "one_line_summary": "Should be trimmed by the section limit.",
            "total_score": 70.0,
            "primary_category": "cs.AI",
            "categories": ["cs.AI"],
            "matched_rules": ["topic:trim"],
        },
        {
            "paper_id": "p4",
            "title": "Reasoning with Molecules",
            "one_line_summary": "Chemistry reasoning benchmark.",
            "total_score": 79.0,
            "primary_category": "cs.CL",
            "categories": ["cs.CL"],
            "matched_rules": ["topic:reasoning"],
        },
    ]

    digest = assembler.assemble(papers, workspace_name="Demo Workspace")

    assert digest["title"] == "Demo Workspace Research Digest"
    assert digest["summary"] == {"section_count": 2, "paper_count": 3}
    assert digest["sections"][0]["paper_count"] == 2
    assert [paper["paper_id"] for paper in digest["sections"][0]["papers"]] == ["p1", "p2"]
    assert digest["sections"][1]["papers"][0]["paper_id"] == "p4"



def test_digest_assembler_normalizes_string_like_fields() -> None:
    assembler = DigestAssembler()
    digest = assembler.assemble(
        [
            {
                "paper_id": "p1",
                "title": "Agentic Retrieval for Science",
                "total_score": 83.0,
                "matched_topics": "retrieval agents",
                "categories": "cs.AI",
                "matched_rules": "topic:retrieval",
            }
        ]
    )

    assert digest["sections"][0]["section_id"] == "retrieval-agents"
    assert digest["sections"][0]["papers"][0]["categories"] == ["cs.AI"]
    assert digest["sections"][0]["papers"][0]["reasons"] == ["topic:retrieval"]



def test_deliver_pipeline_executes_assembly_and_delivery_steps() -> None:
    pipeline = Pipeline([AssembleDigestStep(), DeliverDigestStep()])
    task = TaskPayload(
        task_type=TaskType.DELIVER,
        workspace_id=uuid4(),
        idempotency_key="digest-deliver-001",
        payload={
            "workspace_name": "Demo Workspace",
            "channels": ["email", "discord"],
            "papers": [
                {
                    "paper_id": "p1",
                    "title": "Agentic Retrieval for Science",
                    "one_line_summary": "Retrieval-augmented ranking for research feeds.",
                    "total_score": 83.0,
                    "primary_category": "cs.AI",
                    "categories": ["cs.AI"],
                    "matched_rules": ["topic:retrieval"],
                }
            ],
        },
    )

    result = asyncio.run(pipeline.execute_task(task))

    assert result.result["steps"]["AssembleDigestStep"]["selected_paper_count"] == 1
    assert result.result["steps"]["DeliverDigestStep"]["delivery"]["status"] == "logged"
    assert result.result["final"]["delivery"]["channels"] == ["email", "discord"]



def test_deliver_step_normalizes_single_channel_string() -> None:
    pipeline = Pipeline([AssembleDigestStep(), DeliverDigestStep()])
    task = TaskPayload(
        task_type=TaskType.DELIVER,
        workspace_id=uuid4(),
        idempotency_key="digest-deliver-002",
        payload={
            "workspace_name": "Demo Workspace",
            "channels": "email",
            "papers": [
                {
                    "paper_id": "p1",
                    "title": "Agentic Retrieval for Science",
                    "total_score": 83.0,
                    "primary_category": "cs.AI",
                }
            ],
        },
    )

    result = asyncio.run(pipeline.execute_task(task))

    assert result.result["final"]["delivery"]["channels"] == ["email"]
