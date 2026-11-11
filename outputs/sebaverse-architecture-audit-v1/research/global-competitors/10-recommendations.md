# 10 — Recommendations and architecture handoff

## Recommended direction

**H — decision proposal:** an assessment-led, curriculum-grounded tutor with one conversational orchestrator, explicit learning evidence and reviewed content. Start with one curriculum slice. Use original engineering and reusable mathematical/scheduling components; avoid recreating competitor platforms or adopting their scale of infrastructure.

The ranking below is qualitative founder judgment, not a measured scoring model. Value assumes correct content and effective implementation. Evidence strength describes support for the underlying mechanism or disclosed pattern, not guaranteed Egypt-specific outcomes. Cost includes authoring/review effort, not just inference.

| Rank / capability | Educational value | Complexity | Evidence strength | Cost | Maintainability | Solo-founder fit |
|---|---|---|---|---|---|---|
| 1. Reviewed curriculum and item provenance | high | medium | strong reliability rationale | medium authoring | high with narrow scope | high |
| 2. Independent checks and evidence ledger | high | low–medium | strong assessment rationale | low runtime | high | high |
| 3. Original misconception-linked items | high | medium | product/trial support, local validation needed | medium educator effort | high if versioned | high |
| 4. Bounded dialogue with verified grading tools | high | medium | concrete technical disclosures | measured moderate | high | high |
| 5. Small prerequisite graph and reasoned selection | high | medium | established assessment tradition | low runtime | high with review | high |
| 6. Retrieval practice and delayed checks | high | low | strong bounded pedagogical evidence | low | high | high |
| 7. Egyptian Arabic/English text and controlled voice | potentially high locally | medium–high | local quality unresolved | variable | medium | medium |
| 8. Human quality review, regression and rollback | high reliability value | medium | technical/process evidence | review workload | high | high if scoped |
| 9. Parent digest and teacher override | medium–high | low–medium | practical design, learning effect unproven | low–medium | high | high |
| 10. Cost and latency instrumentation | enables viability | low–medium | operational necessity | low instrumentation | high | high |
| Later: calibrated BKT/IRT | uncertain incremental value | medium | mature methods, local gain unknown | low–medium | medium | conditional |
| Later: learned scheduling / DKT / RL | uncertain incremental value | high | predictive research, policy gains uncertain | higher data/ops | low–medium | low initially |
| Later: fine-tuning or agent teams | unproven incremental value | high | task dependent | high review/data | low–medium | low initially |

## Phases and advancement gates

**Phase 0 — planning and rights.** Choose target grade, subject and syllabus version; identify educator review capacity and authorized materials. Define minor/guardian permissions, processor handling, retention and safeguarding responsibilities. Establish a variable-cost ceiling and a realistic usage scenario. No product implementation is included in this research assignment.

**Phase 1 — narrow pilot design.** Specify a small set of original items and explanations, graph edges, independent checks, state-update rules, tutor states and retrieval provenance. Define Arabic/English evaluation cases. Text plus controlled voice is a candidate configuration, subject to measured child comprehension and cost.

**Phase 2 — monitored use and measurement.** Inspect errors, delayed independent performance, voluntary use, parent understanding, review workload and full session cost. Correct content before adding algorithm complexity. Stop affected activities when severe errors appear.

**Phase 3 — evidence-driven expansion.** Add curricula or a more complex predictor only when baseline quality, content governance and support capacity permit. Neural tracing and model updates require explicit comparative evidence. Teacher authoring/classroom intelligence can follow stable individual learning workflows.

## Audit priorities for a future supplied repository

| Priority | Inspect | Reviewable evidence / acceptance |
|---|---|---|
| P0 | child/tenant identity and retrieval access | synthetic cross-student reads denied, audited access roles |
| P0 | scoring and mastery mutation | one event traced end-to-end; assisted/ambiguous responses cannot count as independent mastery |
| P0 | material rights and curriculum identity | source manifest, edition/year mapping and educator approval |
| P0 | mathematical/content correctness | reviewed answer keys, tool edge cases and incident quarantine |
| P0 | privacy and safeguarding | consent purpose mapping, processor inventory, deletion trace and owned escalation route |
| P1 | uploaded-content injection | adversarial documents cannot alter authorization or tool policy |
| P1 | voice recovery | cancellation and ambiguous speech do not score the wrong turn |
| P1 | release lineage | prompt/model/content/policy/index version manifest and demonstrated rollback |
| P1 | cost/latency | session-level usage reconciled to provider billing; heavy-use scenario tested |
| P2 | adaptive model evaluation | student/time/item-family holdouts, calibration and independent retention baseline |

These are future acceptance criteria, not findings that an existing repository fails them.

## Structured handoff to architecture planning

**Inputs ready:** competitor evidence pack, conservative mechanism comparison, three-loop design, event-contract proposal, orchestration/memory diagram, candidate components and phased ranking.

**Decisions still required:** first curriculum slice; target age band; available content rights; educator/safeguarding owner; legal/privacy launch requirements; maximum variable cost; preferred voice usability targets; pilot success criteria and measurement window. None prevents this research, but each affects implementation planning.

**Planning artifacts to produce next:** domain model and curriculum identifiers; architecture decision records; rights/processor matrix; content-review workflow; learning-event/state specification; threat and failure model; evaluation protocol; cost model; phased delivery estimate. Review these before product development.

**Unresolved empirical questions:** whether dialect voice adds enough learning value over text/read-aloud; whether additional personal memory helps; how well misconception probes discriminate causes; whether BKT improves on transparent rules; whether delayed transfer improves; whether the intended price can fund voice and human review. Convert each into a bounded test with an owner and decision criterion.
