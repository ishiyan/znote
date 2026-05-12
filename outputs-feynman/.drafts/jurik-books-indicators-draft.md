# Mark Jurik's Books: Relationship to His Trading Indicators

## Executive Summary

Mark Jurik produced three publications sold through Jurik Research: two books and one audio seminar. **None of these publications are primarily about his proprietary trading indicators** (JMA, VEL, CFB, RSX, DMX, WAV, DDR). Instead, they cover broader topics — general computerized trading methodology, neural network forecasting, and mathematical approaches to financial data analysis. However, the books are deeply related to the *intellectual foundations* and *design philosophy* behind those indicators, even though they don't document the proprietary algorithms themselves.

The key distinction: the books teach the **principles** (signal processing, noise reduction, lag minimization, data preprocessing, phase analysis) that Jurik later commercialized as proprietary indicator products. They are "how to think about indicators" books, not "how to use JMA/RSX/etc." manuals.

## The Three Publications

### 1. *Computerized Trading: Maximizing Day Trading and Overnight Profits* (1999)

- **Publisher:** New York Institute of Finance (Prentice Hall)
- **ISBN:** 9780735200777
- **Pages:** 415
- **Role:** Mark Jurik is the **editor**, not sole author
- **Format:** Hardcover (now out of print / sold out)
- **Status on jurikres.com:** "100% SOLD OUT — Currently not available"

This is a **multi-author edited volume** with contributions from approximately 20 experts. Jurik organized the book and contributed appendix chapters on data quality and resources, but the main chapters are written by other practitioners (DiNapoli, Melancon, Vomund, Widner, Ang, Luisi, Kiev, Hayes, Kase, Antonacci, Strasser, May, Klimasauskas, Drake, Katz, and others).

**Contents organized in four sections:**
1. **Basic Trading Skills and Methods** — market entry/exit, popular indicators, trend analysis, money management
2. **Testing and Evaluation** — backtesting, evaluating trading performance
3. **Assessing the Market and Yourself** — trading psychology, market potential quantification, bar length selection
4. **Advanced Indicators and Forecasting** — intermarket analysis, nonlinear pricing, data preprocessing, statistical data mining, building advanced trading systems

**Relationship to Jurik indicators:** Indirect. The book discusses general indicator design principles and trading system development. Chapter topics like "Popular Trading Indicators" (by Melancon), "Complex Indicators" (by May), and "Data Preprocessing" (by Klimasauskas) cover the conceptual territory that Jurik's proprietary tools address — but they do not describe JMA, RSX, CFB, or any other Jurik-branded product. Jurik's own contributions are limited to appendix material on data sources and resources.

### 2. *Neural Networks & Financial Forecasting* (collection, ~1997)

- **Publisher:** Jurik Research (self-published, not available in bookstores)
- **Role:** Mark Jurik is the **author** of most reports in this collection
- **Format:** Bound collection of published and unpublished technical reports
- **Status on jurikres.com:** "100% SOLD OUT — Currently not available"

This is a **collection of Jurik's own research papers and technical reports**, covering neural networks, fuzzy logic, data preprocessing, and financial forecasting methodology.

**Contents include 16+ reports:**
- "Wall Street Forecast with a Neural Network" — introduction to neural net financial applications
- "Consumer Guide to Software for Smart Forecasting" — reviews of modeling software
- "Indicator Development Issues in the Space Domain" — advanced techniques for financial data analysis (also published in *AI in Finance* and the book *Virtual Trading*)
- Methodology Reports #1-3 on train/test performance, data partitioning, and scoring trading systems
- Application Notes #1-2 on optimal phase in crossover moving averages and adaptive moving averages (explicitly compares results "with Jurik's moving average" — an early reference to JMA)
- "Estimating Optimal Forecast Distance using Chaos Analysis"
- Reports on neural network algorithms, backpropagation critique, and the "Backpercolation" algorithm (Jurik's own invention)

**Relationship to Jurik indicators:** This is the most directly relevant publication. Several reports address the exact problems that Jurik's commercial indicators solve:
- The **adaptive moving average** application note directly discusses low-lag smoothing — the core problem JMA addresses.
- The **indicator development** report covers data preprocessing techniques related to WAV and DDR.
- The **chaos analysis** report touches on optimal forecast horizons — related to CFB's fractal analysis approach.
- However, the reports describe *methodological principles*, not the proprietary algorithms themselves. The commercial products (JMA, RSX, etc.) are implementations of ideas discussed in these research papers, but the papers predate and do not document the final commercial implementations.

### 3. *Space, Time, Cycles & Phase* (audio seminar, 1995)

- **Publisher:** Jurik Research
- **Format:** MP3 audio file on CD, with printed lecture notes/visuals
- **Origin:** Recording of a lecture at the 1995 Futures International Conference in California
- **Status on jurikres.com:** Available from Jurik Research only

This is a **recorded seminar**, not a book in the traditional sense, though jurikres.com catalogs it alongside the books. It presents four mathematical frameworks for analyzing financial time-series data.

**Topics covered:**
- **Space:** geometric perspective, data decorrelation
- **Time:** optimal sampling, temporal compression
- **Cycles:** filtering, frequency spectrum, low-lag data smoothing
- **Phase:** phase-shifting the MACD, phase diagram applications

Also covers: limitations of regression, neural networks, flexibility vs. reliability, and a "master flow chart for model building."

**Relationship to Jurik indicators:** Strongly foundational. The lecture explicitly covers **low-lag data smoothing** (the core JMA concept), **filtering and the frequency spectrum** (related to RSX and VEL), and **data decorrelation** (related to DDR). The seminar is based on Jurik's published article "Developing Indicators for Financial Trading," which is essentially the theoretical manifesto for his indicator product line. This is perhaps the closest any Jurik publication comes to explaining *why* his indicators work the way they do.

## Open Library's "Third Work"

Open Library lists three works by Mark Jurik, but two of them appear to be catalog entries for the same book under slightly different titles:
1. *Computerized Trading: Maximizing Day Trading and Overnight Profits (New York Institute of Finance)* — listed as "First published in 1998"
2. *Computerized trading: maximizing day trading and overnight profits* — listed as "First published in 1999"
3. *Advanced Computerized Trading Techniques: Using the Power of Technology to Manage Market Uncertainty and Maximize Profits* — listed as "First published in 1997"

The first two are clearly the same book (different edition records). The third title, "Advanced Computerized Trading Techniques," does not appear on jurikres.com's catalog at all and may be an earlier edition, a working title, or a cataloging artifact. No ISBN or publisher details are available for it on Open Library. **Inference:** This is likely an earlier or alternate edition of the same "Computerized Trading" book, not a separate work. The 1997 date would align with pre-publication or a preliminary edition.

## Additional Publications (Not Books)

Beyond the three cataloged publications, Jurik also produced:
- **Free technical reports** (PDFs) on jurikres.com, including "The BIG Picture," "Why Use JMA?", "Evolution of Moving Averages," "Optimal Forecast Horizon," and others
- **Articles** in *Futures* magazine and *Neurovest* journal
- **A chapter** in the book *Virtual Trading* (the "Indicator Development Issues in the Space Domain" report)
- **Tutorial strategies** — 13 demonstration trading strategies with TradeStation/MultiCharts code showing how to use Jurik Tools

The free technical reports are the publications most directly about his proprietary indicators. "Why Use JMA?" and "Evolution of Moving Averages" explicitly benchmark JMA against competitors. These are marketing/educational documents rather than books, but they are the closest thing to indicator-specific publications Jurik produced.

## Summary Assessment

| Publication | Type | Jurik's Role | About Jurik Indicators? | Relationship |
|---|---|---|---|---|
| *Computerized Trading* (1999) | Edited book | Editor | No — general trading topics | Covers the broader domain; does not discuss Jurik products |
| *Neural Networks & Financial Forecasting* (~1997) | Report collection | Author | Partially — discusses underlying methods | Closest to indicators; covers adaptive MA, data preprocessing principles |
| *Space, Time, Cycles & Phase* (1995) | Audio seminar | Speaker | Indirectly — teaches foundational theory | Covers low-lag smoothing, filtering, decorrelation — the theoretical basis for JMA, VEL, DDR |
| Free PDF tech reports | White papers | Author | **Yes** — directly about JMA, RSX | Marketing/educational documents; benchmark indicators explicitly |

**Bottom line:** Jurik's books are about the *science of indicator design and trading system development*, not about his specific commercial products. They teach the mathematical and conceptual foundations that his indicators are built on. The only publications that directly discuss JMA, RSX, and the other branded tools are the free PDF technical reports available on jurikres.com — which we covered in our previous session's research.

## Open Questions

1. **Is "Advanced Computerized Trading Techniques" (1997) truly a separate book?** Open Library has minimal metadata. It could be an early edition of "Computerized Trading" or a distinct publication. No corroborating source found beyond the Open Library entry.
2. **Did Jurik's Futures magazine articles discuss his proprietary indicators by name?** The jurikres.com bio mentions "many articles in Futures magazine" but doesn't list them. These might contain more direct indicator content than the books.
3. **Were the "Neural Networks & Financial Forecasting" reports ever updated after the commercial indicators launched?** The collection appears to be from the mid-1990s, before several indicators (RSX, DMX) were released.
