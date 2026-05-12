# J. Welles Wilder Jr. — Research Brief

**Research Agent:** T1  
**Date:** 2026-05-07  
**Status:** Complete

---

## 1. Biography

| Field | Detail |
|-------|--------|
| Full Name | John Welles Wilder Jr. |
| Born | June 11, 1935, Norris, Tennessee, USA |
| Died | April 18, 2021, Christchurch, New Zealand (aged 85) |
| Education | B.S. Mechanical Engineering, North Carolina State University (1962) |
| Military | U.S. Navy, Korean War |
| Career | Mechanical engineer → real estate developer → technical analyst |
| Family | Wife: Eleanor Dawn Barefoot (m. 1958); children: John III, Catharine, David |
| Brother | Albert "Bert" Wilder (NFL player, 1939–2012) |
| Company | Trend Research LTD, Greensboro, NC; Delta Society International |
| Relocation | Moved to Christchurch, New Zealand (October 1999) |
| Death | Vascular dementia/Alzheimer's; died April 18, 2021 |

### Accolades
- **Forbes** (Oct 1980): "the premier technical trader publishing his work today"
- **Barron's** (Jul 1984): credited with expanding mathematical analysis in 1978
- **Financial World** (Jul 1985): "developed more accurate commodity trading systems and concepts than any other expert"

### Famous Quotes
1. "Letting your emotions override your plan or system is the biggest cause of failure."
2. "Some traders are born with an innate discipline. Most have to learn it the hard way."
3. "If you can't deal with emotion, get out of trading."

---

## 2. TASC (Stocks & Commodities) Articles

### Articles BY Wilder
The TASC author archive does not list any articles authored directly by J. Welles Wilder Jr. (search returned no XML file). This is consistent with the fact that his book predates the magazine (1978 vs. 1982 launch).

### Articles ABOUT Wilder / Interviews

| Date | Title | Author | Type | URL |
|------|-------|--------|------|-----|
| March 2009 | "Surviving The Test Of Time: J. Welles Wilder" | Brian Twomey | Interview | http://traders.com/Documentation/FEEDbk_docs/2009/03/Interview.html |

**Interview summary (March 2009):** Twomey interviews Wilder about his background (born Norris TN, NC State engineering, real estate), Delta Phenomenon theory (perfect order in 5 time frames, 19-year longest), and his continued system development from New Zealand.

**TASC Article Count: 1 confirmed (interview about Wilder)**

---

## 3. Books — Full Citations

### Primary Works by Wilder

1. **New Concepts in Technical Trading Systems**  
   Wilder, J. Welles. (1978). *New Concepts in Technical Trading Systems*. Greensboro, NC: Trend Research.  
   ISBN: 978-0-89459-027-6  
   Google Books: https://books.google.com/books?id=WesJAQAAMAAJ  
   Internet Archive: https://archive.org/details/newconceptsintec00wild

2. **The Adam Theory of Markets or What Matters Is Profit**  
   Wilder, J. Welles. (1987). *The Adam Theory of Markets or What Matters Is Profit*. Greensboro, NC: Trend Research.  
   ISBN: 978-9997619730

3. **The Wisdom of the Ages in Acquiring Wealth**  
   Wilder, J. Welles. (1989). *The Wisdom of the Ages in Acquiring Wealth*. Cavida.  
   ISBN: 978-0974645803

4. **The Delta Phenomenon, Or, The Hidden Order in All Markets**  
   Wilder, J. Welles. (1991). *The Delta Phenomenon, Or, The Hidden Order in All Markets*. Delta Society International.  
   ISBN: 978-9992823262

### Key Reference Works Citing Wilder

5. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance. ISBN: 978-0735200661.

6. Achelis, S. B. (2001). *Technical Analysis from A to Z* (2nd ed.). McGraw-Hill. ISBN: 978-0071363488.

7. Kaufman, P. J. (2013). *Trading Systems and Methods* (5th ed.). Wiley. ISBN: 978-1118043561.

8. Appel, G. (2005). *Technical Analysis: Power Tools for Active Investors*. FT Press. ISBN: 978-0131479029.

**Book Count: 4 by Wilder + 4 reference works = 8 total**

---

## 4. Photos / Videos / Interviews

| Type | Description | URL | Status |
|------|-------------|-----|--------|
| Photo | Wikipedia/Wikimedia Commons portrait | https://upload.wikimedia.org/wikipedia/commons/e/ef/Welles_Wilder.jpg | ✓ Found |
| Interview | TASC March 2009 (text) | http://traders.com/Documentation/FEEDbk_docs/2009/03/Interview.html | ✓ Found |
| Obituary | Greensboro News & Record via Legacy.com | https://www.legacy.com/us/obituaries/greensboro/name/welles-wilder-obituary?id=53397461 | ✓ Found |
| Blog | "Welles Wilder - Father of RSI & SAR" | https://thebestbusinessintheworld.blogspot.com/2010/05/welles-wilder-father-of-rsi-sar.html | ✓ Found |
| YouTube | Search "J Welles Wilder interview" | [URL not found — no confirmed video interviews located] | ✗ |
| Conference | Appearance recordings | [URL not found] | ✗ |

**Photo/Video URL Count: 4 confirmed URLs**

---

## 5. Indicators from *New Concepts in Technical Trading Systems* (1978)

### 5.1 RSI (Relative Strength Index)
- **Category:** Oscillator
- **Default period:** 14
- **Formula:**
  - RS = Average Gain / Average Loss (Wilder-smoothed)
  - RSI = 100 − 100 / (1 + RS)
- **Wilder's smoothing:** New Avg = (Prev Avg × (N−1) + Current Value) / N

### 5.2 ATR (Average True Range)
- **Category:** Volatility filter
- **Default period:** 14
- **Formula:**
  - TR = max(H − L, |H − C₋₁|, |L − C₋₁|)
  - ATR = Wilder's smoothing of TR over N periods

### 5.3 ADX / DMI (Directional Movement Index)
- **Category:** Trend
- **Default period:** 14
- **Formula:**
  - +DM = H − H₋₁ (if > −DM and > 0, else 0)
  - −DM = L₋₁ − L (if > +DM and > 0, else 0)
  - +DI = Smoothed(+DM) / ATR × 100
  - −DI = Smoothed(−DM) / ATR × 100
  - DX = |+DI − −DI| / (+DI + −DI) × 100
  - ADX = Wilder's smoothing of DX over 14 periods

### 5.4 Parabolic SAR (Stop and Reverse)
- **Category:** Trend / Strategy
- **Formula:**
  - SAR(t+1) = SAR(t) + AF × (EP − SAR(t))
  - AF starts at 0.02, increments by 0.02, max 0.20
  - EP = extreme point of current trade

### 5.5 Swing Index / Accumulative Swing Index (ASI)
- **Category:** Oscillator
- **Formula:** Complex formula using O, H, L, C of current and previous bars
- **Use:** Confirms breakouts, measures commitment

### 5.6 Commodity Selection Index (CSI)
- **Category:** Filter
- **Formula:** CSI = ADXR × ATR × (margin/commission factor)
- **Use:** Ranks commodities by tradability (directional movement + volatility)

### 5.7 Wilder's Smoothing Method
- **Category:** Filter / Smoothing
- **Formula:** New = (Old × (N−1) + Value) / N
- **Equivalence:** EMA with period (2N − 1)
- **Note:** Used internally by RSI, ATR, ADX calculations

---

## 6. Summary Statistics

| Metric | Count |
|--------|-------|
| TASC articles (by/about Wilder) | 1 |
| Books by Wilder | 4 |
| Reference books citing Wilder | 4 |
| Photo/media URLs found | 4 |
| Indicators documented | 7 |

---

## Sources
- Wikipedia: https://en.wikipedia.org/wiki/J._Welles_Wilder_Jr.
- TASC Archive: http://technical.traders.com/archive/combo/display5.asp
- TASC Interview: http://traders.com/Documentation/FEEDbk_docs/2009/03/Interview.html
- Wikimedia Commons photo: https://upload.wikimedia.org/wikipedia/commons/e/ef/Welles_Wilder.jpg
