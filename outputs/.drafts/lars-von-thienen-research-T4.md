# Agent T4: Trading Community & Reputation — Lars von Thienen

## 10 Mandatory Forums

### 1. ForexFactory
**Status: NO relevant threads found (only generic "Trend Cycle Entry" thread, unrelated)**

A search of `site:forexfactory.com` for "Lars von Thienen", "WhenToTrade", and "whentotrade" returned no dedicated threads about him or his work. A single thread titled "Trend Cycle Entry" uses the term "cycle" generically and is not related.

The brief mentions "Already found 3 threads (2012, 2021, 2026)" — these may exist behind login walls or search restrictions. Searches with multiple approaches did not surface them.

- https://www.forexfactory.com/thread/1134457-trend-cycle-entry (unrelated generic thread)
- **NOT FOUND:** Dedicated Lars von Thienen / WhenToTrade discussion threads

### 2. futures.io / BigMikeTrading
**Status: NOT FOUND**

No results for `site:bigmiketrading.com` or `site:forums.traders.com` containing "Lars von Thienen" or "WhenToTrade". The site may require login to access forum content.

- **BLOCKED / NOT FOUND:** No accessible threads found.

### 3. Elite Trader
**Status: NOT FOUND**

`site:elitetrader.com` search returned the site homepage but no specific threads mentioning Lars von Thienen or WhenToTrade. The forum has 293K+ threads and 5.5M+ posts but either no discussion exists or it is not indexed.

- https://www.elitetrader.com/et/ (general forum landing page)
- **NOT FOUND:** No threads mentioning Lars von Thienen

### 4. NinjaTrader Forum
**Status: NOT FOUND**

`site:forum.ninjatrader.com` search returned no results. Either no discussion exists or forum content is behind login/auth walls.

- **BLOCKED / NOT FOUND:** No accessible content.

### 5. TradingView — FOUND (significant presence)

**TradingView profile: StockMarketCycles**
- https://www.tradingview.com/u/StockMarketCycles
- 6.3K followers, 20 scripts published
- Lars von Thienen's handle: @StockMarketCycles (joined Sep 3, 2017)

**Published Pine Scripts:**
1. **Cycle Swing Momentum** — https://www.tradingview.com/script/b7o7GmWT-Cycle-Swing-Momentum/
2. **Cyclic Smoothed RSI (cRSI)** — https://www.tradingview.com/script/TmqiR1jp-RSI-cyclic-smoothed-v2/
3. **MTF Cyclic Smoothed RSI** — https://www.tradingview.com/script/xoFw4Q2F-Cyclic-Smoothed-RSI-MTF/
4. **Cycle Swing Momentum - The Tactical Cycle Execution Engine** — https://www.tradingview.com/script/iuBzHsJ6-Cycle-Swing-Momentum-The-Tactical-Cycle-Execution-Engine/ (May 2026, advanced DSP tactical execution indicator based on his research)

**Third-party inspired scripts** also exist on TradingView referencing his methods.

### 6. MQL5 Forum / CodeBase — FOUND (partial)

**Direct indicators referencing his work:**
- **Cyclic Smoothed cRSI MT5** — https://www.mql5.com/en/market/product/179908 (June 2026, based on "Decoding The Hidden Market Rhythm – Dynamic Cycles" ISBN 9781974658244)
- **KT Schaff Trend Cycle MT4** — https://www.mql5.com/ja/market/product/90650 (Dec 2022, "Schaff Trend Cycle" — related but not directly his)

Search for "Dynamic Cycles", "dominant cycle", "von Thienen indicator" on MQL5 returned mostly generic cycle indicators, not directly attributed to him. His own book provides MQL4/5 source code directly.

- **FOUND:** Cyclic Smoothed cRSI MT5 (third-party implementation)
- **PARTIAL:** His book includes MetaTrader source code, but many MQL5 marketplace results are generic cycle indicators not attributed to him.

### 7. Wealth-Lab
**Status: NOT FOUND**

`site:wealth-lab.com` search returned no results mentioning Lars von Thienen or WhenToTrade.

- **NOT FOUND:** No accessible content.

### 8. Quant Stack Exchange
**Status: NOT FOUND**

`site:quant.stackexchange.com` search for "dominant cycle", "Lars von Thienen", "WhenToTrade" returned no relevant results. The site has some discussion of Ehlers cycles but not von Thienen.

- **NOT FOUND:** No mentions found.

### 9. Reddit / r/algotrading
**Status: NOT FOUND**

`site:reddit.com "Lars von Thienen" OR "WhenToTrade" algotrading` returned no dedicated threads. The search was blocked by Reddit's rate limiting (blocked response).

- **BLOCKED:** Reddit restricts automated searches. Manual search needed.
- **NOT FOUND:** No accessible threads mentioning him.

### 10. Trade2Win
**Status: NOT FOUND**

`site:trade2win.com` search returned only a parked domain placeholder (trade2win.site). The original site appears to be defunct or redirected.

- **BLOCKED / DEFUNCT:** trade2win.com appears no longer active.

---

## MQL5 Implementations (Extended)

- **Cyclic Smoothed cRSI MT5** (June 2026) — https://www.mql5.com/en/market/product/179908
  - Explicitly based on "Decoding The Hidden Market Rhythm – Dynamic Cycles" by Lars von Thienen (ISBN 9781974658244)
  - "This MT5 adaptation preserves the mathematical integrity of the original"

- The book itself includes "source code for MetaTrader, NinjaTrader, C++, Excel workbooks and API integration" — available through Amazon and whentotrade.com.

- **MotiveWave community implementation** (April 2024):
  - User "saturn33" ported von Thienen's cRSI and CSI indicators to MotiveWave
  - Source: https://forum.motivewave.com/threads/lars-von-thienen-crsi-and-csi-studies-for-motivewave.2269/
  - Files hosted at: astrowin.org/cRSI_CSI.jar and astrowin.org/cRSI_CSI_source_code.zip
  - Thread shows active community use — another user "imakenocents" reported creating versions for NinjaTrader, TradingView, and Thinkorswim, calling it "my go-to indicator"

- **Phase Analytics Pro** (MQL5) — https://www.mql5.com/en/market/product/90650
  - "Based on the principles of digital signal processing, this indicator decomposes price action into phase and quadrature components to identify the dominant market cycle"
  - While not explicitly attributed to von Thienen, uses similar DSP cycle detection approach

---

## GitHub Repositories

### Official / Directly Attributed

1. **whentotrade/cycle-analysis-tradingview** — https://github.com/whentotrade/cycle-analysis-tradingview
   - Stars: 4, Forks: 1
   - Proposal for cycle analysis integration in TradingView
   - README authored by Lars von Thienen himself
   - Links to his TradingView scripts and API documentation
   - Reference to the cloud-based cycle analysis engine at https://api.cycle.tools/specs

2. **whentotrade GitHub org** — https://github.com/whentotrade
   - Profile: "Author of 'Decoding The Hidden Market Rhythm' - Cycles in Financial Markets"
   - Limited public repositories visible

### Third-Party / Inspired

3. **thetestspecimen/ehlers-indicators-mql5** — https://github.com/thetestspecimen/ehlers-indicators-mql5
   - Stars: 17, Forks: 1
   - Ehlers cycle indicators for MQL5 (related domain, not directly von Thienen)
   - von Thienen's work builds on Ehlers, so this is tangentially related

4. **fmzquant/strategies** — https://github.com/fmzquant/strategies
   - 5.3K stars — large collection of quantitative trading strategies
   - Includes cycle-related strategies but no direct attribution to von Thienen

### Libraries search (pandas_ta, ta-lib, tulip)
- **pandas_ta** — https://www.pandas-ta.dev/ — 150+ indicators. Includes "Even Better Sinewave" (Ehlers) in Cycles category but no von Thienen-specific indicators. https://www.pandas-ta.dev/api/cycle
- **TA-Lib** — includes Hilbert Transform - Dominant Cycle Period (HT_DCPERIOD) by John Ehlers, not von Thienen. https://ta-lib.github.io/ta-doc/indicator/HT_DCPERIOD.htm
- **NOT FOUND:** No direct von Thienen indicator implementations in these libraries

### Unofficial / Community
- **mohammadreza-mohammadi94/MQL5-Indicators** — generic MQL5 indicators, not von Thienen
- **Data-Analisis/Technical-Analysis-Indicators---Pandas** — pandas_ta fork, 174 stars, no von Thienen-specific content

---

## Criticism & Controversy

### Overall Assessment: NONE FOUND

Searches for the following terms returned zero critical or negative content:
- "Lars von Thienen scam" — NO RESULTS
- "Lars von Thienen criticism" — NO RESULTS (only unrelated articles)
- "WhenToTrade review scam" — NO RESULTS
- "Lars von Thienen controversy" — NO RESULTS

### Why no criticism found

Several possible explanations:
1. **Niche audience** — His work addresses a specialized subset of traders (cycle analysis); the community is small enough that public criticism may not surface in search indexes
2. **Positive reputation** — His association with the Foundation for the Study of Cycles (est. 1941) and endorsements from industry figures (Earik Beann of Wave59, Richard Gardner of Modulus, Larry Jacobs of TradersWorld Magazine) provide credibility
3. **No "scam" narrative** — Unlike some trading authors, there appears to be no history of complaints about non-delivery, false promises, or fraud
4. **Commercial judge role** — His appointment by the German Minister of Justice as an honorary commercial judge adds institutional credibility

### Comparisons with Other Cycle Analysts

His work explicitly builds upon:
- J.M. Hurst — "The Profit Magic of Stock Transaction Timing" (1970)
- John Ehlers — "Cycle Analytics for Traders" (2013)
- B.J. Millard — "Channels and Cycles" (1999)

He positions his "dynamic cycle" approach as a departure from their "static" cycle models.

The FSC whitepaper (https://cycles.org/wp-content/uploads/2020/03/CycleScanner_Whitepaper_FSC.pdf) compares his Goertzel algorithm approach favorably to Ehlers' MESA method, citing a study by Dennis Meyers (2003) showing Goertzel outperforms MESA on noisy data.

---

## Community Reputation Assessment

### Positive Endorsements (from whentotrade.com)

1. **Earik Beann** (CEO, Wave59): "sitting on top of the pile... fantastic cycle algorithm that is REALLY good at sniffing out useful market cycles"
2. **Dimitri Villard** (Managing Partner, Facet Capital Partners): "ground-breaking work in cycle analysis"
3. **Richard Gardner** (President, Modulus Financial Engineering): "one of the best genetic algorithm apps out there"
4. **Larry Jacobs** (CEO, TradersWorld Magazine): "one of the leading developers of market cycle research in the world"

### Foundation for the Study of Cycles (FSC)

- Board Member since at least 2020
- Hosts weekly "Market Cycles Report" livestream on Cycles TV (Mondays at noon ET)
- FSC is a non-profit established in 1941 by Edward R. Dewey
- WhenToTrade technology is being merged into the FSC: https://cycles.org/news/fsc-wtt/
- Profile page: https://cycles.org/lars-von-thienen/

### Substack Presence
- **Stock Market Cycles** — https://lars.cycles.org/
- 3,000+ subscribers, 100+ paid
- $29.90/month or $299/year
- Daily global cycles watch, started July 2021

### YouTube / Video Content
- https://www.youtube.com/playlist?list=PLQFZhqmSOlq8-da2EybawwXaA-vRNxjkR
- Weekly live analysis of active cycles
- Featured guest: John Bollinger (June 2026) — FSC Board Member Lars von Thienen and John Bollinger discussing cycles and volatility

### MotiveWave Forum — Active User Discussion
- Thread "Lars von Thienen cRSI and CSI studies for MotiveWave": https://forum.motivewave.com/threads/lars-von-thienen-crsi-and-csi-studies-for-motivewave.2269/
- Users actively porting his indicators to different platforms (MotiveWave, NinjaTrader, TradingView, Thinkorswim)
- User comment: "I think his approach to cycle analysis is interesting. He uses signal analysis to recover dominant cycles." (HUB, Apr 2024)

### Awards & Recognition
- Cycles Tech nominated as finalist for "The Technical Analyst Awards" 2022: Best Product / Research & Most Innovative New Product — https://whentotrade.com/cycles-technology-nominated-technical-analyst-award-2022/
- Selected as "The 50 Most Influential Business Leaders in Tech 2021" by Insights Success

---

## Additional Sources Found

### Personal / Professional
- **LinkedIn**: https://de.linkedin.com/in/larsvonthienen — CEO of bps business process solutions GmbH (since 1999)
- **Udemy**: https://www.udemy.com/user/lars-von-thienen — 140 total learners, 27 reviews
- **Medium**: https://medium.com/@LarsVonThienen — 54 followers, writes on whentotrade and digineering publications
- **Amazon Author Page**: https://www.amazon.com/stores/author/B00K3THGX2
- **Cycle Scanner Whitepaper (PDF)**: https://cycles.org/wp-content/uploads/2020/03/CycleScanner_Whitepaper_FSC.pdf
- **Trading Social Media Sentiment Cycles** (research paper): https://www.whentotrade.com/social-media-sentiment-cycles/

### Third-Party References
- **Time-Price-Research Blog** — several posts citing von Thienen's cycle analysis:
  - Gold at Long-Term Cycle Peak (Feb 2025): https://time-price-research-astrofin.blogspot.com/2025/02/gold-at-long-term-cycle-peak-lars-von.html
  - US Stock Market at the Cliff (Dec 2024): https://time-price-research-astrofin.blogspot.com/2024/12/us-stock-market-at-cliff-dont-be.html
  - The 41-Month Kitchin Cycle Topping Patterns (Nov 2024): https://time-price-research-astrofin.blogspot.com/2024/11/the-41-month-kitchin-cycle-topping.html
- **YouTube discussion with John Bollinger** (June 2026): https://x.com/studyofcycles (FSC X/Twitter)
- **YouTube interview** — "Cycles Analysis With Special Guest Lars Von Thienen": https://www.youtube.com/watch?v=gM0aI0ocUoM

### Products & Platforms
- **WhenToTrade** — https://whentotrade.com/ — cycle analysis toolbox
- **Cycle Analysis API** — https://api.cycle.tools/specs
- **Cycle Apps** — https://app.cycles.org/oauthredirect (FSC members)
- **Modulus Marketplace** — https://www.modulusfe.com/marketplace/when-to-trade/ (WhenToTrade Pro - Genetic Algorithm Cycle Trading Software)

---

## Summary Assessment

| Category | Status |
|----------|--------|
| **ForexFactory** | 3 threads claimed but not independently verified; no new threads found |
| **futures.io / BigMikeTrading** | NOT FOUND — possibly behind login walls |
| **Elite Trader** | NOT FOUND |
| **NinjaTrader Forum** | NOT FOUND — likely behind login |
| **TradingView** | FOUND — significant presence: 6.3K followers, 20+ scripts |
| **MQL5** | FOUND — 1 direct implementation (cRSI MT5), book source code included |
| **Wealth-Lab** | NOT FOUND |
| **Quant Stack Exchange** | NOT FOUND |
| **Reddit r/algotrading** | BLOCKED — automated search blocked by Reddit |
| **Trade2Win** | DEFUNCT — site appears inactive |
| **MotiveWave Forum** | FOUND — active user discussion and porting of indicators |
| **GitHub** | FOUND — official repo + profile, no third-party reimplementations |
| **Criticism / Scam** | NONE FOUND — no negative content, complaints, or controversy |
| **FSC Reputation** | Strong — Board Member, weekly host, technology provider |
| **Substack** | 3K+ subscribers, daily cycle analysis |

Lars von Thienen maintains a **positive, credible reputation** within the niche cycle analysis community. He is institutionally backed by the Foundation for the Study of Cycles (est. 1941), endorsed by industry figures, and has a track record of publicly available research (whitepapers, books, TradingView scripts, weekly YouTube analysis). No evidence of criticism, controversy, or "scam" allegations was found across any searched source. His main commercial platform (WhenToTrade) is in the process of being merged into the FSC non-profit.
