# figures/

| File | What it is | Needs |
|---|---|---|
| `fig2_umap.py` | Draws Figure 2 from the released UMAP coordinates | numpy, matplotlib |
| `fig4_measurement_instability.py`, `make_figs.sh` | Draws Figure 4 from the perturbation label tables | matplotlib |
| `vizstyle.py` | Palette and helpers shared by the Figure 4 script | |
| `TEXT_FINDINGS.md` | The numbers behind Figure 4, and the numbers deliberately kept out of it | |
| `fig2_umap.pdf`, `fig2_left_all_domains.pdf`, `fig2_right_research_stages.pdf` | Figure 2 as written by `fig2_umap.py` | |
| `fig2_left_all_domains.png`, `fig2_right_research_stages.png` | The two Figure 2 panels as embedded in the paper | |

Neither script makes network, GPU or API calls, and both finish in seconds.

## Figure 2: `fig2_umap.py`

```bash
python3 figures/fig2_umap.py          # from the repository root
python3 figures/fig2_umap.py --png    # also write the two panel PNGs
```

It reads only `dataset/sciskillbank_umap_all_candidates.csv` and writes into this folder:

| File | Contents |
|---|---|
| `fig2_umap.pdf` | Both panels side by side, as in the paper |
| `fig2_left_all_domains.pdf` | Left panel: all 11,613 repositories, research and data science highlighted, labels at the density peak of each broad domain with at least 150 repositories |
| `fig2_right_research_stages.pdf` | Right panel: the 2,199 research-relevant repositories colored by primary workflow stage; the three most frequent stages in color, the other twelve in dark grey, stages with at least 40 repositories labeled |
| `fig2_left_all_domains.png`, `fig2_right_research_stages.png` | With `--png` only: the two panels at 400 dpi, the form embedded in the paper |

The script prints every count behind the figure: repositories per broad domain, including the
21 rows with an off-menu domain string (10 distinct values); repositories per primary stage
and which three are colored; and which labels were drawn or dropped for lack of space. No
label is dropped.

In the PDFs the axis titles are text, the on-plot labels are vector outlines (drawing their
white halo converts them), and the points are rasterized at 400 dpi. Repeated runs produce
byte-identical PDFs.

The script asks for Helvetica Neue, then Helvetica, Arial and DejaVu Sans. On macOS with
Helvetica Neue, matplotlib 3.10.7 and numpy 2.2.6, the two `--png` panels are pixel-identical
to the two images in the paper's PDF. On a system without Helvetica Neue the glyphs change,
but point positions and label positions do not, because label placement uses an estimate of
label width rather than the rendered text.

## Figure 4: `fig4_measurement_instability.py`

```bash
./figures/make_figs.sh                # writes figures/fig4_measurement_instability.pdf
```

It reads only `dataset/instability/option_order_labels.csv` and
`dataset/instability/decoupled_labels.csv`. Every plotted value is recomputed from these
per-repository label tables rather than hardcoded, and the script prints all of them to stdout,
so the figure can be audited against `TEXT_FINDINGS.md` without opening the PDF. The point
estimates reproduce the archived run reports in `dataset/instability/` exactly; bootstrap
intervals are recomputed under a stated seed. The output shows the same values as Figure 4 in
the paper; the figure in the paper was rendered at a slightly shorter height.

## How this folder was filtered for release

`fig4_measurement_instability.py`, `vizstyle.py`, `make_figs.sh` and `TEXT_FINDINGS.md` come
from the paper's supplementary material, where the script was named
`fig5_measurement_instability.py`; it was renamed to match the figure's number in the paper, and
its docstring now names the runs that wrote its input tables rather than internal file paths.
`fig2_umap.py` is rewritten from the version that produced the paper's figure: it reads the
released CSV instead of internal working tables, writes into this folder, adds the PDF output and
the printed counts, and changes nothing that affects the PNG output, which the pixel comparison
above confirms. The scripts for the other figures in the paper are not included.
