# SciSkillBank: A Dataset of Claude Code Skills for Scientific Research

Code and data for the paper of the same title. It contains the SciSkillBank
dataset, 2,200 research-relevant GitHub repositories of Claude Code skills with LLM annotations
of workflow stage, methodology encoding and autonomy; the 3,072-dimensional summary
embeddings; and the data and code that regenerate Figure 2, the UMAP landscape of repository
summaries ([PDF](figures/fig2_umap.pdf)).

## Contents

| Path | What it is |
|---|---|
| `data/annotation/sciskillbank_repositories.csv` | The dataset: 2,200 repositories, 37 columns |
| `data/analysis/sciskillbank_umap_all_candidates.csv` | UMAP coordinates of all 11,613 validly summarized candidates, the input to Figure 2 |
| `data/analysis/embeddings/` | The `text-embedding-3-large` embeddings of those 11,613 summaries (float32, seven parts) |
| `code/fig2_umap.py` | Regenerates Figure 2 from the UMAP table |
| `code/umap_projection.py` | Loads the embeddings and recomputes the UMAP table from them |
| `figures/` | Figure 2 as PDF: both panels together, and each panel alone |
| `data/README.md` | Column dictionary, embedding layout, record-validity flags, redaction note |
| `code/README.md` | Script outputs, fonts, and how exact the reproduction is |

## Reproduce Figure 2

```bash
pip install -r requirements.txt
python3 code/fig2_umap.py
```

This rewrites the three PDFs in `figures/` and prints the counts behind the figure. It needs no
network, GPU or API key, and runs in under ten seconds. `python3 code/fig2_umap.py --png` also
writes the two panels as the PNGs embedded in the paper; on macOS with Helvetica Neue they are
pixel-identical to the figure in the paper.

## Recompute the UMAP coordinates from the embeddings

```bash
python3 code/umap_projection.py
```

This joins the seven embedding parts, runs UMAP with the settings of the original analysis
(cosine distance, 15 neighbors and minimum distance 0.1, as stated in the paper, plus
`random_state=42` and one thread), and compares the result with
`data/analysis/sciskillbank_umap_all_candidates.csv`. With the pinned versions on macOS
(x86_64), all 11,613 rows come out equal to the released coordinates. It takes about 90
seconds on a laptop CPU.

## Using the dataset

With pandas (not needed for the figure):

```python
import pandas as pd

df = pd.read_csv("data/annotation/sciskillbank_repositories.csv")
df = df[df["record_valid"]]                          # 2,199 usable records
df["broad_domain"].value_counts()                    # research, data_science
df["autonomy_level"].value_counts()
df["workflow_stages"].str.split(",").explode().value_counts()
```

Filter on `record_valid`: one record's summary is an API error string, so its summary-based
labels are invalid. The labels are model outputs, and the paper reports how far they move under
changes of prompt, model and input; read those results before using the labels record by
record.

## What this release leaves out

The two dataset tables come from the paper's supplementary material; the
embeddings, the two scripts and the figure PDFs were not part of it. The rest of the
supplementary material is left out: the annotation-pipeline scripts, the perturbation
experiments and their label tables, the input-consistency study, the skill-file retrieval
checks, the label-recoverability task, the blinded validation instrument, the research-only
UMAP table, and the script that regenerates Figure 4. It contains no notebooks, API keys,
environment files, API request logs or spend records. See `data/README.md` and
`code/README.md` for what was filtered in each folder.

## License

CC BY 4.0 for the authors' contributions, data and code alike; see `LICENSE`. Repository
metadata is not relicensed: content at each linked repository remains governed by that
repository's own license, and 957 of the 2,200 repositories carry no license field.
