# Walter Bressert's Cycle Methodology — Mechanics & Lineage

> Compiled 2026-06-03. Primary source is Bressert's own words in the March 1998
> *Technical Analysis of Stocks & Commodities* interview "Trading and Control"
> (interviewer Thom/Tom Hartle, conducted by telephone 22 Dec 1997), mirrored in
> full at the archived walterbressert.com:
> <https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html>.
> Quotations below are verbatim from that page unless otherwise noted. Where the
> exact arithmetic is **not** stated in a located source, this is flagged
> explicitly — no formulas are invented.

Bressert's system is a *two-engine* method: a **timing engine** (cycles, made
visible by detrending and made tradable by "timing bands") and a **trigger
engine** (oscillators that turn at cycle tops/bottoms without "wiggle"), bolted
to a **controlled-risk, multi-contract money-management** frame. The unifying
thesis — the title of his 1991 book — is that cycles tell you *when* to expect a
turn and oscillators *confirm* that the turn has happened, so each covers the
other's weakness. The sections below take each mechanism in turn.

---

## Methodology

### 1. Centered detrend (the timing engine's foundation)

**Source:** TASC 1998 interview, Fig. 3 caption and the "And the steps to
detrend the data?" exchange —
<https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html>

Construction, in Bressert's own steps:

1. Identify the suspected dominant cycle length by hand. "My method was to find
   the lowest low on the chart, and then start looking for the significant dips.
   I marked those. Then I counted the bars between those." Most markets show a
   dominant daily cycle of **14 to 25 bars**, "and a 20-day MA is a good cycle
   length to start with" (Fig. 3 caption).
2. Compute a moving average **equal in length to the cycle**, calculated up to
   the most recent close: "You take a centered moving average, which is the same
   length as the cycle, calculate it up to the last day…"
3. **Displace (plot) that MA backward by half the cycle length** to center it:
   "…and then plot it back half of the length of the cycle. Which means I would
   take a 20-period moving average and plot it back on day 10. Ideally, it should
   be between day 10 and day 11. I plot it back on the 10th day."
4. **Detrend by subtraction:** "I detrend it by subtracting the moving average
   from prices. Subtracting that difference between the moving average and the
   prices shows the cycle tops and bottoms much more clearly."

The exact arithmetic here *is* documented and unambiguous for the centered
version: detrend value = price − (N-period MA displaced back N/2 bars), with
N≈20 as the default daily starting point. The result is a wave oscillating
around zero whose troughs/peaks mark cyclic lows/highs.

**Why it lags:** because the MA is shifted back N/2 bars, the most recent
plottable detrend value sits half a cycle in the past. Bressert: "the centered
detrend lags back half of the length of the cycle… the data is back 10 bars from
current time." He warns that a first-timer "will think that this is great, and
that they've found the Holy Grail" — but it cannot be read at the live right edge
of the chart.

### 2. Real-time detrend (the right-edge version)

**Source:** same interview, "What next?" exchange.

To get a usable signal at the hard right edge, Bressert dropped the back-shift:
"Next, I tried a real-time detrend. I found that if I took a 10- or 20-day
real-time detrend, the real-time detrend was not as accurate as a centered
detrend."

So the real-time detrend is the same price-minus-MA construction **without the
N/2 displacement** — no lag, but degraded accuracy. Crucially, Bressert treats
the real-time detrend as *insufficient on its own*: "That realization led to
oscillators. That's when I started using a detrend and the 3-10 oscillator over
the detrends." The detrend localizes *where* in the cycle you are; the
oscillator overlaid on it provides the actual real-time turn signal.

> **Confidence flag:** The interview does not give the precise smoothing/normalization
> of the real-time detrend beyond "10- or 20-day." Whether his software version
> normalized amplitude or applied additional smoothing is **not documented** in the
> primary source.

### 3. The 3-10 oscillator overlay

**Source:** same interview, "What next?" / "Anything else you've found?" exchanges.

Bressert overlaid a **3-vs-10 momentum oscillator** on the detrend: "I saw that
the 3-10 often turned right at those cycle tops and bottoms." This is the classic
short-minus-long momentum construction (a 3-period vs 10-period difference). It,
the stochastic, and the RSI3M3 are the "three oscillators" he settled on; he
notes each "was constructed very differently," which is deliberate — independent
constructions reduce correlated false signals.

> **Confidence flag:** The interview names the "3-10 oscillator" but does not
> spell out whether the 3 and 10 are simple MAs of price, of the detrend, or a
> MACD-style difference. The exact formula is **not stated** in the primary source.

### 4. RSI3M3 (the signature trigger oscillator)

**Source:** TASC 1998 interview, Fig. 2 caption and the "To smooth the
volatility…" / "You use the three-period smoothed three-bar RSI?" exchanges.

Discovery and construction, in his words:

- He pushed the RSI lookback to an extreme short: "I tried a lookback period of
  three, but it is so short-term that it looks like static."
- The 3-period RSI still tracked cycle turns: "even though the RSI was volatile,
  it was still coming pretty close to where the cycle bottoms and tops were."
- He smoothed it with a 3-bar average: "To smooth the volatility, I applied a
  **three-bar average of the three-period RSI**. That smoothed the indicator's
  fluctuations. Suddenly, I had a very tradable oscillator that was better than
  the stochastic."

So **RSI3M3 = a 3-period RSI, then smoothed by a 3-bar moving average.** That
two-step definition is explicit. The Fig. 2 caption confirms the label and use:
"Overlaid on the centered detrend is the RSI-3M3, a 3 RSI smoothed with a 3 MA.
Note how the oscillator flows with the detrend and makes a dip as the cycle
bottoms, dropping below the buy line at **30** for the significant bottoms."

**Buy/sell line levels:** The **buy line is at 30** (stated explicitly twice —
Fig. 2 caption and "drop down below a buy line, such as the 30 on the RSI"). The
sell signal is described only as "the mirror image of the buy signal."

> **Confidence flag:** The numeric **sell line is not stated**. By symmetry it is
> presumably ~70, but the interview never prints that number, so it is inferred,
> not documented. Also, the RSI variant (Wilder smoothing vs simple) for the
> 3-period RSI base is not specified in the primary source.

**Pairing with the detrend:** RSI3M3 is plotted *on* the centered detrend so the
two move together; the detrend says you are in a cyclic low zone, the RSI3M3 dip
below 30 plus an upturn confirms momentum has changed. Bressert: "the
three-period smoothed three-bar RSI does that very well too" (turns at cycle
tops/bottoms).

### 5. Setup-bar / entry-stop mechanics

**Source:** same interview, Fig. 2 caption and "So to mechanize the decision…" /
"So if it turns up…" exchanges.

The mechanical, judgment-free entry (a "setup entry"):

1. Wait for the oscillator (e.g., RSI3M3) to **drop below the buy line (30)**.
2. Wait for it to **turn up**. The price bar of that upturn becomes the
   **setup bar** (colored blue in his software): "when the oscillator turned up,
   that bar would be my setup bar and that would tell me that the market had a
   change in momentum."
3. **Entry trigger:** place a **buy-stop one tick above the high of the setup
   bar** (signaled by a red dot). "I put my buy-stop one tick above that high to
   enter into the long position. By using one tick above that high, I would
   increase my odds for buying the cycle bottom by 10% to 25%, depending on the
   market and the time frame."
4. **Protective stop:** "If I've got a cycle bottom in, say a 20-day cycle, I
   could put my sell-stop loss in one tick below the low."

Why a stop above the high rather than buying the close: "if I bought a market on
close of an upturn, the market could slam down the next day… So to improve that
setup entry pattern, you wait for the next day's trading, put a buy-stop in above
the high of the day, and if the market moves higher, you're in." Sells are the
exact mirror image. This deliberately enters *after* the bottom — "there's only
one bottom" and chasing the exact tick is what produced his losses.

### 6. Timing bands (the "middle 70%" forecast windows)

**Source:** TASC 1998 interview, the "So what did you do?" exchange and Fig. 5.

How they were built, by hand:

- "I counted all the measurements from low to low, low to high and high to low. I
  came up with these very long periods in which cycles had topped and bottomed…
  the time periods were much too wide for trading."
- The 70% rule: "I believed that if I could just be right in my timing 70% of the
  time, I could make money. So I took the **middle 70% of the time periods** and
  low and behold, I had a relatively short period. I called that a **timing
  band**."

**What they predict:** Given a confirmed cycle low, a timing band forecasts the
window in which (a) the next cycle **top** is due and (b) the next cycle **low**
is due: "With that timing band, I could forecast from the time that a bottom
occurred when the next cycle top would occur. I could also forecast from that
same bottom when the next bottom was going to occur."

**Trading use as an exit gate:** "I get a 70% timing band, so I am not going to
even consider getting out until I'm into that 70% timing band. Because only 15%
of the tops have occurred before that." (The middle-70% band leaves 15% of
historical turns in each tail — early and late — which is the source of the "only
15% have occurred before" figure.)

> **Confidence flag (mechanics well-documented; exact statistic method not):**
> The *concept* — keep the central 70% of the historical interval distribution —
> is explicit. The exact statistical construction (percentile clipping vs
> mean ± something) is **not formally specified**; "middle 70%" reads as a 15th-to-
> 85th percentile band but the interview does not state the estimator.

### 7. The oscillator/cycle combination thesis

**Source:** title and content of *The Power of Oscillator/Cycle Combinations*
(1991, Walter Bressert and Associates); developed throughout the 1998 interview.

The central idea of his 1991 book is that **cycle timing and oscillator
confirmation cover each other's blind spots.** Cycles alone give an *element of
time* but no confirmation that a specific bar is the turn — "something that would
say this was a cycle bottom or a cycle top." Oscillators alone wiggle and produce
false turns, and in trends they pin at overbought/oversold ("in a strong bull
market, it will stay at very high overbought levels"). Combined:

- The cycle/timing band restricts *when* you will even look for a signal (so an
  oscillator turn outside the band is ignored — killing many false signals).
- The oscillator, overlaid on the detrend, confirms that the turn has *actually
  happened* and provides the mechanical setup-bar/entry-stop trigger.

Bressert frames the whole exercise as eliminating judgment: "I've got to quantify
my methods because I want to eliminate the judgment. Using judgment is what causes
losses." The combination is what makes the cycle *mechanical and tradable* rather
than merely descriptive — the gap he says Hurst's theory left open (see Lineage).

### 8. Controlled-risk, multi-contract money management

**Source:** TASC 1998 interview, Fig. 1 caption and the multi-contract exchanges.

The structure scales out of 2–3 contracts at progressively longer-cycle targets:

- **Why multiples of two/three:** small dollar risk per contract (achieved by
  entering close to the cycle bottom) is what *permits* multiple contracts. "the
  smaller my dollar risk, the more contracts I could put on and the more I could
  take off of my number 1 contract at my first target."
- **Contract #1 — fast scalp of the bounce.** Taken off quickly at a first target
  (the forecastable minimum bounce): "I take my number 1 off… I've got to get
  that off within four days, five at the most, or the odds are very good that
  it's going to drop." Purpose is to cut both dollar *and emotional* risk: "as
  soon as I took the number 1 contract off, it was like there was a bright
  light… I was no longer under pressure."
- **Contract #2 — the trading-cycle top.** "The second contract is designed to
  look for the top of the trading cycle" (exited inside the timing band on an
  oscillator sell signal or trailing stop).
- **Contract #3 — the longer cycle.** "The third contract is there for the
  longer-term move," held for the dominant cycle in the next-longer time frame.

**The risk arithmetic he gives (Fig. 1 context):** "say you've got 10% of your
money at risk with a three-contract position. Therefore, you've got 3 1/3% in
each position. If I take that first contract off, that lops off 3 1/3% of my
risk. That 3 1/3% in my hand also offsets the second 3 1/3%. So my exposure for
that trade then drops from 10% to 3 1/3% by taking that one-third profit." Exits
on #2/#3 use a toolkit, not one rule: "Parabolic stops can be used. Swing highs
and lows can be used. Weekly highs and lows can be used… an oscillator sell
signal… sell-stop below that setup bar."

### 9. Left / right translation (trend bias)

**Source:** TASC 1998 interview, Fig. 4 caption and the translation exchanges.

Definition: translation is the *skew* of a cycle's high within the cycle.

- **Right translation** = cycle high leans to the **right** (late in the cycle) =
  market in a **bull** move / up-trend.
- **Left translation** = cycle high leans to the **left** (early in the cycle) =
  market in a **declining** / down-trend.

Bressert: "A right translation occurs when a market is in a bull move. That's
when the cycle highs lean to the right. A left translation is when the market is
in a declining move. The cycle top leans to the left." His worked example: in an
ideal 20-day cycle the shape is "10 days up, 10 days down," but a bull market
might run "15 days up and five days down" (right translation); after a top it
flips to "five days up and 15 days down" (left translation).

**Trend-bias use:** translation sets directional expectation and tells you when to
*believe your oscillator*: "Trend is up, right translation. Trend is down, left
translation… It tells you what to expect when the trend reverses." This dovetails
with his hierarchical trend rule — "the trend to the time frame you are trading is
the dominant cycle in the next longer time frame" (a daily chart's trend is set by
the weekly cycle).

---

## Lineage

Bressert is explicit that his work is *applied, quantified* descendant of two
prior bodies of cycle research. He did not originate the underlying ideas; he
adapted them to make futures trading mechanical.

### J. M. Hurst — *The Profit Magic of Stock Transaction Timing* (1970) & workshops

**Source:** TASC 1998 interview ("Before I started the newsletter…") and the
archived bio overview —
<https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWBTitle.html>

Direct connection: Bressert attended Hurst's workshops. "during that time, the
classic *The Profit Magic of Stock Transaction Timing* was published. After the
book was published, the book's author, J.M. Hurst, started holding workshops…
we all went to his workshops." The bio page confirms he "studied… Jim Hurst's
classic book on cycles… [and] also attended several of Jim's workshops."

What Hurst contributed (the framework Bressert built on):

- **The cyclic principle and the principle of commonality / summation** — prices
  are the sum of several roughly harmonic cyclic components plus trend.
- **The nominal model** — a hierarchy of cycles of nominal (typical) lengths,
  each roughly twice/half its neighbours. This is the conceptual parent of
  Bressert's "dominant cycle in the next longer time frame sets the trend."
- **Displaced moving averages** — Hurst's signature tool: an MA centered by
  plotting it back half its span to track a cyclic component. **This is the
  direct ancestor of Bressert's centered detrend** (same back-displacement of
  N/2). Bressert's added step is subtraction (price − displaced MA) to isolate
  the wave, then overlaying oscillators on it.
- **Hurst's FLD (Future Line of Demarcation)** and envelope/channel work around
  the displaced MA.

**Crucial distinction Bressert himself draws:** Hurst gave *theory without
tradable structure*. The bio overview states he "realized that something was
missing. There was plenty of theory on how to use cycles, but no quantification,
or structure, that would allow him to trade the markets cyclically with
confidence." Bressert's timing bands, RSI3M3 trigger, and money-management frame
are precisely the quantification he felt Hurst's work lacked.

> **Confidence flag:** The *specific* attribution of "displaced MA → centered
> detrend" is an analytic inference from matching mechanics (both displace an MA
> back N/2). Bressert, in the interview, actually credits the **centered detrend
> technique to the Foundation for the Study of Cycles, not to Hurst** (see below).
> Hurst and the Foundation both used centered/displaced MAs, so the detrend has a
> *dual* heritage; the interview's own attribution points to the Foundation.
> Likewise, FLD and the nominal model are documented Hurst contributions from the
> TA literature, but the **interview does not name FLD or "nominal model"** — those
> are Hurst's known contributions generally, not items Bressert cites by name.

### Edward R. Dewey & the Foundation for the Study of Cycles (founded 1941)

**Source:** TASC 1998 interview ("I found a couple of books published by Ned
Dewey…" and "centered detrending… was the process initially used by the
Foundation for the Study of Cycles, and they still use it today").

- Bressert read Dewey's books and the Foundation's magazine, and studied ***The
  Catalogue of Cycles*** ("which lists about 20,000 different cycles"). This gave
  him the conviction that cycles are pervasive and that short-term market cycles
  should exist if long-term ones do: "if the long-term cycles existed, then
  short-term cycles should work, too."
- **The centered detrend technique is borrowed directly from the Foundation,** by
  Bressert's own statement: "I used a process called centered detrending… which
  was the process initially used by the Foundation for the Study of Cycles, and
  they still use it today" and "I borrowed this technique from the Foundation."
- **He was a USER, not a founder.** The Foundation was founded in 1941 by
  economist Edward R. ("Ned") Dewey — who, per Bressert, "had been hired by the US
  government back in the 1930s to determine what had caused the Great
  Depression," concluded the cause was "cyclical in nature," then "left the
  government and started the Foundation for the Study of Cycles." Any claim that
  Bressert *co-founded* the Foundation is false; he studied its published
  research decades after its founding.

### Boundary note — Blau double-smoothing (out of scope here)

Bressert's name is also attached to the **Double Smoothed Stochastic (DSS /
"DSS Bressert")**, which shares double-smoothing lineage with **William Blau**'s
1990s TASC work. That indicator and the Blau-vs-Bressert formulation question are
covered by a separate agent and are deliberately **not** analyzed in this brief.
Flagging only the boundary: the DSS double-smoothing is a *distinct* thread from
the centered-detrend / RSI3M3 / timing-band methodology documented above.

---

## Confidence notes

**Well-documented mechanics (explicit numbers/steps in the primary source):**

- **Centered detrend** — full construction: N-period MA (N≈20 default for daily,
  range 14–25), displaced back N/2 bars, subtracted from price. Lag = N/2.
  *Exact and unambiguous.*
- **RSI3M3** — 3-period RSI smoothed by a 3-bar MA; **buy line = 30**. Definition
  explicit.
- **Setup-bar / entry-stop** — oscillator below buy line → upturn = setup bar →
  buy-stop one tick above its high; protective stop one tick below the low.
  Fully specified, sells are the mirror image.
- **Timing bands** — "middle 70%" of the historical low-to-low / low-to-high /
  high-to-low interval distribution; used as forecast windows and as an exit gate
  ("only 15% of tops occur before" the band). Concept explicit.
- **Money management** — 2–3 contracts, #1 scalp (off within 4–5 days), #2 trading-
  cycle top, #3 longer cycle; the 10% → 3⅓% risk-reduction arithmetic is given.
- **Left/right translation** — definitions and the 20-day worked example are
  explicit; trend rule (longer time frame's cycle = current trend) is explicit.

**Vaguely described / inferred (flagged, not invented):**

- **RSI3M3 sell line** — never printed; ~70 is inferred by symmetry only.
- **RSI base** — whether the 3-period RSI uses Wilder vs simple smoothing is not
  stated.
- **Real-time detrend** — only "10- or 20-day" given; no normalization/smoothing
  detail.
- **3-10 oscillator** — named but its exact formula (MA difference? of price or
  detrend?) is not specified in the primary source.
- **Timing-band statistics** — "middle 70%" implies a 15th–85th-percentile band
  but the estimator is not formally stated.
- **Detrend → displaced-MA lineage to Hurst** — analytic inference from matching
  mechanics; Bressert's *own* attribution of the centered detrend is to the
  Foundation for the Study of Cycles. FLD and the "nominal model" are documented
  Hurst contributions from TA literature, **not** named by Bressert in the
  interview.

---

## Sources (inline above; consolidated)

- Walter Bressert, interviewed by Thom Hartle, **"Trading and Control,"**
  *Technical Analysis of Stocks & Commodities*, Mar 1998 (Vol. 16, No. 3). Full
  text:
  <https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html>
  (Figures 1–5 captions are the source of the money-management, RSI3M3,
  centered-detrend, translation, and weekly/daily trend examples.)
- **"About Walter Bressert / Professional Career: An Overview,"** archived bio:
  <https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWBTitle.html>
  (Hurst workshops, Foundation study, "something was missing — no quantification.")
- **"From the Desk of Walter Bressert,"** archived:
  <https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB1.html>
  (cycles-as-timing philosophy; "cycles within cycles" for trend.)
- *The Power of Oscillator/Cycle Combinations* (Walter Bressert and Associates,
  1991) — the named source of the oscillator/cycle combination thesis (catalogued
  in `trading-research/walter-bressert.md`).
- J. M. Hurst, *The Profit Magic of Stock Transaction Timing* (Prentice-Hall,
  1970) — cyclic principle, nominal model, displaced MAs, FLD (named in the
  interview/bio; specific tools per standard TA literature).
- Edward R. Dewey / Foundation for the Study of Cycles (founded 1941); *The
  Catalogue of Cycles* — centered-detrend technique and ~20,000-cycle catalogue
  (per Bressert's interview).
