import { DEMO_WORKSPACE_ID } from "@/lib/mock/profiles";
import { hoursAgo } from "@/lib/mock/time";
import type { PaperOut } from "@/lib/api/types";

export const mockPapers: PaperOut[] = [
  {
    id: "paper-lab-notebook-agents",
    arxiv_id: "2503.10123",
    version: 1,
    title: "Lab Notebook Agents: Retrieval-Augmented Planning for Open-Ended Scientific QA",
    abstract:
      "We introduce a research-agent stack that grounds long-form scientific questions in notebook traces, paper metadata, and citation snippets before planning an answer. The system combines a lightweight retrieval planner with structured verification checkpoints, improving factual consistency on multi-hop paper questions while keeping token costs bounded.",
    authors: [
      { name: "Yue Lin", affiliation: "Stanford University" },
      { name: "Hannah Park", affiliation: "Allen Institute for AI" },
      { name: "Mika Chen", affiliation: "University of Washington" },
    ],
    categories: ["cs.AI", "cs.CL", "cs.IR"],
    primary_category: "cs.AI",
    comment: "Code and benchmark release included.",
    published_at: hoursAgo(6.5),
    updated_at: hoursAgo(6.5),
    one_line_summary:
      "A retrieval-planning loop for scientific QA that logs evidence before answering.",
    key_points: [
      "Introduces explicit notebook evidence checkpoints before answer synthesis.",
      "Shows better groundedness on ambiguous research questions than agent baselines.",
      "Releases an evaluation set focused on paper-level follow-up questions.",
    ],
    method_summary:
      "The planner chooses between abstract retrieval, citation retrieval, and notebook memory before a verifier scores the proposed answer plan.",
    conclusion_summary:
      "Evidence-first planning improves answer quality most on long, citation-heavy scientific queries.",
    limitations:
      "The benchmark still focuses on English-language papers and does not measure long multi-session memory drift.",
    figure_descriptions: [
      "A pipeline figure shows retrieval, planning, verification, and answer synthesis as separate stages.",
    ],
    profile_labels: ["Scientific QA Systems"],
    score: {
      id: "score-lab-notebook-agents",
      paper_id: "paper-lab-notebook-agents",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 88,
      topical_relevance: 39,
      prestige_priors: 13,
      actionability: 14,
      profile_fit: 10,
      novelty_diversity: 7,
      penalties: -3,
      matched_rules: {
        positive: [
          "Scientific QA keyword overlap in title and abstract",
          "Code release and benchmark terms found in comments",
          "Retrieval and verification both match saved themes",
        ],
        negative: ["No multilingual evaluation reported"],
      },
      threshold_decision: "source_fetch",
      llm_rerank_delta: 8,
      llm_rerank_reasons: [
        "High likely user value because the abstract names both retrieval and verification.",
        "Benchmark release makes it immediately digest-worthy.",
      ],
      created_at: hoursAgo(5.7),
    },
  },
  {
    id: "paper-vision-language-repair-loops",
    arxiv_id: "2503.09811",
    version: 2,
    title: "Vision-Language Repair Loops for Embodied Benchmarks",
    abstract:
      "This paper studies how multimodal agents can repair failed plans after visual grounding errors in embodied benchmarks. The proposed loop detects whether a failure is caused by perception, state tracking, or action sequencing, then selectively re-queries visual evidence instead of restarting the entire trajectory.",
    authors: [
      { name: "Marta Kovac", affiliation: "University of Oxford" },
      { name: "Rishi Patel", affiliation: "Google DeepMind" },
    ],
    categories: ["cs.AI", "cs.CV", "cs.RO"],
    primary_category: "cs.CV",
    comment: "Project page and simulator videos included.",
    published_at: hoursAgo(13.5),
    updated_at: hoursAgo(7.8),
    one_line_summary:
      "A repair loop that re-opens visual evidence only when an embodied agent fails for perception reasons.",
    key_points: [
      "Separates perception failures from planning failures before issuing repairs.",
      "Improves benchmark success without full trajectory resets.",
      "Includes videos that explain which visual evidence triggered each repair.",
    ],
    method_summary:
      "Failure diagnosis is learned from trajectory state and visual mismatch signals, then used to choose a cheap repair strategy.",
    conclusion_summary:
      "Targeted visual repairs outperform naive replanning when the environment state remains mostly correct.",
    limitations:
      "Results are concentrated on indoor simulators and may not transfer to noisy real-world sensors.",
    figure_descriptions: [
      "A confusion matrix highlights perception failures versus planning failures across benchmark tasks.",
    ],
    profile_labels: ["Vision-Language Agents"],
    score: {
      id: "score-vision-language-repair-loops",
      paper_id: "paper-vision-language-repair-loops",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-vlm-agents",
      score_version: "2026.03.public",
      total_score: 82,
      topical_relevance: 36,
      prestige_priors: 14,
      actionability: 13,
      profile_fit: 8,
      novelty_diversity: 8,
      penalties: -5,
      matched_rules: {
        positive: [
          "Embodied and visual grounding terms match agent profile",
          "Project page and videos increase actionability",
        ],
        negative: ["Limited real-world validation"],
      },
      threshold_decision: "digest_candidate",
      llm_rerank_delta: 6,
      llm_rerank_reasons: [
        "Repair-loop framing is more actionable than general multimodal planning papers this week.",
      ],
      created_at: hoursAgo(7.3),
    },
  },
  {
    id: "paper-sparse-memory-adapters",
    arxiv_id: "2503.09007",
    version: 1,
    title: "Sparse Memory Adapters for 512k Token Scientific Review",
    abstract:
      "We propose sparse memory adapters that preserve salient evidence across 512k-token scientific review sessions without retraining the base model. The method routes long-context evidence into a compact memory bank, recovering ablation details and appendix references more accurately than dense cache baselines.",
    authors: [
      { name: "Irene Wu", affiliation: "MIT" },
      { name: "David Feldman", affiliation: "MosaicML" },
      { name: "Koji Saito", affiliation: "University of Tokyo" },
    ],
    categories: ["cs.CL", "cs.LG", "stat.ML"],
    primary_category: "cs.LG",
    comment: "Open weights and long-context benchmark scripts released.",
    published_at: hoursAgo(38),
    updated_at: hoursAgo(38),
    one_line_summary:
      "Sparse adapters keep high-value evidence alive during very long scientific review sessions.",
    key_points: [
      "Preserves appendix and ablation references more faithfully than dense caches.",
      "Runs on top of existing long-context models without finetuning.",
      "Comes with scripts tailored to paper-review workflows.",
    ],
    method_summary:
      "A salience model writes only high-utility evidence chunks into a sparse adapter memory, then rehydrates them during answer generation.",
    conclusion_summary:
      "Sparse memory is especially helpful when evidence appears early and must be recalled after hundreds of pages.",
    limitations:
      "The work does not compare against retrieval-based compression pipelines with human annotations.",
    figure_descriptions: [
      "A latency-versus-recall plot shows sparse adapters dominate dense cache baselines in the tested regime.",
    ],
    profile_labels: ["Long-Context Efficiency"],
    score: {
      id: "score-sparse-memory-adapters",
      paper_id: "paper-sparse-memory-adapters",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-long-context",
      score_version: "2026.03.public",
      total_score: 84,
      topical_relevance: 37,
      prestige_priors: 12,
      actionability: 13,
      profile_fit: 9,
      novelty_diversity: 9,
      penalties: -4,
      matched_rules: {
        positive: [
          "Long-context and memory keywords match saved profile exactly",
          "Open weights and scripts add strong actionability",
        ],
        negative: ["No cost breakdown for hosted inference"],
      },
      threshold_decision: "digest_candidate",
      llm_rerank_delta: 7,
      llm_rerank_reasons: [
        "Likely high value because it addresses evidence retention in review workflows rather than generic long-context chat.",
      ],
      created_at: hoursAgo(36.5),
    },
  },
  {
    id: "paper-dataset-cards-cite-back",
    arxiv_id: "2503.08765",
    version: 1,
    title: "Dataset Cards that Cite Back: Automatic Evidence Linking for Benchmark Reports",
    abstract:
      "Benchmark reports often summarize dataset choices without surfacing the experimental evidence that motivated them. We present a citation-linking pipeline that attaches benchmark observations to structured dataset cards, making it easier to inspect why particular dataset slices or exclusions mattered.",
    authors: [
      { name: "Paula Gomez", affiliation: "Carnegie Mellon University" },
      { name: "Neel Shah", affiliation: "University of Toronto" },
    ],
    categories: ["cs.CL", "cs.IR", "cs.AI"],
    primary_category: "cs.IR",
    comment: "Includes evaluation on benchmark reports and data statements.",
    published_at: hoursAgo(70),
    updated_at: hoursAgo(70),
    one_line_summary:
      "Automatically links benchmark report claims back to structured dataset cards.",
    key_points: [
      "Turns benchmark observations into traceable dataset evidence links.",
      "Makes evaluation reports easier to inspect for evidence quality.",
      "Could fit directly into digest QA and audit workflows.",
    ],
    method_summary:
      "A citation linker aligns benchmark report sentences with dataset card slots using citation spans and claim schemas.",
    conclusion_summary:
      "Structured evidence links improve auditability even when automatic extraction is imperfect.",
    limitations:
      "The method depends on semi-structured dataset cards and degrades when reports omit citation spans.",
    figure_descriptions: [
      "A side-by-side example highlights how a benchmark claim connects back to dataset-card evidence.",
    ],
    profile_labels: ["Scientific QA Systems"],
    score: {
      id: "score-dataset-cards-cite-back",
      paper_id: "paper-dataset-cards-cite-back",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 74,
      topical_relevance: 31,
      prestige_priors: 11,
      actionability: 12,
      profile_fit: 9,
      novelty_diversity: 8,
      penalties: -7,
      matched_rules: {
        positive: [
          "Evidence linking matches digest QA interests",
          "Benchmark report language increases downstream usefulness",
        ],
        negative: ["Less direct tool-use angle than top-ranked QA papers"],
      },
      threshold_decision: "rerank",
      llm_rerank_delta: 4,
      llm_rerank_reasons: [
        "Worth digesting as infrastructure for evidence-backed reports, but not urgent enough for source fetch.",
      ],
      created_at: hoursAgo(66),
    },
  },
  {
    id: "paper-toolsandbox-r",
    arxiv_id: "2503.08142",
    version: 1,
    title: "ToolSandbox-R: A Reproducible Evaluation Suite for Research Agents",
    abstract:
      "We build a reproducible sandbox for evaluating research agents on tasks that involve paper retrieval, note-taking, evidence quoting, and follow-up question answering. The suite emphasizes replayability, latency accounting, and failure inspection rather than only final answer accuracy.",
    authors: [
      { name: "Daniel Ho", affiliation: "Princeton University" },
      { name: "Sara Nikkhah", affiliation: "Anthropic" },
      { name: "Leo Martens", affiliation: "ETH Zurich" },
    ],
    categories: ["cs.AI", "cs.CL", "cs.IR"],
    primary_category: "cs.AI",
    comment: "Includes a command-line runner and replay traces.",
    published_at: hoursAgo(24),
    updated_at: hoursAgo(24),
    one_line_summary:
      "A replay-friendly benchmark for research agents that measures evidence quality and latency.",
    key_points: [
      "Puts replayability and latency tracking into the benchmark itself.",
      "Includes failure traces for inspection instead of just aggregate scores.",
      "Matches the exact workflow of paper QA and digest follow-up.",
    ],
    method_summary:
      "Tasks are packaged as deterministic sandboxes with quoted-evidence requirements and replayable execution traces.",
    conclusion_summary:
      "Benchmarks that expose failure traces lead to more actionable agent improvements than score-only suites.",
    limitations:
      "The suite currently covers paper-centric tasks and does not yet include code execution sandboxes.",
    figure_descriptions: [
      "A leaderboard-style table compares evidence coverage, latency, and replay success across agents.",
    ],
    profile_labels: ["Scientific QA Systems"],
    score: {
      id: "score-toolsandbox-r",
      paper_id: "paper-toolsandbox-r",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 79,
      topical_relevance: 34,
      prestige_priors: 12,
      actionability: 14,
      profile_fit: 10,
      novelty_diversity: 8,
      penalties: -4,
      matched_rules: {
        positive: [
          "Replay and latency accounting align strongly with workspace goals",
          "CLI runner increases practical follow-up value",
        ],
        negative: ["No multimodal component yet"],
      },
      threshold_decision: "digest_candidate",
      llm_rerank_delta: 5,
      llm_rerank_reasons: [
        "High relevance to agent evaluation infrastructure and directly useful for comparing future papers.",
      ],
      created_at: hoursAgo(23),
    },
  },
  {
    id: "paper-chain-of-verification-figures",
    arxiv_id: "2503.07654",
    version: 1,
    title: "Chain-of-Verification for Multimodal Paper Figure Grounding",
    abstract:
      "Figure-grounded paper assistants often hallucinate chart conclusions when captions are underspecified. We present a chain-of-verification procedure that asks the model to separately ground figure region evidence, caption evidence, and abstract-level claims before emitting a final explanation.",
    authors: [
      { name: "Amina Farouk", affiliation: "National University of Singapore" },
      { name: "Dylan Hart", affiliation: "Meta FAIR" },
    ],
    categories: ["cs.CV", "cs.CL", "cs.AI"],
    primary_category: "cs.CV",
    comment: "Accepted to a multimodal reasoning workshop.",
    published_at: hoursAgo(108),
    updated_at: hoursAgo(108),
    one_line_summary:
      "Verifies figure evidence in three passes before producing a paper explanation.",
    key_points: [
      "Separates figure-region evidence from caption evidence before answer generation.",
      "Improves citation faithfulness on chart-heavy papers.",
      "Good fit for future paper detail pages and visual QA.",
    ],
    method_summary:
      "The verifier forces intermediate evidence statements that can be scored before the final multimodal explanation is accepted.",
    conclusion_summary:
      "Structured verification reduces overconfident figure explanations with modest latency cost.",
    limitations:
      "The method focuses on chart and table figures, leaving microscopy and diagram-heavy papers underexplored.",
    figure_descriptions: [
      "A three-stage pipeline figure shows region grounding, caption grounding, and abstract grounding feeding the final answer.",
    ],
    profile_labels: ["Vision-Language Agents"],
    score: {
      id: "score-chain-of-verification-figures",
      paper_id: "paper-chain-of-verification-figures",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-vlm-agents",
      score_version: "2026.03.public",
      total_score: 72,
      topical_relevance: 33,
      prestige_priors: 10,
      actionability: 11,
      profile_fit: 9,
      novelty_diversity: 8,
      penalties: -9,
      matched_rules: {
        positive: [
          "Figure grounding and verification match saved profile",
          "Workshop acceptance suggests mature experimental framing",
        ],
        negative: ["Coverage limited to selected figure types"],
      },
      threshold_decision: "rerank",
      llm_rerank_delta: 3,
      llm_rerank_reasons: [
        "Strong fit for the workspace's future paper-detail UX even if benchmark scope is still narrow.",
      ],
      created_at: hoursAgo(101),
    },
  },
  {
    id: "paper-affiliation-signals",
    arxiv_id: "2503.07111",
    version: 1,
    title: "Affiliation Signals in Large-Scale Paper Recommendation",
    abstract:
      "Affiliation priors are common in paper recommenders, but they can over-amplify prestige and suppress topical fit. We analyze when affiliation features help triage, when they hurt, and how normalization schemes can preserve relevance while limiting bias.",
    authors: [
      { name: "Nora Bell", affiliation: "University of Edinburgh" },
      { name: "Kaito Hara", affiliation: "Preferred Networks" },
    ],
    categories: ["cs.IR", "cs.LG", "stat.ML"],
    primary_category: "cs.IR",
    comment: "Includes ablations on institution and lab priors.",
    published_at: hoursAgo(131),
    updated_at: hoursAgo(131),
    one_line_summary:
      "A careful look at when affiliation priors help paper ranking and when they distort it.",
    key_points: [
      "Measures how prestige features interact with topical relevance.",
      "Compares several normalization schemes for multi-author papers.",
      "Directly relevant to Scivly's metadata-first triage layer.",
    ],
    method_summary:
      "Offline ranking experiments compare relevance, bias, and diversity under multiple affiliation-prior formulas.",
    conclusion_summary:
      "Soft priors work best when author count normalization is explicit and topical fit remains dominant.",
    limitations:
      "The paper evaluates offline recommendation logs rather than live user-facing digest quality.",
    figure_descriptions: [
      "A tradeoff curve shows relevance gains against bias increases for different prior weightings.",
    ],
    profile_labels: ["Scientific QA Systems", "Long-Context Efficiency"],
    score: {
      id: "score-affiliation-signals",
      paper_id: "paper-affiliation-signals",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 63,
      topical_relevance: 26,
      prestige_priors: 12,
      actionability: 8,
      profile_fit: 9,
      novelty_diversity: 10,
      penalties: -2,
      matched_rules: {
        positive: [
          "Directly overlaps with explainable scoring design",
          "Ablation studies increase tuning usefulness",
        ],
        negative: ["Less urgent than operational agent or digest work"],
      },
      threshold_decision: "pdf_queue",
      llm_rerank_delta: 0,
      llm_rerank_reasons: [],
      created_at: hoursAgo(125),
    },
  },
  {
    id: "paper-headline-only-triage",
    arxiv_id: "2503.06543",
    version: 1,
    title: "On the Limits of Headline-Only Triage for arXiv Alerts",
    abstract:
      "Some alerting systems rank new papers using only titles and category priors. We show that title-only scoring can miss benchmark, code-release, and methodological nuance that appear in comments and abstracts, leading to unstable triage quality under fast-moving topics.",
    authors: [
      { name: "Elena Petrov", affiliation: "University College London" },
      { name: "Jonas Meyer", affiliation: "Cohere" },
    ],
    categories: ["cs.IR", "cs.AI", "cs.CL"],
    primary_category: "cs.IR",
    comment: "Short paper with analysis over one month of arXiv alerts.",
    published_at: hoursAgo(149),
    updated_at: hoursAgo(149),
    one_line_summary:
      "Title-only triage is cheap, but it misses the metadata signals that make alerts trustworthy.",
    key_points: [
      "Highlights failure cases where titles hide benchmark and code-release signals.",
      "Useful as a counterpoint when designing cheap first-pass scoring.",
      "Empirical scope is narrow but directly relevant.",
    ],
    method_summary:
      "The authors compare title-only alerts to metadata-rich alerts over a month-long arXiv sample.",
    conclusion_summary:
      "Comments and abstract metadata add meaningful stability to alert ranking despite their extra complexity.",
    limitations:
      "The study is short and limited to a narrow category mix.",
    figure_descriptions: [
      "A bar chart compares false negatives under title-only versus metadata-rich scoring.",
    ],
    profile_labels: ["Scientific QA Systems"],
    score: {
      id: "score-headline-only-triage",
      paper_id: "paper-headline-only-triage",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 58,
      topical_relevance: 24,
      prestige_priors: 8,
      actionability: 8,
      profile_fit: 9,
      novelty_diversity: 9,
      penalties: 0,
      matched_rules: {
        positive: [
          "Matches current metadata-first triage work exactly",
          "Provides concrete false-negative examples",
        ],
        negative: ["Short paper with limited evaluation horizon"],
      },
      threshold_decision: "pdf_queue",
      llm_rerank_delta: 0,
      llm_rerank_reasons: [],
      created_at: hoursAgo(140),
    },
  },
  {
    id: "paper-benchmark-memorization",
    arxiv_id: "2503.05987",
    version: 1,
    title: "Benchmark Memorization in Scientific Claim Extraction Models",
    abstract:
      "Scientific claim extraction models often report strong benchmark performance while memorizing repeated phrasing and annotation artifacts. We analyze memorization patterns across three claim extraction datasets and propose evaluation slices that better separate genuine evidence understanding from superficial pattern matching.",
    authors: [
      { name: "Leah Brooks", affiliation: "University of Cambridge" },
      { name: "Tao Meng", affiliation: "Harvard University" },
      { name: "Nikhil Rao", affiliation: "OpenAI" },
    ],
    categories: ["cs.CL", "cs.AI", "stat.ML"],
    primary_category: "cs.CL",
    comment: "Evaluation slices and annotation audit released.",
    published_at: hoursAgo(166),
    updated_at: hoursAgo(166),
    one_line_summary:
      "Shows where claim extraction models memorize annotation artifacts instead of reading evidence.",
    key_points: [
      "Finds repeated benchmark artifacts that inflate claim extraction scores.",
      "Releases evaluation slices for better evidence understanding checks.",
      "Useful background for benchmarking QA and verification work.",
    ],
    method_summary:
      "The paper contrasts standard benchmark metrics with artifact-aware evaluation slices and annotation audits.",
    conclusion_summary:
      "Evidence-sensitive slices expose memorization failure modes hidden by aggregate benchmark scores.",
    limitations:
      "Focused on claim extraction rather than broader agent benchmarks.",
    figure_descriptions: [
      "A breakdown chart shows the share of benchmark gains attributable to repeated templates.",
    ],
    profile_labels: ["Scientific QA Systems"],
    score: {
      id: "score-benchmark-memorization",
      paper_id: "paper-benchmark-memorization",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-scientific-qa",
      score_version: "2026.03.public",
      total_score: 67,
      topical_relevance: 29,
      prestige_priors: 13,
      actionability: 10,
      profile_fit: 9,
      novelty_diversity: 8,
      penalties: -2,
      matched_rules: {
        positive: [
          "Benchmark and verification themes match QA profile",
          "Evaluation slices are actionable for future internal checks",
        ],
        negative: ["Narrowly scoped to claim extraction models"],
      },
      threshold_decision: "rerank",
      llm_rerank_delta: 2,
      llm_rerank_reasons: [
        "Helpful context paper with reusable benchmark lessons, but not the day's strongest operational signal.",
      ],
      created_at: hoursAgo(157),
    },
  },
  {
    id: "paper-distillation-document-vlms",
    arxiv_id: "2503.05100",
    version: 1,
    title: "Practical Distillation Recipes for OCR-Free Document VLMs",
    abstract:
      "OCR-free document VLMs can simplify paper ingestion, but they remain expensive to run at digest scale. We present distillation recipes that preserve table and figure understanding while reducing inference cost, enabling more affordable document-level reasoning for paper monitoring systems.",
    authors: [
      { name: "Juniper Lee", affiliation: "KAIST" },
      { name: "Amir Haddad", affiliation: "NVIDIA" },
      { name: "Sofia Alvarez", affiliation: "University of Illinois Urbana-Champaign" },
    ],
    categories: ["cs.CV", "cs.LG", "cs.AI"],
    primary_category: "cs.CV",
    comment: "Includes cost-per-page comparisons and table extraction evals.",
    published_at: hoursAgo(188),
    updated_at: hoursAgo(188),
    one_line_summary:
      "Distillation recipes that keep document VLM quality while cutting the cost of page-level reasoning.",
    key_points: [
      "Preserves table and figure understanding in smaller OCR-free models.",
      "Makes document-level paper enrichment more affordable.",
      "Useful for future PDF parsing and figure-extraction decisions.",
    ],
    method_summary:
      "The work combines teacher-guided region supervision with cost-aware distillation objectives across page-level tasks.",
    conclusion_summary:
      "Targeted distillation retains the document signals needed for paper enrichment at much lower cost.",
    limitations:
      "The paper studies document VLMs rather than full agent pipelines.",
    figure_descriptions: [
      "A cost-per-page chart shows how distillation shifts the quality-cost frontier for document VLMs.",
    ],
    profile_labels: ["Vision-Language Agents", "Long-Context Efficiency"],
    score: {
      id: "score-distillation-document-vlms",
      paper_id: "paper-distillation-document-vlms",
      workspace_id: DEMO_WORKSPACE_ID,
      profile_id: "profile-long-context",
      score_version: "2026.03.public",
      total_score: 77,
      topical_relevance: 31,
      prestige_priors: 14,
      actionability: 12,
      profile_fit: 8,
      novelty_diversity: 10,
      penalties: -4,
      matched_rules: {
        positive: [
          "Directly lowers future cost for paper enrichment",
          "Includes cost-per-page analysis and table extraction metrics",
        ],
        negative: ["Less directly tied to QA than top-ranked papers"],
      },
      threshold_decision: "digest_candidate",
      llm_rerank_delta: 4,
      llm_rerank_reasons: [
        "Strong follow-on value for the pipeline because it improves document-level reasoning economics.",
      ],
      created_at: hoursAgo(176),
    },
  },
];
