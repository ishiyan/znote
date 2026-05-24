Example Code:
using QuantaculaBacktest;
using System;
using QuantaculaCore;
using System.Drawing;
using TASCIndicators;

namespace Quantacula
{
    public class MyModel1 : UserModelBase
    {
        //this is executed prior to the main trading loop
        public override void Initialize(BarHistory bars)
        {
            StartIndex = 14;
            ca = new CorrelationAngle(bars.Close, 14);
            PlotIndicator(ca);
        }

        //this is executed once for each bar in the backtest history
        public override void Execute(BarHistory bars, int idx)
        {
            //determine market state
            int state = 0;
            double angle = ca[idx];
            double angle1 = ca[idx - 1];
            if (Math.Abs(angle - angle1) < 9 && angle < 0)
                state = -1;
            else if (Math.Abs(angle - angle1) < 9 && angle >= 0)
                state = 1;

            //color background based on state
            if (state == -1)
                SetBackgroundColor(idx, colorUp);
            else if (state == 1)
                SetBackgroundColor(idx, colorDown);
        }

        //declare private variables below
        private CorrelationAngle ca;
        private Color colorUp = Color.FromArgb(32, 255, 0, 0);
        private Color colorDown = Color.FromArgb(32, 0, 255, 0);
    }
}
