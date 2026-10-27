# Numbers behind Figure 4, and numbers that stayed out of it

Regenerate with `./make_figs.sh`. The script prints every value below to stdout, so
this file can be checked against a run without opening the PDF.

## In the figure

Panel (a) autonomy-level share (%) under each option ordering, n = 2,200:

| level | forward | reverse | collab-first | deleg-first |
|---|---|---|---|---|
| assistive | 13.7 | 16.2 | 29.6 | 51.0 |
| collaborative | 11.6 | 3.3 | 7.8 | 5.8 |
| delegated | 69.8 | 75.0 | 56.2 | 35.1 |
| autonomous | 4.9 | 5.5 | 6.4 | 8.0 |

Panel (b) position effect, same level compared with itself:

| level | leads | does not lead | lift (pp) |
|---|---|---|---|
| assistive | 13.7 | 32.3 | -18.5 |
| collaborative | 7.8 | 6.9 | +0.9 |
| delegated | 35.1 | 67.0 | -31.9 |
| autonomous | 5.5 | 6.4 | -0.9 |

Mean absolute lift 13.0 pp. All four orderings agree on 1,116 of 2,200 repositories (50.7%).

Panel (c) methodology encoding x autonomy level, Cramer's V (bootstrap B = 5,000, seed 20260923):

| elicitation | V | 95% CI |
|---|---|---|
| as released | 0.870 | [0.848, 0.892] |
| joint re-run | 0.863 | [0.840, 0.885] |
| separate calls (v2) | 0.167 | [0.126, 0.211] |
| separate, stages dropped | 0.165 | [0.128, 0.207] |

## Verification against the archived runs

Point estimates are deterministic and reproduce `01_decoupled_report.txt` and
`02_option_order_report.txt` exactly, to every digit printed there. Bootstrap intervals
are recomputed here under seed 20260923 and differ from the archived intervals by at most
0.002, which is resampling noise under a different seed, not a discrepancy.

## Deliberately not in the figure

- **`released vs forward` agreement (56.3%, kappa 0.288).** `02_option_order_report.txt`
  states this row is not a drift control: the released labels come from the
  three-dimension joint prompt while every ordering condition is a single-dimension
  prompt, so the row confounds order with prompt structure. Panel (a) therefore shows
  only the four counterbalanced orderings, which are the clean comparison.
- **The autonomous share across single-dimension prompts (4.9-8.0%).** Real, and already
  in the manuscript, but it is a fifth number on a panel that is about the distribution
  reshuffling, and it invites reading the 99.6% headline as refuted rather than as
  prompt-dependent. It belongs in prose.
- **Cross-model prevalence ranges** (47.33-48.61% GPT-4o, 50.15-50.21% GPT-5,
  52.56-58.18% GPT-4o-mini against 66.24% archived). These are identification ranges over
  unresolved labels, not confidence intervals, and plotting them beside bootstrap
  intervals in panel (c) would put two incompatible bracket semantics on one axis. They
  stay in Table 3.
