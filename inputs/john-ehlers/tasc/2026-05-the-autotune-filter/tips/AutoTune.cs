using WealthLab.TASC;
using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.Indicators;

namespace WealthScript2026
{
    public class AutoTuneProFormaLong : UserStrategyBase
    {
        public override void Initialize(BarHistory bars)
        {
            _autoTune = AutoTune.Series(bars.Close, 20, 0.2);
            _roc = Momentum.Series(_autoTune, 2) / bars.Close * 100;
            PlotTimeSeriesLine(_roc, "Mo %", "ROC", WLColor.SandyBrown);
            DrawHorzLine(-0.15, WLColor.White, 1, LineStyle.Dashed, "ROC");

            PlotIndicator(_autoTune, WLColor.FromArgb(255, 120, 120, 255), PlotStyle.Line);
            _minCorr = AutoTune.Series(bars.Close, 20, 0.2, true);

            PlotTimeSeriesLine(_minCorr, "MinCorr", "MinCorr", WLColor.White, 2);
            StartIndex = 20;
        }

        public override void Execute(BarHistory bars, int idx)
        {
            if (!HasOpenPosition(bars, PositionType.Long))
            {   // entry
                if (_roc[idx - 1] < -0.15 && _roc.TurnsUp(idx) && _minCorr[idx] < _thresh)
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
            }
            else
            {   // exit
                if (_roc.CrossesUnder(0, idx) && _minCorr[idx] < _thresh)
                    ClosePosition(LastPosition, OrderType.Market);
            }
        }

        IndicatorBase _autoTune;
        IndicatorBase _minCorr;
        TimeSeries _roc;
        double _thresh = 0.22;
    }
}