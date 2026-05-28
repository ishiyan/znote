/* Code for the WealthLab.Strategies namespace */
public class MeasuringCyclePeriods : WealthScript
{
   public class ArrayHolder
   {   // current, old, older
      internal double I, I2, I3;
      internal double Q, Q2, Q3;
      internal double R, R2, R3;
      internal double Im, Im2, Im3;
      internal double A;
      internal double dB;
   }
   public DataSeries CycleFilterDC(DataSeries ds, out DataSeries sine, out DataSeries cosine)
   {
      double twoPi = 2 * Math.PI;
 
      // Initialize arrays
      ArrayHolder[] ah = new ArrayHolder[51];
      for( int n = 8; n  maxAmpl ? ah[n].A : maxAmpl;
         }
         double num = 0;   double den = 0;
         for( int n = 8; n  0 )
               ah[n].dB = 10 * Math.Log10( (1 - 0.99 * ah[n].A / maxAmpl) / 0.01 );
            ah[n].dB = ah[n].dB > 20 ? 20 : ah[n].dB;
            SetSeriesBarColor(bar, DB[n], color[(int)Math.Round(ah[n].dB)]);
 
            if( ah[n].dB  0 ) domCycle = num/den;
            result[bar] = domCycle;
 
            ah[n].I3 = ah[n].I2;
            ah[n].I2 = ah[n].I;
            ah[n].Q3 = ah[n].Q2;
            ah[n].Q2 = ah[n].Q;
            ah[n].R3 = ah[n].R2;
            ah[n].R2 = ah[n].R;
            ah[n].Im3 = ah[n].Im2;
            ah[n].Im2 = ah[n].Im;
         }
      }
      result = Median.Series(result, 10);
      PlotSeries(dbPane, result, Color.Lime, WealthLab.LineStyle.Solid, 2);
 
      // sine and cosine components
      sine = Low - Low;  sine.Description = "sine(DC)";
      double a2 = 0d;
      for(int bar = 10; bar > 1) );
      cosine.Description = "cosine(DC)";
 
      ChartPane sinePane = CreatePane( 40, false, false );
      for(int bar = 0; bar < Bars.Count; bar++)
         SetPaneBackgroundColor(sinePane, bar, Color.Black);
      PlotSeries(sinePane, sine, Color.Red, LineStyle.Solid, 1);
      PlotSeries(sinePane, cosine, Color.Cyan, LineStyle.Solid, 1);
      return result;
   }
 
   protected override void Execute()
   {
      HideVolume();
      DataSeries avgPrice = (High + Low) / 2;
      avgPrice.Description = "Avg Price";
 
      // Get the dominant cycle, sine and cosine, and plot the heat map
      DataSeries sine, cosine;
      DataSeries DC = CycleFilterDC(avgPrice, out sine, out cosine);
 
      /* Use the DC, sine, and cosine DataSeries in a Trading Strategy here */
   }