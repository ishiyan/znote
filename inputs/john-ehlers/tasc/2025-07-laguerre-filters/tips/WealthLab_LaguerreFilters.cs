using WealthLab.TASC;
using System;
using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.Indicators;

namespace WealthScript
{
    public class LaguerreX : UserStrategyBase
    {
        public LaguerreX()
        {
            _period = AddParameter("Period", ParameterType.Int32, 60, 20, 80, 10);
            _gamma = AddParameter("Gamma", ParameterType.Double, 0.2, 0.1, 0.5, 0.1);
        }

        public override void Initialize(BarHistory bars)
        {
            PlotStopsAndLimits(3);
            _laguerre = new Laguerre(bars.Close, _period.AsInt, _gamma.AsDouble);
            _ultsmooth = new UltimateSmoother(bars.Close, _period.AsInt);
            _lagOsc = new LaguerreOsc(bars.Close, _period.AsInt, _gamma.AsDouble);

            PlotIndicatorLine(_laguerre, WLColor.Aqua);
            PlotIndicatorLine(_ultsmooth, WLColor.Red);
            PlotIndicatorLine(_lagOsc, WLColor.Gold);
            DrawHorzLine(-2, WLColor.White, 2, LineStyle.Dashed, _lagOsc.PaneTag);
            StartIndex = Math.Max(100, _period.AsInt);
        }

        public override void Execute(BarHistory bars, int idx)
        {
            if (!HasOpenPosition(bars, PositionType.Long))
            {
                if (_ultsmooth.CrossesOver(_laguerre, idx))
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market, 0, 1);
                if (_lagOsc.TurnsUp(idx) && _lagOsc[idx - 1] < -2 && _lagOsc[idx - 1] > -3)
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market, 0, 2);
            }
            else
            {
                Position p = LastPosition;
                ClosePosition(p, OrderType.Stop, p.EntryPrice * 0.97, "SL");
                if (_ultsmooth.CrossesUnder(_laguerre, idx))
                    ClosePosition(p, OrderType.Market, 0, "XU");
            }
        }

        Parameter _period;
        Parameter _gamma;
        IndicatorBase _laguerre;
        IndicatorBase _ultsmooth;
        IndicatorBase _lagOsc;
    }
}
