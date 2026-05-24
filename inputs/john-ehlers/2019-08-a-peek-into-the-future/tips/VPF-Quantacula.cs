using QuantaculaBacktest;
using QuantaculaCore;
using QuantaculaIndicators;
using System.Drawing;
using TASCIndicators;

namespace Quantacula
{
    public class MyModel : UserModelBase
    {
        //create indicators and other objects here
        public override void Initialize(BarHistory bars)
        {
            voss = new VossPredictor(bars.Close, 20, 3);
            PlotIndicator(voss, Color.Red);
            lowestVoss200 = new Lowest(voss, 200);
            PlotTimeSeries(lowestVoss200, "LowestVoss(200)", voss.PaneTag, Color.Black);
        }

        //execute the strategy rules here
        public override void Execute(BarHistory bars, int idx)
        {
            if (!HasOpenPosition(bars, PositionType.Long))
            {
                if (voss[idx] == lowestVoss200[idx])
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Limit, bars.Close[idx]);
            }
            else
            {
                if (voss[idx] > 0)
                    PlaceTrade(bars, TransactionType.Sell, OrderType.Market);
            }
        }

        //declare private variables below
        VossPredictor voss;
        TimeSeries lowestVoss200;
    }
}