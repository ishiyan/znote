# FAQs on DDR

Source: `http://jurikres.com/faq1/faq_ddr.htm`

## BibTeX

```bibtex
@online{jurikres_faq_ddr,
  author       = {{Jurik Research}},
  title        = {{FAQs} on {DDR}},
  year         = {2012},
  url          = {http://jurikres.com/faq1/faq_ddr.htm},
  note         = {Archived at Wayback Machine}
}
```

---

## Table of Contents

### FAQs on DDR

- [What is the Theory Behind DDR?](#what-is-the-theory-behind-ddr)
  - [Will DDR's new explanatory variables resemble my original variables?](#will-ddrs-new-explanatory-variables-resemble-my-original-variables)
    - [Does DDR reduce the number of explanatory variables better than other software products?](#does-ddr-reduce-the-number-of-explanatory-variables-better-than-other-software-products)
      - [Can the outputs of DDR be used as indicators in their own right?](#can-the-outputs-of-ddr-be-used-as-indicators-in-their-own-right)
        - [Can I export the DDR's output values to a text file?](#can-i-export-the-ddrs-output-values-to-a-text-file)

### General Topics on Jurik Tools

- [Can the tools plot many curves on each of many charts?](#can-the-tools-plot-many-curves-on-each-of-many-charts)
  - [Can the tools process any type of data?](#can-the-tools-process-any-type-of-data)
    - [Can the tools work in real-time?](#can-the-tools-work-in-real-time)
      - [Are the algorithms disclosed or black-boxed?](#are-the-algorithms-disclosed-or-black-boxed)
        - [Do Jurik tools need to look into the future of a time series?](#do-jurik-tools-need-to-look-into-the-future-of-a-time-series)
          - [Do the tools produce similar values across all platforms (TradeStation, Multicharts, ...)?](#do-the-tools-produce-similar-values-across-all-platforms)
            - [Do Jurik's tools come with a guarantee?](#do-juriks-tools-come-with-a-guarantee)
              - [How many installation passwords do I get?](#how-many-installation-passwords-do-i-get)

---

## FAQs on DDR

### What is the Theory Behind DDR?

When an analyst is not certain which financial indicators should be used in a new forecast model or trading system, he typically starts by considering all forms of data that might have some relation to the desired result. For example, when developing a model intended to forecast aluminum prices, one might start by collecting historical metal prices as well as indicators related to future supply and demand. Such indicators may include the consumer confidence index, projected car sales (autos require lots of aluminum), projected oil prices (which may affect car sales), and related indices. This collection of market data time series could be quite large, exceeding 50 or more entities.

Should 50 or more variables be fed to a forecast model? As unintuitive as this may appear, models with fewer input variables frequently *outperform* those utilizing more variables! Statisticians attribute this counter-intuitive behavior to two well understood phenomena:

- **OVER-FITTING** . . . too many variables permit the model/system to focus on the random as well as non-random aspects of market behavior. The developed model/system will then try forecasting random as well as non-random market movement. But, like forecasting the roll of dice, this will probably lead to disastrous results.

- **MULTI-COLINEARITY** . . . some input variables may yield essentially the same information, with only slight differences between them. Pairs of such indicators are said to be *correlated*. Models that are "trained" stochastically may depend on such correlations and catastrophic consequences occur when these correlations change even a little over time.

The model/system builder can address both phenomena by reducing the number of inputs to a bare minimum. But if you were to start with just 10 indicators, you would need to consider over 1,000 possible combinations of variables! If you were to start with 100 indicators, there would be about 2^100 combinations, and your computer would spend the next 13 eons considering them all! Civilization may not be around by then.

Some modeling tools try to get around this problem by performing correlation analysis between pairs of input variables and deleting one indicator from each highly correlated pair. This approach is faulty as it may delete one or more critical indicators, because for some problems, two correlated inputs are exactly what the model may need! For example, a model may require as input either the futures contract price or the spot price because the two are highly correlated and only one or the other is sufficient. On the other hand, some models require both inputs because they need to know the difference or *premium*.

> **Is there an efficient way to decorrelate input data and reduce the number of input variables simultaneously, without throwing away potentially useful information?**

Professional forecasters use software based on solid techniques that large companies can afford to buy. This puts individual traders at a disadvantage. Until now, that is. DDR, the Decorrelator and Dimension Reducer, gives you access to the same powerful technique used by professional data analysts.

To reduce the number of variables for your model (regression, neural net, etc.) DDR does not eliminate any of your input variables. Dimension reduction is attained in a completely different way.

Instead, DDR processes all N input fields (explanatory variables, such as price, MACD, interest rates, etc.) and converts them into N new explanatory variables (e.g. N new columns on a spreadsheet). These new indicators, in total, represent all the information found in your original columns; however, DDR concentrates most of the information into just a few of these new variables.

DDR also ranks all the new indicators it produces according to how much of the original information each new indicator represents. This way, you can eliminate most of the other new variables without losing much information, if any at all. As a result, you have the same information as before, but now it is represented by fewer variables. On a typical data set, DDR reduces the number of explanatory variables by at least 50% without losing more than 1% of the total information supplied by all the original indicators. That's dimension reduction!

As an added benefit, the new time series indicators produced by DDR are completely decorrelated, normalized and with zero-mean. Just right for input to a non-linear regression model, such as a neural network.

### Will DDR's new explanatory variables resemble my original variables?

The new explanatory variables (indicators) produced by DDR will typically have no resemblance to the original data you give it. This is because each of the new variables are a unique mathematical combination of all the original indicators. These combinations are specifically designed so that the new variables have the following desirable properties:

- All are 100% decorrelated from each other
- All are normalized with zero-mean
- Most of the available information is concentrated into the first few columns

Those of you experienced with building forecasting models know just how important these features are. You have probably realized by now that DDR is not a toy indicator. In fact, it uses one of the most powerful algorithms known to mathematicians.

### Does DDR reduce the number of explanatory variables better than other software products?

Yes. Some modeling tools reduce the dimensionality (number of explanatory variables) of a data set by performing correlation analysis between pairs of variables. They assume that if two variables are correlated, then you do not need both, and so one of them may be eliminated. This popular practice can easily lead to a dead end.

Here's a simple example to illustrate why. Suppose you have access to two indicators:

1. Daily value of technology securities sector
2. Daily value of energy securities sector

Assuming both sectors are somewhat correlated, you would still need to know both values if you want to estimate money flow from one sector to another. If one of the two series were removed by pairwise correlation elimination, there would not be enough information remaining to estimate money flow. Therefore, no information should be lost during the data pre-processing stage.

In contrast, DDR does not throw away any information. In fact, you can ALWAYS recreate all your original explanatory variables by using simple weighted combinations of DDR's output variables! Consequently, DDR's output still contains all the vital information that your forecast model might need.

### Can the outputs of DDR be used as indicators in their own right?

Yes. The output columns of DDR are indicators in their own right. Some users have built trading strategies using DDR output directly.

### Can I export the DDR's output values to a text file?

You can export any alphanumeric data on Excel's spreadsheets to text files.

---

## General Topics on Jurik Tools

### Can the tools plot many curves on each of many charts?

Yes. You can create and chart as many indicators as you like.

### Can the tools process any type of data?

Jurik Tools can be applied to any time-series data that WANDERS, like a random walk. For example, daily prices of IBM securities, monthly readings of a person's body weight are two examples of wandering values. Although RSX is not designed to process a purely random time series, it can be used to process the cumulative sum of the same series. This is because the cumulative sum would plot as a random walk.

Types of time frames include tick, volume or range bars; minute, hourly, end-of-day, weekly or monthly bars.

Jurik Tools run on any number of time series simultaneously, and on multiple charts.

### Can the tools work in real-time?

Yes. All Jurik tools are designed to operate as fast as possible in real-time.

### Are the algorithms disclosed or black-boxed?

Because Jurik Research has spent years perfecting these algorithms, disclosed versions of our formulas are available to U.S.A. firms only with special agreements, for a price of $5,000 per tool. The black-boxed version of our tools cost significantly less.

### Do Jurik tools need to look into the future of a time series?

One can create impressive looking indicators on historical data when it analyzes both past and future values surrounding each data point being processed. However, any formula that needs to see future values in a time series cannot be applied in real world trading. This is because when calculating today's value of an indicator, future values don't exist.

All Jurik indicators use only current and previous time-series data in its calculations. This allows all Jurik indicators to work in real time conditions, including live trading.

### Do the tools produce similar values across all platforms?

Yes. Although the tools are activated differently within each platform, the values produced by our core functions (JMA, VEL, RSX, CFB) are as similar as can be, within the constraints of each charting platform.

If you have already licensed one or more tools, you can get the same tool(s) for a different platform at a discount.

### Do Jurik's tools come with a guarantee?

**WHAT WE DO GUARANTEE** (Effective 9 FEB 98)

We guarantee that our software performs as advertised. Of course, proper application and common sense is required on your part. If you can demonstrate a "bug" in our software, we will make every effort to fix it in reasonable time. If not, we will refund your purchased user license for that specific tool.

**WHAT WE DO NOT GUARANTEE**

We cannot guarantee that our tools will improve the profitability of every trading system, as some systems are flat out losers and quick remedial efforts would be fruitless. Our tools are powerful functions, but even the best workshop tool cannot save a burning house.

We endeavor to offer you the best products and customer support. Our reputation depends on it.

### How many installation passwords do I get?

For licensed TradeStation users, one password is good for all copies of TradeStation having the same "TradeStation Customer Number" or TCN. A different TCN will require a different password.

For all other users (i.e. not TradeStation), a password permits you to install onto only one computer. If you want to install onto a second computer, you need a second password. We will provide you a second password for free, provided you meet certain requirements. Contact CUSTOMER SUPPORT for details.

Should you replace your computer with a new one, we will send you a replacement password, provided you meet certain requirements. Contact CUSTOMER SUPPORT for details.
