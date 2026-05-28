Code:
using QuantaculaBacktest;
using QuantaculaCore;
using QuantaculaIndicators;
using System.Drawing;
using TASCIndicators;

namespace Quantacula
{
    public class MyModel1 : UserModelBase
    {
        //create indicators here
        public override void Initialize(BarHistory bars)
        {
            StartIndex = 200;
            reflex = new Reflex(bars.Close, 20);
            PlotIndicator(reflex);
            reflexLL = new Lowest(reflex, 200);
            PlotIndicator(reflexLL, Color.Maroon);
            reflexHH = new Highest(reflex, 20);
            PlotIndicator(reflexHH, Color.DarkGreen);
        }

        //execute the strategy rules here
        public override void Execute(BarHistory bars, int idx)
        {
            if (!HasOpenPosition(bars, PositionType.Long))
            {
                //code your buy conditions here
                if (reflex[idx] == reflexLL[idx])
                {
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
                    exitFlag = false;
                }
            }
            else
            {
                //code your sell conditions here
                if (exitFlag)
                {
                    if (reflex[idx] < reflexHH[idx])
                        PlaceTrade(bars, TransactionType.Sell, OrderType.Market);
                }
                else if (reflex[idx] == reflexHH[idx])
                    exitFlag = true;
            }
        }

        //declare private variables below
        Reflex reflex;
        Lowest reflexLL;
        Highest reflexHH;
        bool exitFlag;
    }
}
