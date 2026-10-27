# dataset/

| File | Rows | Contents |
|---|---|---|
| `sciskillbank_repositories.csv` | 2,200 | The SciSkillBank release: repository metadata, broad domain, model summary, methodology encoding, autonomy level, multi-label workflow stages, primary stage, discipline, and the labels re-annotated from skill files |
| `sciskillbank_umap_all_candidates.csv` | 11,613 | UMAP coordinates of every validly summarized candidate repository, the input to Figure 2 |
| `embeddings/sciskillbank_embeddings_all_candidates_part{1..7}of7.npy` | 11,613 | The 3,072-dimensional summary embeddings the UMAP coordinates were computed from, in seven parts of 1,659 rows |
| `sciskillbank_umap_research.csv` | 2,199 | UMAP coordinates from an earlier embedding run over the research-relevant summaries alone; no figure in the paper uses it |
| `skill_file_retrieval_status.csv` | 2,200 | The skill-file check eight weeks after collection: 1,805 with a `SKILL.md`, 209 reachable with no matching file, 102 with other Claude Code markdown, 84 unretrievable |
| `repository_status_Sept-23-2026.jsonl` | 2,200 | Re-check of every released repository on September 23, 2026: 2,044 still resolve, 156 are gone |
| `skill_file_status_Sept-23-2026.jsonl` | 2,200 | Re-check of the skill files on the same date, with the earlier status in `prior` and the new one in `now` |
| `instability/option_order_labels.csv` | 2,200 | Autonomy label under each of four counterbalanced option orderings, plus the counterbalanced consensus |
| `instability/decoupled_labels.csv` | 2,200 | Methodology and autonomy under released, joint, decoupled and decoupled_v2 elicitation |
| `instability/domain_input_comparison.json` | 3 models | Domain-field sensitivity: identification ranges, conservative bounds, per-model cost and source hashes |
| `instability/*_report.txt` | | The archived run reports of the two perturbation runs, verbatim |
| `instability/manifests/manifest_*.json` | 3 | Per-model run manifests, each recording SHA-256 digests of the nine upstream artifacts the sensitivity runs read |

The release table and the all-candidate UMAP table are byte-identical to the copies in the
paper's supplementary material:

| File | SHA-256 |
|---|---|
| `sciskillbank_repositories.csv` | `fdc2c08325378431aa2fe29f013e3453e0978b046238f552abb04dc1844b26e5` |
| `sciskillbank_umap_all_candidates.csv` | `a5144bce7a299ec0441d5d7ec7bbaa7c5a1ef1b8f8de7b1c8df53fdc049cd643` |

## `sciskillbank_repositories.csv`

One row per GitHub repository. The 2,200 rows are the 331 repositories labeled `research`
and the 1,869 labeled `data_science`. GitHub metadata was collected on April 2 and 3, 2026,
and READMEs on April 4. All labels come from GPT-4o-mini; the paper describes the prompts,
the codebook and how far the labels hold under changes of prompt, model and input.

| Column | Meaning |
|---|---|
| `repo` | `owner/name` on GitHub |
| `html_url` | Repository URL |
| `stars`, `forks` | Counts at collection |
| `description`, `language`, `topics`, `license`, `size_kb`, `default_branch` | GitHub metadata at collection. `topics` is a Python list literal. `license` is the SPDX identifier, empty when the repository has no license field (957 rows) |
| `created_at`, `updated_at`, `pushed_at` | GitHub timestamps, UTC |
| `from_code_search`, `from_repo_search` | Whether the repository was found by file-convention code search (`SKILL.md`, `.claude/`, `CLAUDE.md`), by keyword repository search over names, descriptions and topics, or both (54 rows) |
| `readme_score`, `desc_score`, `total_score` | Weighted keyword score for skill signals in the README and the description (strong terms weigh 3, medium 2, weak 1); `total_score` is their sum, and candidates needed at least 1 |
| `matched_signals` | The keywords that matched, with their weights |
| `readme_length`, `has_readme` | README length in characters, and whether one exists |
| `broad_domain` | `research` or `data_science`, assigned from a ten-category menu |
| `llm_reason` | The model's rationale for the broad domain |
| `skill_summary` | Two-to-four-sentence model summary of the repository. Annotation and embedding both read this summary |
| `methodology_encoding` | `yes` if the skills encode methodological knowledge, `no` if they are procedural wrappers |
| `autonomy_level` | `assistive`, `collaborative`, `delegated` or `autonomous` |
| `workflow_stages` | Comma-separated tags from the 15-stage research workflow scheme; 6,409 tags over 2,199 rows |
| `annotation_reason` | The model's rationale for the three labels above |
| `primary_stage` | A single stage chosen from `workflow_stages`; it colors the right panel of Figure 2 |
| `primary_stage_source` | `llm` when the model chose among several tags (2,108), `sole_tag` when the only tag was taken (91), `no_tags` when there was none (1) |
| `discipline`, `discipline_confidence` | The scientific field the repository serves, and the model's stated confidence |
| `record_valid`, `record_note` | Validity flag and the reason for any flag; see below |
| `methodology_encoding_skillfile`, `autonomy_level_skillfile`, `workflow_stages_skillfile` | The same labels annotated from the repository's skill files instead of the summary, for 1,772 of the 1,805 repositories whose skill files were retrievable eight weeks after collection. Empty otherwise. `workflow_stages_skillfile` is a Python list literal and is empty for 27 of the 1,772 |

**Filtering.** Keep the rows whose `record_valid` is `true` to get the 2,199 usable records
(pandas reads the column as boolean, so `df[df["record_valid"]]`). The one invalid record,
`AppantasyArthurLai/taiwan-hungry-soul`, had its summarization call return an API error: the
stored `skill_summary` is that error string, its summary-based labels (methodology encoding,
autonomy level, workflow stages, primary stage, discipline) were produced from it, and it has
no embedding. Its `broad_domain` was assigned before summarization, and its `*_skillfile`
labels come from its skill files. It is kept for archival continuity.
`record_note` also flags `AetherCore-Dev/ag402`, which is valid but received no workflow-stage
tags and so has an empty `primary_stage`.

## `sciskillbank_umap_all_candidates.csv`

One row per candidate repository with a valid summary, across all broad domains. The
summaries were embedded with OpenAI `text-embedding-3-large` (3,072 dimensions) and projected
to two dimensions with UMAP (cosine distance, 15 neighbors, minimum distance 0.1). The axes and
distances carry no quantitative meaning.

| Column | Meaning |
|---|---|
| `repo` | `owner/name` on GitHub |
| `umap_x`, `umap_y` | UMAP coordinates |
| `broad_domain` | Broad domain as the model returned it. Ten values are on the menu; 21 rows carry an off-menu string (`game_dev`, `productivity` and others), which the paper merges into `other` |
| `stars` | Stars at collection |
| `primary_stage` | Primary workflow stage, filled only for repositories in the release (`research` or `data_science`) |

2,199 of the 2,200 released repositories appear here; the missing one is the invalid record
above. Because the summaries were generated with the broad domain as an input, the layout is
not independent evidence of domain structure.

`sciskillbank_umap_research.csv` has the same columns, for the 2,199 research-relevant
repositories only. It comes from a separate, earlier embedding run over those summaries alone,
whose embeddings are not released.

## `embeddings/`

The OpenAI `text-embedding-3-large` embeddings of the 11,613 valid summaries, as a float32
matrix of shape 11,613 x 3,072 split row-wise into seven `.npy` files of 1,659 rows each, so
that every file stays under GitHub's 25 MiB browser-upload limit. Row *i* of the joined matrix
is the repository in row *i* of `sciskillbank_umap_all_candidates.csv`; the embeddings carry no
repository column of their own. Each row has unit length. To select the research-relevant
corpus, keep the rows whose `broad_domain` in that table is `research` or `data_science`
(2,199 rows).

```python
import numpy as np
X = np.concatenate([np.load(f"dataset/embeddings/"
                            f"sciskillbank_embeddings_all_candidates_part{k}of7.npy")
                    for k in range(1, 8)])          # (11613, 3072) float32
```

Running UMAP on the joined matrix with the settings above plus `random_state=42` and one thread
(umap-learn 0.5.11, on macOS x86_64) gives coordinates equal to the released ones.

The embeddings were stored as float64 after the API call. Every value is exactly
representable in float32, so the float32 release loses nothing: cast back to float64, it
equals the stored matrix element for element.

| File | SHA-256 |
|---|---|
| `..._part1of7.npy` | `ac0cfc2eb476989e76f3c789823a39d07a36335d0a7abdd2d6ec5606df5852ac` |
| `..._part2of7.npy` | `5d3bb5d526cff0f3b47b43f8b0ae5528b28675dc77c81890220c6895f27b48aa` |
| `..._part3of7.npy` | `db0c051031662e8d4d13546ba77c7bb416d03764a9fe6f0b3119bf44cba81510` |
| `..._part4of7.npy` | `d5ed04e5c836166358ed62d1b734ef512a3ba865fe18be8fbf723cb33437eab2` |
| `..._part5of7.npy` | `8593a79dfe615b7df7a115fcc1657471398063a58959e55ff977095012494adb` |
| `..._part6of7.npy` | `d10454efe10f303a2ef478726736601dd3865b7a0ef63d25c931ae75ac93866a` |
| `..._part7of7.npy` | `de65378371a6965be634278e828a201ca3df0bd9c7a7cfac7e32a9e56d2b4622` |

## `instability/`

The label tables behind Figure 4 and Section 5.3, one row per released repository. In
`option_order_labels.csv`, `released` is the released autonomy label; `forward`, `reverse`,
`mid_collab` and `mid_deleg` are the labels under the four option orderings; and
`autonomy_consensus`, `autonomy_agreement` and `order_stable` summarize them. In
`decoupled_labels.csv`, each elicitation structure contributes a methodology (`*_meth`) and an
autonomy (`*_aut`) column. `figures/fig4_measurement_instability.py` recomputes every plotted
value from these two tables. `domain_input_comparison.json` and the three manifests belong to
the domain-field sensitivity experiment of Appendix A.7.

## How this data was filtered for release

All files here except the embeddings come from the paper's supplementary material. The
embeddings were not part of it. In `instability/`, the API cost, budget and approval fields were
removed from the three manifests and `domain_input_comparison.json`, and the cost section from
the two run reports; every result, setting and input digest is unchanged. Each manifest's
`config_sha256` was computed over the original configuration, so it no longer matches the
stored `config`. Left out:

- The embeddings of the earlier research-only run behind `sciskillbank_umap_research.csv`.
- The collected third-party skill-file text that the skill-file re-annotation, the
  input-consistency test and the label-recoverability task read. The skill-file labels are
  kept (the `*_skillfile` columns above).
- API request logs, raw API responses, spend records and credentials.

The model-generated fields (`llm_reason`, `skill_summary`, `annotation_reason`) and the
embedding vectors are part of the dataset as the paper describes it and are kept.

One personal email address in a `description` field was replaced with the literal string
`[email redacted]` (repository `fleurytian/awesome-claude-skills`); see `../REDACTIONS.json`.
Repository owner names are kept, because public GitHub repository identity is the data under
study, and every record links to its public source.
