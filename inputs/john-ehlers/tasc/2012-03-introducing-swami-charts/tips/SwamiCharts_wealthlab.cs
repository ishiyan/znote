Wealth-Lab 6 strategy code (C#):

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;

namespace WealthLab.Strategies
{
   public class SwamiStochastics : WealthScript
   {   
      StrategyParameter _plotWidth;
      
      public SwamiStochastics()
      {
         _plotWidth = CreateParameter("Plot Width", 6, 2, 10, 1);
      }
      
      public class ArrayHolder
      {
         internal double Stoc, Num, Denom;
      }
      
      public void SwamiStochHeatMap(DataSeries ds, int plotThickness)
      {
         int r = 0; int g = 0; int b = 0;
         string s = ds.Description + ")";   
         DataSeries swStoch = new DataSeries(ds, "SwamiStoch(" + s);
         DataSeries[] swamistoch = new DataSeries[49];
         
         // Initialize array
         ArrayHolder[] ah = new ArrayHolder[49];   
         for( int n = 4; n < 49; n++ )
            ah[n] = new ArrayHolder();
         
         // Create and plot the heatmap series (change bar colors later)
         HideVolume();  HidePaneLines();
         ChartPane swPane = CreatePane(50, false, false );
         for( int n = 4; n < 49; n++ ) 
         {
            swamistoch[n] = swStoch + n;
            swamistoch[n].Description = "SwamiSto." + n.ToString();   
            PlotSeries(swPane, swamistoch[n], Color.LightGray, LineStyle.Solid, plotThickness);
         }
         
         for(int bar = 48; bar < Bars.Count; bar++)
         {         
            double num2, denom2, stoch2;

            for (int n = 4; n < 49; n++) 
            {
               num2 = ah[n].Num;
               denom2 = ah[n].Denom;
               stoch2 = ah[n].Stoc;
               
               double hh = 0;
               double ll = 1e10;
               for (int j = 0; j < n; j++)   
               {
                  if (ds[bar - j] > hh) hh = ds[bar - j];
                  if (ds[bar - j] < ll) ll = ds[bar - j];
               }
               ah[n].Num = 0.5 * (ds[bar] - ll) + 0.5 * num2;
               ah[n].Denom = 0.5 * (hh - ll) + 0.5 * denom2;
               if (ah[n].Denom != 0)
               {
                  ah[n].Stoc = 0.2 * (ah[n].Num / ah[n].Denom) + 0.8 * stoch2;
               }
               
               if (ah[n].Stoc >= 0.5) {                  
                  r = Convert.ToInt32(255 * (2 - 2 * ah[n].Stoc)); 
                  g = 255;
               }
               else {
                  r = 255;
                  g = Convert.ToInt32(255 * 2 * ah[n].Stoc);
               }
               SetSeriesBarColor(bar, swamistoch[n], Color.FromArgb(r, g, b));   
            }
         }         
      }      
      
      protected override void Execute()
      {
         SwamiStochHeatMap(Close, _plotWidth.ValueInt);      
      }
   }
}
