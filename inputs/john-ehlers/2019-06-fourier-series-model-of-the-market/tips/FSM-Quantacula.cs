using QuantaculaBacktest;
using QuantaculaCore;
using TASCExtensions;

namespace Quantacula
{
    public class MyModel : UserModelBase
    {
        //create indicators and other objects here, executed prior to main trading loop
        public override void Initialize(BarHistory bars)
        {
            fs = new FourierSeries(bars.Close, 20);
            PlotIndicator(fs);
            StartIndex = 201;
        }

        //execute strategy rules here, executed once for each bar in the backtest history
        public override void Execute(BarHistory bars, int idx)
        {
            if (LastPosition == null)
            {
                //is FS at its historical low, and turning up?
                double lowFS = fs.GetLowest(idx - 1, 200);
                if (fs[idx - 1] == lowFS)
                    if (fs.TurnsUp(idx))
                        PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
            }
            else
            {
                //sell at 2 bar high
                PlaceTrade(bars, TransactionType.Sell, OrderType.Limit, bars.High.GetHighest(idx, 2));
            }
        }

        //declare private variables below
        private FourierSeries fs;
    }
}