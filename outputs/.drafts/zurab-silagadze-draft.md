# Zurab Silagadze — Deep Research Brief

## Executive Summary

Zurab Karlovich Silagadze is a senior research physicist at the Budker Institute of Nuclear Physics (BINP) and Novosibirsk State University, Russia. Active since the early 1980s, he has published 296 papers (INSPIRE-HEP count; 203 on arXiv) spanning experimental e+e- physics (SND collaboration), mirror matter/dark matter theory, Finsler geometry, quantum gravity phenomenology, physics education, and popular science. His single contribution to quantitative finance — the **Moving Mini-Max** indicator (arXiv:0802.0984, IFTA Journal 2011) — applies quantum tunneling concepts to detect local price extrema with inherent smoothing. Despite modest adoption (6 citations, one MQL5 implementation, no major platform ports), the paper bridges physics and technical analysis in an intellectually original way.

---

## Biography

| Field | Detail |
|-------|--------|
| **Full name** | Zurab Karlovich Silagadze |
| **Affiliation** | Budker Institute of Nuclear Physics (BINP), Novosibirsk, Russia |
| **Teaching** | Novosibirsk State University (NSU) |
| **Office** | BINP Building 1, Room 253 |
| **Email** | Z.K.Silagadze@inp.nsk.su |
| **Phone** | +7(3832) 39-42-05 |
| **Education** | Tbilisi State University, Georgia (earliest publications 1981–82) |
| **Career start** | ~1987 at BINP (INP Novosibirsk preprints) |
| **Visiting positions** | JINR Dubna (mid-1990s), SLAC (1993) |
| **Total publications** | 296 (INSPIRE-HEP) / 203 (arXiv) |
| **Publication span** | 1981–2026 (45 years) |
| **Estimated birth** | ~1957–1960 (based on 1981 first publication from Tbilisi) |

Silagadze is a member of the **SND (Spherical Neutral Detector) Collaboration** — one of the main experiments at the VEPP-2M and VEPP-2000 electron-positron colliders at BINP. He also maintains a popular science blog at "Science First Hand" (scfh.ru) and has authored multiple physics textbooks in Russian. [1]

---

## Research Areas — Category Breakdown

### 1. SND/VEPP Experimental Physics (~100+ papers)
The largest portion of his output. Precision measurements of e+e- annihilation cross sections at low energies, crucial for muon g-2 calculations and hadron spectroscopy. Key channels: π+π-, K+K-, ηγ, ωπ⁰, nn̄, and φ meson decays. [2]

### 2. Mirror Matter / Dark Matter (~15 papers)
A signature theoretical theme. His 1995 paper "Neutrino mass and the mirror universe" (127 citations) is his most-cited solo work. Other highlights: "Do mirror planets exist in our solar system?", "TeV scale gravity, mirror universe, and... dinosaurs", "Mirror dark matter discovered?", "Thorne-Żytkow objects with mirror neutron star cores?" [3]

### 3. Physics Pedagogy (~25-30 papers)
Prolific educator: "Relativity without tears" (78 pp comprehensive SR tutorial), "Chukchi Myths perspective on Special Relativity", "Sliding rope paradox", "Dog-and-rabbit chase problem", multiple problem books in Russian (mechanics, SR). [4]

### 4. Finsler Geometry / Very Special Relativity (~8 papers)
Extensions of special/general relativity using Finsler geometry, including "On Finslerian extension of Schwarzschild metric" and "Finsler space-time in light of Segal's principle". [5]

### 5. Quantum Gravity Phenomenology (~10 papers)
"Quantum gravity, minimum length and Keplerian orbits", "Non-local imprints of gravity on quantum theory", Planck-scale deformations of classical mechanics. [6]

### 6. Quantum Mechanics / Koopman-von Neumann (~8 papers)
"Evading Quantum Mechanics à la Sudarshan", Lévy-Leblond equation, Berry phase calculations, Pauli equation in curved spaces. [7]

### 7. HEP Phenomenology (~15 papers)
"Feynman's derivation of Maxwell equations and extra dimensions", "SO(8) colour as origin of generations", B-factory spectroscopy (218 citations). [8]

### 8. Astrophysics / Cosmology (~10 papers)
Positronium superradiance, Schumann resonances and gravitational waves, ekpyrotic universe and black holes. [9]

### 9. Interdisciplinary / Unconventional (~10 papers)
Technical analysis (Moving Mini-Max), "Visceral theory of sleep" (neuroscience), "Citation entropy" (scientometrics), "LHC card games: retrocausality?", "SETI and muon collider", arXiv moderation critique. [10]

---

## Most-Cited Papers

| # | Title | Citations | Year | arXiv |
|---|-------|-----------|------|-------|
| 1 | BaBar Technical Design Report | 330 | 1995 | — |
| 2 | Update of e+e- → π+π- (SND, 400–1000 MeV) | 289 | 2006 | hep-ex/0605013 |
| 3 | Spectroscopy at B-factories using hard photon emission | 218 | 1999 | hep-ph/9910523 |
| 4 | φ(1020) → π⁰π⁰γ decay | 172 | 2000 | hep-ex/0005017 |
| 5 | Dominant two-loop EW contributions to muon g-2 | 160 | — | — |
| 6 | Neutrino mass and the mirror universe | 127 | 1995 | hep-ph/9503481 |
| 7 | e+e- → nn̄ at VEPP-2000 | 123 | 2014 | 1410.3188 |

---

## The Moving Mini-Max Indicator

### Overview

The Moving Mini-Max (MMM) is a technical analysis indicator that uses an analogy with **quantum mechanical tunneling** (specifically Gamow's theory of alpha decay) to identify local extrema in price series with built-in smoothing. [11]

### Mathematical Formulation

Given a price series `S` over a window of size `n` with smoothing parameter `m`:

**1. Transition probabilities** (mimicking tunneling through price barriers):

```
Q(i,i+1) = Σ_{k=1}^{m} exp(2*(S[i+k] - S[i]) / (S[i+k] + S[i]))
Q(i,i-1) = Σ_{k=1}^{m} exp(2*(S[i-k] - S[i]) / (S[i-k] + S[i]))
```

**2. Normalized probabilities:**

```
P(i,i+1) = Q(i,i+1) / (Q(i,i+1) + Q(i,i-1))
P(i,i-1) = Q(i,i-1) / (Q(i,i+1) + Q(i,i-1))
```

**3. Recurrence relation:**

```
u[i] = (P(i,i-1) / P(i,i+1)) * u[i-1],  u[0] = 1
```

**4. Normalization:** `uSi[i] = u[i] / Σu[j]`

- **uSi** emphasizes local **maxima** (positive exponent variant)
- **dSi** emphasizes local **minima** (negative exponent variant)
- Parameter `m` controls "mass" of the quantum ball: larger m = heavier = less tunneling = more smoothing
- Requires `n + 2m` price bars; lags by `m` bars [12]

### Interpretation

The quantum ball metaphor: imagine dropping a ball onto the price landscape. A classical ball gets trapped in local valleys. A quantum ball has nonzero probability of tunneling through barriers to find the deepest well (true minimum). The indicator computes the probability distribution of where the quantum ball "settles," naturally emphasizing genuine extrema while smoothing out noise. [11]

### Applications
- Support/resistance identification
- Trend direction detection (spread between uSi and dSi peaks)
- Chart pattern recognition via inherent smoothing

### Known Limitations
- **Repaints heavily** — recalculates the entire history on each new bar
- Community consensus: "looks beautiful on history, but in practice sometimes guesses direction, sometimes not; arrows get removed and redrawn" [13]
- Limited real-time trading utility due to repainting behavior

---

## Publication History

| Year | Venue | Notes |
|------|-------|-------|
| 2008 | arXiv:0802.0984 (v1) | First submission, 10 pages, 3 figures |
| 2011 | arXiv:0802.0984 (v2) | Revised version |
| 2011 | IFTA Journal 11, pp. 46–49 | Published version |

---

## Citations of the Moving Mini-Max Paper (6 total)

| # | Title | Authors | Year | Venue |
|---|-------|---------|------|-------|
| 1 | Automatic one two three | S. Maier-Paape | 2015 | Quantitative Finance |
| 2 | Classification of Symbolic Financial Data on Forex | J. Kozak, P. Juszczuk, K. Kania | 2019 | Int'l Conf. Computational Science (Springer) |
| 3 | Supporting decisions on Forex using fuzzy approach | P. Juszczuk, L. Kruś | 2020 | J. Automation, Mobile Robotics & Intelligent Systems |
| 4 | kNN in Pattern Classification on Financial Time Series | I. Makarov, K. Maria, Z. Ekaterina | 2021 | IEEE Int'l Conf. |
| 5 | Quantifying Volatility Using Moving Average Envelope and Bollinger Bands | A. Chakrabarty, A. Majumdar | 2024 | Institutions and Economies |
| 6 | Prognozowanie cen akcji za pomocą indeksu DJIA | P.T. Czaja | 2012 | Przestrzeń, Ekonomia, Społeczeństwo |

---

## Implementations

### MQL5 (Primary Implementation)

| Field | Detail |
|-------|--------|
| **Article** | [Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5](https://www.mql5.com/en/articles/238) |
| **Author** | investeo (Poland) |
| **Year** | 2011 |
| **Source file** | movingminimax.mq5 (7.34 KB) |
| **Forum** | [Discussion thread](https://www.mql5.com/en/forum/3018) — 44 comments, 5 pages |

Notable forum contributions:
- **Alexey Subbotin**: Parameter `m` = inverse ball mass; suggested using volume data to dynamically adjust `m`; proposed quadratic price transformation for better energy representation [14]
- **Roberto_Ev**: Code correction for line 225 [15]
- **Siarhei Kudrytski (2024)**: Confirmed repainting behavior [13]

### Other Platforms

| Platform | Status |
|----------|--------|
| GitHub | No dedicated repositories found |
| TradingView / Pine Script | No confirmed implementations |
| Python / PyPI | No packages found |
| Other languages | None discovered |

The indicator remains essentially an **MQL5-only curiosity**. The repainting behavior has likely discouraged wider adoption. [16]

---

## Photos & Media

| Type | URL | Source |
|------|-----|--------|
| Photo (headshot) | https://www.inp.nsk.su/~silagadz/silagadze.jpg | BINP personal page |
| Personal page | https://www.inp.nsk.su/~silagadz/ | BINP |
| Publication list | https://www.inp.nsk.su/~silagadz/publ.html | BINP |
| Popular writings | https://www.inp.nsk.su/~silagadz/pop.html | BINP |
| Blog | https://scfh.ru/blogs/O_fizike_i_fizikah/ | Science First Hand |
| [URL not found] | — | No YouTube videos or interviews found |
| [URL not found] | — | No Wikipedia article exists |

---

## Key Collaborators

- **Robert Foot** (University of Melbourne) — mirror matter / dark matter
- **SND Collaboration** (~50+ physicists at BINP) — e+e- measurements
- **Olga Chashchina** — quantum mechanics, KvN formalism
- **P.-M. Zhang, P.A. Horvathy** — gravitational memory, flyby effects
- **Abhijit Sen** — Finsler geometry
- **Alina Sagaydak** — recent experimental papers

---

## Open Questions

1. **Exact birth year** — not publicly available; estimated ~1957–1960 from first publication (1981, Tbilisi)
2. **Google Scholar h-index** — profile may exist but was not accessible
3. **ORCID** — likely 0000-0002-1594-4783 but unverified
4. **Whether he trades** — no evidence that Silagadze actually uses technical analysis; the paper appears to be an intellectual exercise by a physicist

---

## Sources

[1] Personal page, Budker Institute of Nuclear Physics. https://www.inp.nsk.su/~silagadz/ (verified)

[2] INSPIRE-HEP search: author Z.K. Silagadze. http://inspirehep.net/search?p=find+a+silagadze (verified, 296 papers)

[3] Silagadze, Z.K. "Neutrino mass and the mirror universe." arXiv:hep-ph/9503481 (1995). 127 citations.

[4] Silagadze, Z.K. "Relativity without tears." arXiv:0708.0929 (2007).

[5] Silagadze, Z.K. "On the Finslerian extension of the Schwarzschild metric." arXiv:1007.4632 (2010).

[6] Silagadze, Z.K. "Quantum gravity, minimum length and Keplerian orbits." arXiv:0901.1258 (2009).

[7] Silagadze, Z.K. "Lévy-Leblond equation and Eisenhart-Duval lift in KvN mechanics." arXiv:2308.16201 (2023).

[8] Silagadze, Z.K. "Spectroscopy at B-factories using hard photon emission." arXiv:hep-ph/9910523 (1999). 218 citations.

[9] Silagadze, Z.K. "Astrophysical positronium and Dicke superradiance." arXiv:2602.07489 (2026).

[10] Silagadze, Z.K. "On arXiv moderation system." J. Informetrics 17, 101433 (2023). arXiv:2307.11791.

[11] Silagadze, Z.K. "Moving Mini-Max — a new indicator for technical analysis." arXiv:0802.0984 (2008); IFTA Journal 11 (2011), 46–49.

[12] investeo. "Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5." MQL5 Articles, 2011. https://www.mql5.com/en/articles/238

[13] Siarhei Kudrytski. Forum comment on repainting behavior. MQL5 Forum, 2024. https://www.mql5.com/en/forum/3018

[14] Alexey Subbotin. Forum comment on parameter interpretation. MQL5 Forum, 2011. https://www.mql5.com/en/forum/3018

[15] Roberto_Ev. Code correction for line 225. MQL5 Forum, 2024. https://www.mql5.com/en/forum/3018/56996336#comment_56996336

[16] MQL5 forum discussion thread. https://www.mql5.com/en/forum/3018 (44 comments across 5 pages)

---

## BibTeX

```bibtex
@article{Silagadze2008MiniMax,
  author       = {Silagadze, Z. K.},
  title        = {Moving Mini-Max -- a new indicator for technical analysis},
  journal      = {IFTA Journal},
  volume       = {11},
  pages        = {46--49},
  year         = {2011},
  eprint       = {0802.0984},
  archiveprefix = {arXiv},
  primaryclass = {q-fin.ST},
  url          = {https://arxiv.org/abs/0802.0984},
  note         = {Originally submitted February 2008; ISSN 2409-0271}
}

@article{Silagadze1995Mirror,
  author       = {Silagadze, Z. K.},
  title        = {Neutrino mass and the mirror universe},
  journal      = {Physics of Atomic Nuclei},
  volume       = {60},
  pages        = {272--275},
  year         = {1997},
  eprint       = {hep-ph/9503481},
  archiveprefix = {arXiv},
  note         = {127 citations}
}

@article{Silagadze1999BFactory,
  author       = {Silagadze, Z. K.},
  title        = {Spectroscopy at B-factories using hard photon emission},
  journal      = {Nuclear Physics B -- Proceedings Supplements},
  year         = {2000},
  eprint       = {hep-ph/9910523},
  archiveprefix = {arXiv},
  note         = {218 citations}
}

@article{MaierPaape2015Auto123,
  author       = {Maier-Paape, Stanislaus},
  title        = {Automatic one two three},
  journal      = {Quantitative Finance},
  year         = {2015},
  publisher    = {Taylor \& Francis},
  note         = {Cites Moving Mini-Max}
}

@inproceedings{Kozak2019Classification,
  author       = {Kozak, Jan and Juszczuk, Przemys{\l}aw and Kania, Krzysztof},
  title        = {Classification of the Symbolic Financial Data on the Forex Market},
  booktitle    = {Int'l Conf. on Computational Science},
  year         = {2019},
  publisher    = {Springer},
  note         = {Cites Moving Mini-Max}
}

@article{Juszczuk2020Fuzzy,
  author       = {Juszczuk, Przemys{\l}aw and Kru{\'s}, Lech},
  title        = {Supporting decisions on the Forex market using fuzzy approach},
  journal      = {Journal of Automation, Mobile Robotics and Intelligent Systems},
  year         = {2020},
  note         = {Cites Moving Mini-Max}
}

@online{mql5_investeo_minimax,
  author       = {investeo},
  title        = {Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5},
  url          = {https://www.mql5.com/en/articles/238},
  urldate      = {2026-05-28},
  year         = {2011},
  note         = {MQL5 article with full source code}
}

@online{mql5_forum_minimax,
  author       = {{MetaQuotes}},
  title        = {Discussion of article "Moving Mini-Max"},
  url          = {https://www.mql5.com/en/forum/3018},
  urldate      = {2026-05-28},
  year         = {2011},
  note         = {44 comments, includes code corrections and parameter discussion}
}

@online{silagadze_binp_page,
  author       = {Silagadze, Zurab K.},
  title        = {Personal page at Budker Institute of Nuclear Physics},
  url          = {https://www.inp.nsk.su/~silagadz/},
  urldate      = {2026-05-28},
  note         = {Includes publication list and contact info}
}
```
