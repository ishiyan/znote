Wealth-Lab 6 Strategy Code (C#):

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;

namespace WealthLab.Strategies
{
   public class SwamiMarketMode : WealthScript
   {   
      StrategyParameter _plotWidth;
      StrategyParameter _delta;
      StrategyParameter _fraction;
      
      public SwamiMarketMode()
      {
         _plotWidth = CreateParameter("Plot Width", 6, 2, 10, 1);
         _delta = CreateParameter("Delta", 0.5, 0.05, 1, 0.05);
         _fraction = CreateParameter("Fraction", 0.1, 0.05, 1, 0.05);
      }
      
      public DataSeries BandPassSeries(DataSeries ds, int period, double delta)
      {
         DataSeries res = new DataSeries(ds, "BandPassSeries(" + ds.Description + "," + period + "," + delta + ")");
         double beta = Math.Cos(2 * Math.PI / period);
         double gamma = 1/ Math.Cos(4 * Math.PI * delta / period);
         double alpha = gamma - Math.Sqrt(gamma * gamma - 1d);
         
         for (int bar = 2; bar < ds.Count; bar++)
         {
            res[bar] = 0.5 * (1 - alpha) * (ds[bar] - ds[bar - 2])
               + beta * (1 + alpha) * res[bar - 1] - alpha * res[bar - 2];
         }         
         return res; 
      }
      
      public void SwamiMarketModeHeatMap(Bars bars, int plotThickness)
      {
         const double k = 1;
         int r = 0; int g = 0; int b = 0;
         string s = Bars.ToString() + ")";   
         DataSeries swMktMode = new DataSeries(bars, "swami(" + s);
         DataSeries[] swami = new DataSeries[49];
                  
         // Create and plot the heatmap series (change bar colors later)
         HideVolume();  HidePaneLines();
         ChartPane swPane = CreatePane(50, false, false );
         for( int n = 12; n < 49; n++ ) 
         {
            swami[n] = swMktMode + n;
            swami[n].Description = "SwamiSto." + n.ToString();   
            PlotSeries(swPane, swami[n], Color.LightGray, LineStyle.Solid, plotThickness);
         }
         
         for (int n = 12; n < 49; n++) 
         {
            DataSeries bp = BandPassSeries(AveragePrice.Series(bars), n, _delta.Value);
            DataSeries mean = SMA.Series(bp, 2 * n);
            
            DataSeries peak = new DataSeries(Bars, "peak()");
            DataSeries valley = new DataSeries(Bars, "valley()");
            double pk = 0d; 
            double v = 0d;
            for(int bar = 2; bar < Bars.Count; bar++)
            {            
               if( bp[bar-1] > bp[bar] && bp[bar-1] > bp[bar-2] ) 
                  pk = bp[bar - 1];
               if( bp[bar-1] < bp[bar] && bp[bar-1] < bp[bar-2] ) 
                  v = bp[bar-1];
               peak[bar] = pk;
               valley[bar] = v;
            }         
            int avgPer = (int)(2.5 * n);
            DataSeries avgPeak = _fraction.Value * SMA.Series(peak, avgPer);
            DataSeries avgValley = _fraction.Value * SMA.Series(valley, avgPer);
            
            for(int bar = 4; bar < Bars.Count; bar++)
            {
               double amp = avgPeak[bar] - avgValley[bar];
               if (amp == 0) continue;
               // ratio of trend slope to cycle amplitude
               double ratio =  mean[bar] / amp;
               
               // Inverse Fisher Transform
               ratio = (Math.Exp(2 * ratio) - 1)/ (Math.Exp(2 * ratio) + 1);   
               
               if (ratio > 0) {
                  r = Convert.ToInt32(255 * (k - ratio)); 
                  g = 255;
               }
               else {
                  r = 255;
                  g = Convert.ToInt32(255 * (k + ratio)); 
               }
               SetSeriesBarColor(bar, swami[n], Color.FromArgb(r, g, b));
            }
         }
      }
      
      protected override void Execute()
      {
         SwamiMarketModeHeatMap(Bars, _plotWidth.ValueInt);
      }
   }
}