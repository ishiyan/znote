WealthScript Code (C#): 
using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;

namespace WealthLab.Strategies
{
   public class FractalDim : WealthScript
   {
      StrategyParameter _n;
      StrategyParameter _per;

      public FractalDim()
      {
         _n = CreateParameter("N", 30, 10, 60, 2);   // An even number
         _per = CreateParameter("Average Period", 20, 10, 55, 1);
      }

      protected override void Execute()
      {   
         HideVolume();
         int N = _n.ValueInt;
         int avPer = _per.ValueInt;
         DataSeries avg = AveragePrice.Series(Bars);
         DataSeries smooth = FIR.Series(avg, "1,2,2,1");
         DataSeries n3 = (Highest.Series(smooth, N) - Lowest.Series(smooth, N)) / N;
         
         int per = N / 2;         
         DataSeries n1 = (Highest.Series(smooth, per) - Lowest.Series(smooth, per)) / per;
         DataSeries smooth_ = smooth >> per;
         DataSeries n2 = (Highest.Series(smooth_, per) - Lowest.Series(smooth_, per))/ per;
         
         DataSeries ratio = new DataSeries(Bars, "Fractal Ratio");
         DataSeries dimen = new DataSeries(Bars, "Fractal Dimension");
         double log2 = Math.Log(2);
         for (int bar = N; bar < Bars.Count; bar++)
         {
            if (n1[bar] > 0 && n2[bar] > 0 && n3[bar] > 0)
               ratio[bar] = 0.5 * ((Math.Log(n1[bar] + n2[bar]) - Math.Log(n3[bar])) / log2 + dimen[bar-1]);
            else
               ratio[bar] = ratio[bar-1];
            
            if (bar < avPer)
               dimen[bar] = ratio[bar];
            else
               dimen[bar] = SMA.Value(bar, ratio, avPer);
         }
         
         ChartPane fdPane = CreatePane(40, false, true);
         DrawHorzLine(fdPane, 1.4, Color.Blue, LineStyle.Solid, 1);
         DrawHorzLine(fdPane, 1.6, Color.Blue, LineStyle.Solid, 1);
         PlotSeries(fdPane, dimen, Color.Red, LineStyle.Solid, 2);   
      }
   }
}
