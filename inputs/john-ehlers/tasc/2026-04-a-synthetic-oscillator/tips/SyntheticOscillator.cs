using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;

namespace WealthScript42
{
    public class SynthOscSample : UserStrategyBase
    {
        Parameter _Ubnd;
        Parameter _Lbnd;
        Parameter _Length;

        public SynthOscSample()
        {
            _Lbnd = AddParameter("Lowerbound", ParameterType.Int32, 12, 5, 15);
            _Ubnd = AddParameter("Upperbound", ParameterType.Int32, 25, 15, 30);
            _Length = AddParameter("Length", ParameterType.Int32, 12, 5, 15);
        }

        SyntheticOscillator _synth;
        TimeSeries _roc2;

        public override void Initialize(BarHistory bars)
        {
            _synth = new SyntheticOscillator(bars.Close, _Lbnd.AsInt, _Ubnd.AsInt);
            PlotIndicator(_synth);

            _roc2 = Momentum.Series(Hann.Series(_synth, _Length.AsInt), 1);
            StartIndex = _Ubnd.AsInt;
        }

        public override void Execute(BarHistory bars, int idx)
        {
            if (!HasOpenPosition(bars, PositionType.Long))
            {
                if (_roc2.CrossesOver(0, idx))
                    PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
            }
            else
            {
                if (_roc2.CrossesUnder(0, idx))
                    ClosePosition(LastPosition, OrderType.Market);
            }
        }
    }
}