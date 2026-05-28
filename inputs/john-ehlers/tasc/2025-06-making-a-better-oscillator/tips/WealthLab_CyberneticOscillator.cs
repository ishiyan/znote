using System;
using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;

namespace WealthScript8
{
    public class CyberneticSystem : UserStrategyBase
    {
        Parameter _LPLength, _HPFast, _HPSlow;
        Momentum _mo1, _mo2;

        public CyberneticSystem()
        {
            _LPLength = AddParameter("LP Length", ParameterType.Int32, 20, 15, 30, 5);
            _HPFast = AddParameter("HP Fast", ParameterType.Int32, 55, 30, 75, 5);
            _HPSlow = AddParameter("HP Slow", ParameterType.Int32, 155, 100, 200, 5);
            StartIndex = _HPSlow.AsInt;
        }

        public override void Initialize(BarHistory bars)
        {
            //create and plot indicators
            SuperSmoother LP = new(bars.Close, _LPLength.AsInt);
            HighPass BP1 = new(LP, _HPFast.AsInt);
            HighPass BP2 = new(LP, _HPSlow.AsInt);

            _mo1 = new Momentum(BP1, 2);
            _mo2 = new Momentum(BP2, 2);
            PlotIndicatorLine(_mo1, WLColor.Green);
            PlotIndicatorLine(_mo2, WLColor.Red);
            DrawHorzLine(0, WLColor.White, 1, LineStyle.Dashed, _mo1.PaneTag);
        }

        public override void Execute(BarHistory bars, int idx)
        {
            //trading rules
            if (!HasOpenPosition(bars, PositionType.Long))
            {
                if (_mo1[idx] > 0 && _mo2[idx] > 0)
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
            }
            else
            {
                Position p = LastPosition;
                if (_mo1[idx] < 0 || _mo2[idx] < 0)
                    ClosePosition(p, OrderType.Market);
            }
        }
    }
}
