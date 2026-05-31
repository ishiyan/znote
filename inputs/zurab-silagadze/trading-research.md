# Zurab Silagadze — Trading Research Profile

## Biography

**Zurab Konstantinovich Silagadze** is a theoretical and mathematical physicist based at the **Budker Institute of Nuclear Physics** and **Novosibirsk State University**, Novosibirsk, Russia. He holds Georgian roots and has published 128+ papers on arXiv spanning high-energy physics, quantum mechanics, general relativity, mathematical physics, and physics pedagogy.

His single contribution to quantitative finance — the **Moving Mini-Max** indicator — draws on quantum tunneling concepts to identify local extrema in price series. Despite being his only finance paper, it gained significant traction in the trading community through implementations on MetaTrader 5 and discussions across multiple forums.

**Affiliation:** Budker Institute of Nuclear Physics / Novosibirsk State University, Russia

---

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| Moving Mini-Max | arXiv Feb 2008; IFTA Journal 2011 | Extrema Detection / Smoothing |

**Moving Mini-Max:** Uses a quantum-tunneling-inspired smoothing approach to emphasize local maximums and minimums in price series. The indicator provides inherent smoothing while preserving turning points, making it useful for mechanical trading rules and chart pattern recognition. It applies a potential barrier function (analogous to quantum tunneling probability) to weight recent highs and lows.

---

## TASC Publications

No articles found in the TASC archive (1982–2025).

---

## IFTA Journal Publications

### 2011

| Title | Pages | Description | Link |
|-------|-------|-------------|------|
| Moving Mini-Max – A New Indicator for Technical Analysis | 46–49 | Introduces the Moving Mini-Max indicator using quantum-tunneling-inspired smoothing | [PDF](https://www.ifta.org/assets/docs/d_ifta_journal_11.pdf) |

---

## Academic Papers

### Finance-Related

| Year | Title | Venue | arXiv |
|------|-------|-------|-------|
| 2008/2011 | Moving Mini-Max — a new indicator for technical analysis | IFTA Journal 11, pp. 46–49 | [0802.0984](https://arxiv.org/abs/0802.0984) |

### Selected Physics Papers (showing breadth)

| Year | Title | Venue | arXiv |
|------|-------|-------|-------|
| 2026 | Pauli equation in spaces of constant curvature | Phys. Lett. A 588, 131734 | [2604.27522](https://arxiv.org/abs/2604.27522) |
| 2026 | Astrophysical positronium and Dicke superradiance | Phys. Rev. D | [2602.07489](https://arxiv.org/abs/2602.07489) |
| 2025 | Chukchi Myths perspective on Special Relativity | Eur. J. Phys. 47, 035604 | [2512.06015](https://arxiv.org/abs/2512.06015) |
| 2024 | Supermassive black holes in ekpyrotic universe | Mod. Phys. Lett. A 39, 2450167 | [2503.23847](https://arxiv.org/abs/2503.23847) |
| 2023 | On arXiv moderation system | J. Informetrics 17, 101433 | [2307.11791](https://arxiv.org/abs/2307.11791) |
| 2022 | On Finslerian extension of special relativity | Mod. Phys. Lett. A 37, 2250106 | [2201.12279](https://arxiv.org/abs/2201.12279) |

---

## MQL5 Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5 | investeo | MetaTrader 5 | [Article](https://www.mql5.com/en/articles/238) |

The article by "investeo" implements Silagadze's indicator in MQL5, explaining the quantum tunneling concepts applied to finance. Source code is attached to the article. A code correction for line 225 was later posted by Roberto_Ev in the discussion forum.

---

## Forum Discussions

| Forum | Title | Author | URL |
|-------|-------|--------|-----|
| MQL5 Forum | Discussion of article "Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5" | MetaQuotes | [Thread](https://www.mql5.com/en/forum/3018) |
| MQL5 Forum | New article at mql5.com — Moving Mini-Max (announcement) | MetaQuotes | [Thread](https://www.mql5.com/en/forum/131341) |
| MQL5 Forum | Some new ideas for your next trading system — "Idea 9: moving Mini-Max" | Rogerio Figurelli | [Post](https://www.mql5.com/en/forum/19166/746496#comment_746496) |
| MQL5 Forum | Elite indicators — request to convert Mini-Max to MT4 | derfel | [Post](https://www.mql5.com/en/forum/175037/4585961#comment_4585961) |
| MQL5 Forum | Discussion: Random Walk and the Trend Indicator — suggests testing Mini-Max | Virty | [Post](https://www.mql5.com/en/forum/3434/56991986#comment_56991986) |
| MQL5 Forum | Code correction for Moving Mini-Max line 225 | Roberto_Ev | [Post](https://www.mql5.com/en/forum/3018/56996336#comment_56996336) |

---

## GitHub Repositories

No dedicated repositories found. GitHub search for "moving mini-max", "minimax indicator", "MovingMiniMax", and "silagadze" returned no results.

---

## Photos, Videos & Interviews

| Type | Description | URL | Source |
|------|-------------|-----|--------|
| [URL not found] | Author photo at Budker Institute | — | Likely on institute faculty page |
| [URL not found] | YouTube search returned no video results | — | YouTube |

No publicly accessible photos, videos, or interviews were found through web searches.

---

## Books

No books authored by Silagadze on trading or technical analysis.

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

@online{mql5_investeo_minimax,
  author  = {investeo},
  title   = {Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5},
  url     = {https://www.mql5.com/en/articles/238},
  urldate = {2026-05-28},
  year    = {2011},
  note    = {MQL5 article implementing Silagadze's indicator}
}

@online{mql5_forum_minimax,
  author  = {{MetaQuotes}},
  title   = {Discussion of article "Moving Mini-Max: a New Indicator for Technical Analysis and Its Implementation in MQL5"},
  url     = {https://www.mql5.com/en/forum/3018},
  urldate = {2026-05-28},
  year    = {2011},
  note    = {Forum discussion with code corrections}
}

@online{mql5_figurelli_ideas,
  author  = {Figurelli, Rogerio},
  title   = {Some new ideas for your next trading system --- Idea 9: Moving Mini-Max},
  url     = {https://www.mql5.com/en/forum/19166/746496#comment_746496},
  urldate = {2026-05-28},
  note    = {Forum post recommending Moving Mini-Max}
}
```
