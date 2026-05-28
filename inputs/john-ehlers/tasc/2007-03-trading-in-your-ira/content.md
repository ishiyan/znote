# Trading In Your IRA

- **Author:** John F. Ehlers
- **Publication:** Technical Analysis of STOCKS & COMMODITIES, Volume 25, March 2007, pp. 22--24
- **Article URL:** [Article PDF](https://technical.traders.com/archive/article.asp?file=\V25\C03\047EHL.pdf)

---

*This concept lets you trade your IRA with performance that can beat the index dramatically.*

## Introduction

Trading in your individual retirement account (IRA) usually means selecting which mutual fund to buy. The performance of these mutual funds is gauged relative to the Standard & Poor's 500 or similar index. In this article I will describe some concepts that will allow you to trade your IRA with index-beating performance --- sometimes dramatically.

Most IRAs do not allow trading on the short side. Selling short is just the flipside of buying a long position. When you buy a long position, your strategy is to hold for a period and then sell back at a higher price for a profit. Similarly, you expect prices to decline if you sell short. In this case your strategy is to sell short now, hold for a period of time, and buy back at a lower price.

## Buying Options

Although you (usually) cannot sell short in your IRA, you *can* buy options to create synthetic positions. You want to use in-the-money options for these synthetic positions. You buy call options for synthetic long positions and you buy put options for synthetic short positions. Therefore, you are always buying something to establish your position in either direction. This is the fundamental concept of trading in your IRA. Simple and elegant, isn't it?

So let's look deeper into how this concept works. I don't want to get bogged down in all the complexities of options, so I will present only the salient points and use hypothetical numbers for clarity.

Suppose you have selected the S&P Deposit Receipts ETF (SPY) as the index to trade, and its current price is $140 per share. You can buy a call option whose strike price is $135 per share for $5 per share. The $5 share price consists of two parts, the intrinsic value and a time value. The time value will erode with time, valueless at expiration of the option. However, the intrinsic value of the options moves in lock-step with the price of the index. Option folks call this rate of change difference *delta*. Delta is theoretically equal to one for deep in-the-money options. As a practical matter, deltas for options in your trading range are more on the order of 0.8.

But suppose you expect the price of the index to decline. You can buy a SPY put option whose strike price is $145 per share for $5 per share. In this case the strike price is above the share price of the SPY index, and also consists of the intrinsic value and the time value. The in-the-money put option value varies inversely with the price of the index. In principle, if the price of the index drops a dollar, the value of the put option increases by a dollar (if delta = 1).

Thus, you can implement a strategy to buy an in-the-money call option when you expect the price of the index to increase and to buy an in-the-money put option when you expect the price of the index to decrease. You basically ignore the erosion of the time value because you will be reversing your position sufficiently frequently that time value erosion becomes another cost of trading, just like commissions.

But timing is crucial to the correct implementation of your strategy. All options have an expiration date. You need to sell back the option or exercise it before expiration. When using options as a trading strategy you need to select an expiration date in the relatively near future to avoid paying an exorbitant premium. Time value erodes with time, remember?

So if you expect to hold a position for a week or two, you can safely buy an option whose expiration is only a month or two into the future. A swing trading system fits the requirements for trading with sufficient frequency so that the position can be fully implemented within the expiration period of the option. There are many swing systems, but the one I use can be found at my website www.indicez.com.

There are several other factors you should be aware of when using the in-the-money option strategy. These are the leverage that options afford, and options act as virtual stop-loss orders.

## In-The-Money

Since the delta of the in-the-money option has an absolute value of nearly 1, the leverage you have is simply the ratio of the index price to the option price. In the example, the leverage is 140/5 = 28. This is more leverage than futures traders realize from their initial margin on futures contracts. Huge profits can be realized with leverage like this. Losses can also become substantial because of this leverage.

On the other hand, you can never lose more than you bet with options; the worst-case scenario is that the option you bought expires valueless. This is just like a stop-loss order --- with one added benefit. If the index price reverses, a previously valueless option can again have value. A stop-loss takes you out of the trade permanently and there can be no recovery.

## ProShares ETFs

Another way to trade your IRA is by using ProShares ETFs. The symbols for their "Ultra Long" ETFs are QLD, SSO, DDM, and MVV. These ETFs have a 2:1 leverage compared to the comparable standard index ETF. The symbols for "Ultra Short" ETFs are QID, SDS, DXD, and MZZ. The price of these Ultra Short ETFs varies inversely with the price of the comparable standard index ETF with a 2:1 leverage, so all you have to do to implement your trading strategy in your IRA is to switch between the Ultra Long and Ultra Short ETFs to establish long and short positions.

The downside of trading ProShares ETFs is that these have only recently been available; therefore, reliable and backtested trading systems don't exist.

## Conclusions

You no longer need to accept just buying mutual funds in your IRA. You can now establish synthetic long and short positions using proven and reliable timing tools.

---

*John Ehlers is a pioneer in the use of cycles and DSP techniques in technical analysis. He is the author of the MESA8 program, and www.indicez.com and www.eminiz.com websites for trading.*

## Suggested Reading

- Ehlers, John F. [2007]. "Fourier Transform For Traders," *Technical Analysis of* STOCKS & COMMODITIES, Volume 25: January.
- www.indicez.com
- www.optionsignals.com

---

```bibtex
@article{ehlers2007trading,
  author  = {Ehlers, John F.},
  title   = {Trading In Your {IRA}},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {25},
  number  = {3},
  pages   = {22--24},
  year    = {2007},
  month   = mar,
}
```
