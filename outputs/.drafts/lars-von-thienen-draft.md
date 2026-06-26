# Deep Research: Lars von Thienen — The Dynamics of Market Cycle Analysis

## Executive Summary

Lars von Thienen is a German cycle analyst, serial entrepreneur, and honorary commercial judge who has developed a distinctive "dynamic" approach to financial market cycle detection using digital signal processing (DSP) and genetic algorithms. He is the author of a two-volume book series *Decoding The Hidden Market Rhythm* (WhenToTrade series), has published 8 articles in Trader's World Magazine, hosts a daily cycle analysis Substack (3,000+ subscribers), and serves as a Board Member of the Foundation for the Study of Cycles (FSC) — a non-profit originally founded by Edward R. Dewey in 1941. His work builds on J.M. Hurst, John Ehlers, and B.J. Millard, but departs from their "static" cycle models by emphasizing real-time adaptive dominant-cycle detection at the right edge of the chart. He has a positive reputation within the niche cycle analysis community, with no detected criticism or controversy. His commercial platform WhenToTrade.com is in the process of merging into the FSC.

---

## 1. Biography and Professional Background

### 1.1 Education

Lars von Thienen earned a degree in **Industrial Engineering and Business Management** (Wirtschaftsingenieurwesen) from the **NORDAKADEMIE** — University of Applied Sciences in Hamburg, in cooperation with the **Technische Universität Hamburg-Harburg**. [1][2]

### 1.2 Career Timeline

| Period | Role | Organization |
|--------|------|-------------|
| 1999–present | CEO / Managing Director | bps business process solutions GmbH, Hamburg [3] |
| 2005–present | Founder & CEO | WhenToTrade.com (cycle analysis software) [4] |
| 2015–present | Founder | Noggle AG (knowledge management / desktop search) [5] |
| 2012–present | Board Member | Aequitas Group [5] |
| 2004/2005–present | Honorary Commercial Judge (Handelsrichter) | Landgericht Hamburg (appointed by German Minister of Justice) [1] |
| 2020–present | Board of Directors | Foundation for the Study of Cycles (FSC) [6] |

Earlier in his career, he worked as a programmer and scientist, supporting leading German DAX companies with digital and business strategy as a large-scale project and IT manager. [2]

### 1.3 Additional Professional Roles

- **Vorstand (Board Member)** of e-ThinkTank e.V. [3]
- **Founder/CEO** of WhenToTrade.com, which developed the first cloud-based cycle detection engine [4]
- Contributes as the **cycle detection engine developer** at the core of TradingVision software [7]
- Has US patents in digital signal processing algorithms [8]

### 1.4 Awards & Recognition

- **"The 50 Most Influential Business Leaders in Tech 2021"** — Insights Success [9]
- **Finalist, The Technical Analyst Awards 2022** — Best Specialist Product/Research & Most Innovative New Product (for FSC Cycles App/WTT technology) [10]

### 1.5 Non-Trading Publications

Von Thienen also authored a German-language business book outside trading:
- *Lean IT-Management: Was die IT aus Produktionssystemen lernen kann* — Gabler Verlag, 2012, ISBN 3834929107 [11]
- Chapter contribution to *CIO Handbuch 2012/2013* — Symposion Publishing [5]

---

## 2. Books: "Decoding The Hidden Market Rhythm" (WhenToTrade Series)

### 2.1 Publication History

The work originated as a single self-published volume in 2010 (~240 pages). For the second edition (2014), it was split into two volumes and substantially expanded. [12][13]

| Edition | Title | Year | ISBN | Pages | Format | Notes |
|---------|-------|------|------|-------|--------|-------|
| 1st | Single volume (self-published) | 2010 | N/A | ~240 | Paperback | Original release |
| 2nd | Part 1: Dynamic Cycles | 2014 | 9781499283495 | 236 | Paperback | Split from single volume |
| 2nd | Part 2: Metonic Cycles | 2014 | 9781499562590 | 238 | Paperback | Expanded standalone |
| 3rd | Part 1: Dynamic Cycles (revised) | 2017 | 9781974658244 | 324 | Paperback & Kindle | Added source code repository |
| 3rd | Part 2 (no 3rd edition published) | — | — | — | — | Kindle edition released Sep 2017 |

**Part 3 (Genetic Algorithm & Cycles)** was referenced in forewords but never released as a standalone book. The genetic algorithm content was instead made available through the WTT Charting Module software. [12]

### 2.2 Part 1: Dynamic Cycles — Core Concepts

- **Dynamic vs. static cycles:** The central thesis is that market cycles are not static/repeating but evolve over time. Von Thienen's approach detects the current "dominant cycle" (wavelength, phase, amplitude) in real-time at the right edge of the chart, updating as new data arrives. [14]
- **Digital Signal Processing (DSP):** Uses FFT, DFT-Goertzel algorithms, and spectral analysis for cycle detection — methods adapted from engineering and signal processing rather than traditional technical analysis. [14]
- **Intellectual lineage:** Acknowledges building on J.M. Hurst (1970), John Ehlers (2013), and B.J. Millard (1999). [12]
- **Source code:** 3rd edition opened source code repositories for NinjaTrader, MetaTrader, C++, Excel, and cloud-based API integrations. [15]
- **Multi-market validation:** S&P 500, Dow Jones, Gold, Silver, Forex (EUR/USD, GBP/USD), VIX sentiment data, Financial Stress Index, Bitcoin. [14]

### 2.3 Part 2: Metonic Cycles — Core Concepts

- **External energy cycles:** Proposes correlations between financial markets and external energy cycles including gravity, geomagnetism, and solar/lunar cycles. [16]
- **Gann's master cycles reverse-engineered:** Uses DSP to decode W.D. Gann's hidden master cycles. [16]
- **Mechanical trading system:** Presents a 100% mechanical, cycle-based system claiming 20% CAGR over 30 years on the Dow. [16]
- **Sentiment predictor:** A cyclic sentiment predictor for the DJIA using daily data from 1935–2013; ancient cycles used to forecast daily sentiment years ahead. [16]
- **TradeStation/EasyLanguage code:** Full rebuildable indicators and trading systems included. [16]

### 2.4 Critical Reception

| Source | Rating | Key Points | URL |
|--------|--------|------------|-----|
| Goodreads (Part 1) | 2 ratings (1× 4-star, 1× 3-star) | Too few for aggregate display | [17] |
| Goodreads (Part 2) | 4.00 / 5.00 (4 ratings) | Positive but limited sample | [18] |
| Amazon (Part 1) | Not accessible (bot-blocked) | Listed as Top 100 Bestseller in Financial Engineering | [15] |
| Amazon (Part 2) | 5-star (Steve Puetz) | "Significant contribution to cycle analysis" | [19] |
| Kirkus Indie Review (Part 2) | Mixed/cautious | "Intriguing strategy... fundamental assumptions require careful scrutiny"; notes astrological framing | [20] |
| Trade Loss Tracker | Descriptive only | No rating; notes limited text extraction in PDF | [21] |

The **Kirkus review** of Part 2 is the most notable critical assessment:
- Praised: "The book outlines an intriguing strategy" and "17 out of 22 trades were winners in a 2008 analysis"
- Criticized: The approach is "steered by astrology"; questions whether a model based on "mood of investors" can compete with "[sophisticated] algorithmic trading" [20]

Steve Puetz (author of *The Unified Cycle Theory*) gave a public 5-star Amazon review, calling it "a significant contribution to cycle analysis." [19]

---

## 3. Trader's World Magazine Publications

Von Thienen has published **8 confirmed articles** in Trader's World Magazine (2014–2021), significantly more than the 5 initially identified:

| # | Issue | Date | Title |
|---|-------|------|-------|
| 1 | 56 | Jan/Feb/Mar 2014 | Detection of Dynamic, Dominant Cycles in Financial Data with a Genetic Algorithm [22] |
| 2 | 61 | 2016 | Gann's Proof & Cause of Market Movements [23] |
| 3 | 72 | Feb/Mar/Apr 2019 | Risk and Fall of a Crypto Star: How Cycles Predicted the Crash of Nvidia [24] |
| 4 | 76 | Mar/Apr/May 2020 | Turning Points [25] |
| 5 | 78 | Mar 2020 | How to select the appropriate cycles for forecasting [26] |
| 6 | 79 | Jan/Feb/Mar 2021 | turning points in 2020 with pre-pandemic data [27] |
| 7 | 80 | Apr/May/Jun 2021 | Dominant Cycles in Investment Managers' Exposure to U.S. Equity Markets Indicate Impending Turnaround [28] |
| 8 | 81 | Jul/Aug/Sep 2021 | extremes [29] |

**No TASC (Technical Analysis of Stocks & Commodities) articles found** under any spelling variant. [30]

---

## 4. Foundation for the Study of Cycles (FSC) Role

- **Board Member** since January 2020 [6]
- **Weekly live host** of the "Market Cycles Report" on Cycles TV (Mondays at noon ET) — a free YouTube livestream [31]
- **Developer** of the cloud-based Cycle Analysis Toolbox (the "Cycles App") used by FSC members [32]
- **Conference organizer/speaker** at FSC events including "Cycles in the City" (NYC, May 2026) featuring John Bollinger and Tom McClellan [33]
- **Technology provider:** WhenToTrade (WTT) is being **merged into the FSC**, with new licenses offered via the non-profit [34]
- The FSC Cycles App was **nominated as a finalist** for The Technical Analyst Awards 2022 (Best Specialist Product/Research & Most Innovative New Product) [10]

Notable FSC collaborations: John Bollinger discussion on cycles and volatility (June 2026), Tom McClellan on sunspot cycles, Dr. Richard Smith (FSC Chairman), Michael Howell (Crossborder Capital), Peter Eliades. [35]

---

## 5. Online Presence and Media

### 5.1 Substack — "Stock Market Cycles"

| Metric | Value |
|--------|-------|
| URL | https://lars.cycles.org/ |
| Subscribers | 3,000+ (100+ paid) |
| Pricing | $29.90/month or $299/year |
| Frequency | Daily (Mon–Fri), plus weekly Cycles TV |
| Started | July 2021 (archived posts from Oct 2022) |
| Tagline | "Understand market rhythm, anticipate reversals, and act with confidence" |

Content includes daily "Global Dominant Cycle Watch" posts covering ~45 international core assets, a proprietary CycleConsensus model scoring from -100 to +100, weekly "Tides Report" for paid subscribers, and access to cycle analysis courses. [36]

### 5.2 YouTube

- **FSC Cycles TV / Market Cycles Report** — Weekly live show hosted on the FSC YouTube channel: https://www.youtube.com/playlist?list=PLQFZhqmSOlq8-da2EybawwXaA-vRNxjkR
- Notable episodes: Market Forecast 2025/2026 (Bitcoin cycles), "US Stock Markets \| Market Cycles Report June 8, 2026" (4.0K views, 252 likes), Gold at Long-Term Cycle Peak (Feb 2025) [37]

### 5.3 Podcasts & Interviews

| Podcast | Date | Language | URL |
|---------|------|----------|-----|
| Torero Trader Insights #169 — "Zyklen bestimmen unser Leben" | Dec 2025 | German | [38] |
| Paul Barron Podcast — "URGENT: Market Expert Says Bitcoin Cycle Is BROKEN" | Nov 2025 | English | [39] |
| Markus Koch Wall Street — "Ein Gespräch mit Lars von Thienen" | Aug 2025 | German | [40] |
| Handelsblatt Wall Street Podcast — "Der verborgene Rhythmus der Märkte" | Jun 2026 | German | [41] |
| Substack Audio Podcasts | Ongoing | English | [42] |

### 5.4 TradingView

- **Username:** StockMarketCycles (joined Sep 2017) [43]
- **Followers:** 6.3K
- **Scripts:** 20 published Pine Scripts, including Cycle Swing Momentum, Cyclic Smoothed RSI (cRSI), MTF cRSI, and the "Tactical Cycle Execution Engine" (May 2026)
- **Ideas:** 20 published market analysis ideas

### 5.5 WhenToTrade.com

WhenToTrade (WTT) is von Thienen's commercial cycle analysis platform:
- **URL:** https://whentotrade.com/
- **Services:** Browser-based cycle detection, dominant market cycles dashboard, cycle scanner, email alerts, developer API at https://api.cycle.tools/specs
- **Status:** Being merged into the FSC non-profit [34]
- **Registered address:** Bredbeekskoppel 6, 21266 Jesteburg, Germany

### 5.6 GitHub

- **Profile:** https://github.com/whentotrade (9 public repos, 19 followers)
- **Key repo:** `cycle-analysis-tradingview` — Framework for TradingView cycle analysis integration (4 stars)
- No significant third-party re-implementations of his indicators found on GitHub

### 5.7 Other Platforms

| Platform | Handle / URL | Followers | Notes |
|----------|-------------|-----------|-------|
| LinkedIn | https://de.linkedin.com/in/larsvonthienen | 1,071 | 500+ connections |
| X/Twitter | @TheDigitalLars (personal? — unconfirmed) | — | Posts primarily through FSC account @studyofcycles |
| Medium | https://medium.com/@LarsVonThienen | 54 | Writes on whentotrade, digineering |
| Udemy | https://www.udemy.com/user/lars-von-thienen | 140 learners | Course on dominant cycle detection (free to Substack paid) |
| Amazon | https://www.amazon.com/stores/author/B00K3THGX2 | — | Author page |
| Facebook | FSC page only | — | Personal account not confirmed |

---

## 6. Trading Community & Reputation

### 6.1 Community Adoption

- **MotiveWave Forum:** Active community thread porting von Thienen's cRSI and CSI indicators; one user called cRSI their "go-to indicator"; versions created for NinjaTrader, TradingView, and Thinkorswim [44]
- **MQL5:** One third-party implementation — "Cyclic Smoothed cRSI" for MT5 (June 2026) — explicitly based on his book [45]
- **TradingView:** 20 original scripts, significant follower base (6.3K)
- **Modulus Marketplace:** WhenToTrade Pro listed at https://www.modulusfe.com/marketplace/when-to-trade/ [46]

### 6.2 Professional Endorsements

| Endorser | Title | Quote |
|----------|-------|-------|
| Earik Beann | CEO, Wave59 | "sitting on top of the pile... fantastic cycle algorithm that is REALLY good at sniffing out useful market cycles" [47] |
| Dimitri Villard | Managing Partner, Facet Capital Partners | "ground-breaking work in cycle analysis" [47] |
| Richard Gardner | President, Modulus Financial Engineering | "one of the best genetic algorithm apps out there" [47] |
| Larry Jacobs | CEO, TradersWorld Magazine | "one of the leading developers of market cycle research in the world" [47] |

### 6.3 Criticism & Controversy

**No criticism, scam allegations, or controversy found** across any searched source (web, forums, social media, review sites). Possible explanations:
- Von Thienen operates in a **niche domain** (cycle analysis) with a small, specialized audience
- **Institutional credibility** from FSC (est. 1941) and his honorary commercial judge appointment
- **Positive reputation** backed by industry endorsements
- No history of **non-delivery or false promises** complaints

### 6.4 Comparison to Other Cycle Analysts

His "dynamic cycle" approach is explicitly positioned as a departure from traditional "static" cycle models of:
- **J.M. Hurst** — "The Profit Magic of Stock Transaction Timing" (1970)
- **John Ehlers** — "Cycle Analytics for Traders" (2013)
- **B.J. Millard** — "Channels and Cycles" (1999)

The FSC whitepaper compares his Goertzel algorithm approach favorably to Ehlers' MESA method, citing a 2003 study by Dennis Meyers showing Goertzel outperforms MESA on noisy data. [48]

---

## 7. Open Questions

1. **Personal X/Twitter account:** @TheDigitalLars exists but is inactive or unconfirmed; it is unclear whether Lars maintains a personal X/Twitter presence or posts exclusively through the FSC account.
2. **Part 3 status:** The Genetic Algorithm volume was repeatedly foretold but never published. Was it fully absorbed into the WTT software, or are plans still active?
3. **3rd edition of Part 2:** No 3rd edition of Part 2 was ever published (only Part 1 was revised). Why was Part 2 left unrevised? Is a revision planned?
4. **User base size:** No independent data on WTT platform users, Substack paid subscriber count, or TradingView script usage statistics.
5. **FSC merger details:** WhenToTrade's merger into FSC is announced but not yet complete. The timeline and terms are unclear.

---

## 8. Sources

1. https://www.amazon.com/stores/author/B00K3THGX2/about — Amazon Author Page
2. https://www.udemy.com/user/lars-von-thienen — Udemy Instructor Profile
3. https://www.xing.com/profile/Lars_vonThienen — XING Profile
4. https://www.linkedin.com/in/larsvonthienen — LinkedIn Profile
5. https://de.linkedin.com/in/larsvonthienen — LinkedIn Profile (DE)
6. https://cycles.org/lars-von-thienen/ — FSC Board Member Profile
7. https://www.tradingvision.net/meet-the-team/ — TradingVision Team Page
8. https://lars.cycles.org/about — Substack About Page
9. https://insightssuccess.com/lars-von-thienen-integrating-technology-software-and-business-skills/ — Insights Success 2021 Award
10. https://cycles.org/news/ta-awards-finalist/ — FSC Technical Analyst Awards Finalist
11. https://www.amazon.de/dp/3834929107 — Lean IT-Management on Amazon DE
12. https://whentotrade.com/book-series/ — WhenToTrade Book Series Page
13. https://whentotrade.com/wordpress/wp-content/uploads/2014/04/DTHMR_Part1_TableOfContent.pdf — Part 1 TOC PDF
14. https://www.amazon.com/Decoding-Hidden-Market-Rhythm-WhenToTrade-ebook/dp/B074YDP92C — Part 1 on Amazon
15. https://whentotrade.com/book-part1/ — Part 1 Official Page
16. https://www.amazon.com/Decoding-Hidden-Market-Rhythm-WhenToTrade/dp/1499562594 — Part 2 on Amazon
17. https://www.goodreads.com/book/show/36117660-decoding-the-hidden-market-rhythm---part-1 — Part 1 Goodreads
18. https://www.goodreads.com/author/list/6117278.Lars_Von_Thienen — Goodreads Author Page
19. https://whentotrade.com/review-by-steve-p/ — Steve Puetz Review
20. https://www.kirkusreviews.com/book-reviews/lars-von-thienen/decoding-hidden-market-rhythm/ — Kirkus Indie Review
21. https://tradelosstracker.com/library/book/628-decoding-the-hidden-market-rhythm-part-1-thienen — Trade Loss Tracker
22. https://www.scribd.com/document/365503625/Traders-World-56 — Trader's World #56
23. https://tradersworld.com/issue61.pdf — Trader's World #61
24. https://www.magzter.com/US/Hallikers-Inc./TradersWorld/Business/331075 — Trader's World #72
25. https://tradersworld.com/issue76.pdf — Trader's World #76
26. https://tradersworld.com/issue-78/ — Trader's World #78
27. https://tradersworld.com/issue79.pdf — Trader's World #79
28. https://tradersworld.com/traders-world-issue-80/ — Trader's World #80
29. https://tradersworld.com/issue81.pdf — Trader's World #81
30. https://www.traders.com/ — TASC archive (searched: no results)
31. https://cycles.org/marketcyclesreport/ — FSC Market Cycles Report
32. https://app.cycles.org/oauthredirect — FSC Cycles App
33. https://cycles.org/cycles-in-the-city/ — Cycles in the City 2026 Conference
34. https://cycles.org/news/fsc-wtt/ — FSC-WTT Merger Announcement
35. https://x.com/studyofcycles — FSC on X/Twitter
36. https://lars.cycles.org/ — Stock Market Cycles Substack
37. https://www.youtube.com/playlist?list=PLQFZhqmSOlq8-da2EybawwXaA-vRNxjkR — Market Cycles Report Playlist
38. https://torero-trader-insights.com/episode/tti-169-zyklen-bestimmen-unser-leben-lars-von-thienen — TTI #169
39. https://www.youtube.com/watch?v=NuN43Qy7cZ0 — Paul Barron Podcast
40. https://markteinblicke.de/124328/2025/08/ein-gespraech-mit-lars-von-thienen/ — Markus Koch Interview
41. https://www.handelsblatt.com/audio/wall-street/wall-street-der-verborgene-rhythmus-der-maerkte-ein-gespraech-ueber-zyklen/100234954.html — Handelsblatt Podcast
42. https://lars.cycles.org/podcast — Substack Podcast
43. https://www.tradingview.com/u/StockMarketCycles/ — TradingView Profile
44. https://forum.motivewave.com/threads/lars-von-thienen-crsi-and-csi-studies-for-motivewave.2269/ — MotiveWave Forum Thread
45. https://www.mql5.com/en/market/product/179908 — cRSI on MQL5
46. https://www.modulusfe.com/marketplace/when-to-trade/ — Modulus Marketplace
47. https://whentotrade.com/ — WhenToTrade Homepage (testimonials)
48. https://cycles.org/wp-content/uploads/2020/03/CycleScanner_Whitepaper_FSC.pdf — FSC Cycle Scanner Whitepaper

**Additional general sources consulted:**
- https://cycles.org/about_us/board_and_staff/ — FSC Board & Staff
- https://whentotrade.com/cycles-technology-nominated-technical-analyst-award-2022/ — WTT Awards Nomination
- https://medium.com/@LarsVonThienen — Medium Profile
- https://github.com/whentotrade — GitHub Organization
- https://time-price-research-astrofin.blogspot.com/ — Time-Price-Research Blog (cites von Thienen)
- https://www.vtad.de/rgt/17566/ — VTAD German Presentation 2022
- https://docs.marketcycles.blog/ — Stock Market Cycles Documentation
- https://whentotrade.com/social-media-sentiment-cycles/ — Social Media Sentiment Cycles Research
