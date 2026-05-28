using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;

namespace WealthLab.Strategies
{
	public class TASC201609 : WealthScript
	{
		private StrategyParameter paramEnhance;

		public TASC201609()
		{
			paramEnhance = CreateParameter("Enhance Resolution", 0, 0, 1, 1);
        	}
		
		protected override void Execute()
		{
			bool EnhanceResolution = paramEnhance.ValueInt == 0 ? false : true;
			DataSeries HP = new DataSeries(Bars, "HP");
			DataSeries Filt = new DataSeries(Bars, "Filt");
			DataSeries DominantCycle = new DataSeries(Bars, "DominantCycle");

			double Deg2Rad = Math.PI / 180.0;
			double cosInDegrees = Math.Cos((.707 * 360 / 48d) * Deg2Rad);
			double sinInDegrees = Math.Sin((.707 * 360 / 48d) * Deg2Rad);
			double alpha1 = (cosInDegrees + sinInDegrees - 1) / cosInDegrees;
			double a1 = Math.Exp(-1.414 * Math.PI / 8.0);
			double b1 = 2.0 * a1 * Math.Cos((1.414 * 180d / 8.0) * Deg2Rad);
			double c2 = b1;
			double c3 = -a1 * a1;
			double c1 = 1 - c2 - c3;

			for (int bar = 2; bar < Bars.Count; bar++)
			{
				HP[bar] = 0.5*(1 + alpha1)*(Close[bar] - Close[bar-1]) + alpha1*HP[bar-1];
				//Smooth with a SuperSmoother Filter
				Filt[bar] = c1*(HP[bar] + HP[bar-1]) / 2 + c2*Filt[bar-1] + c3*Filt[bar-2];
			}
			
			DataSeries[] ds = new DataSeries[48];
			ChartPane tp = CreatePane(50,false,false);
			for( int n = 0; n < 48; n++ )
			{
				ds[n] = new DataSeries(Bars,n.ToString());
				for( int bar = 0; bar < Bars.Count; bar++ )
					ds[n][bar] = n;
				PlotSeries(tp, ds[n], Color.Black, LineStyle.Solid, 16);
			}
			HideVolume();
			
			for( int bar = 0; bar < Bars.Count; bar++)
			{
				SetPaneBackgroundColor(PricePane,bar,Color.Black);
				int AvgLength = 3, M = 0;
				double X = 0, Y = 0, Sx = 0, Sy = 0, Sxx = 0, Syy = 0, Sxy = 0;
				double[] Corr = new double[70];
				double[] CosinePart = new double[70];
				double[] SinePart = new double[70];
				double[] SqSum = new double[70];
				double[,] R = new double[70,2];
				double[] Pwr = new double[70];
			
				//Pearson correlation for each value of lag
				for(int Lag = 0; Lag <= 48; Lag++)
				{
					//Set the averaging length as M
					M = AvgLength;
					if( AvgLength == 0 )
						M = Lag;
					Sx = 0; Sy = 0; Sxx = 0; Syy = 0; Sxy = 0;

					for(int count = 0; count <= M-1; count++)
					{
						X = bar-count < 0 ? 0 : Filt[bar-count];
						Y = bar-Lag+count < 0 ? 0 : Filt[bar-Lag+count];
						Sx = Sx + X;
						Sy = Sy + Y;
						Sxx = Sxx + X*X;
						Sxy = Sxy + X*Y;
						Syy = Syy + Y*Y;
					}				

					if( (M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy) > 0 )
						Corr[Lag] = (M*Sxy-Sx*Sy)/Math.Sqrt((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy));
				}

				//Compute the Fourier Transform for each Correlation
				for(int Period = 0; Period <= 48; Period++)
				{
					CosinePart[Period] = 0;
					SinePart[Period] = 0;

					for(int N = 3; N <= 48; N++)
					{
						double _cosInDegrees = Math.Cos(((double)N * 360 / (double)Period) * Deg2Rad);
						double _sinInDegrees = Math.Sin(((double)N * 360 / (double)Period) * Deg2Rad);
					
						CosinePart[Period] = CosinePart[Period] + Corr[N]*_cosInDegrees;
						SinePart[Period] = SinePart[Period] + Corr[N]*_sinInDegrees;
					}

					SqSum[Period] = CosinePart[Period]*CosinePart[Period] + SinePart[Period]*SinePart[Period];
				}
			
				for(int Period = 8; Period <= 48; Period++)
				{
					R[Period, 1] = R[Period, 0];
					R[Period, 0] = 0.2*SqSum[Period]*SqSum[Period] + 0.8*R[Period,1];					
				}

				//Find Maximum Power Level for Normalization
				double MaxPwr = 0;
				for(int Period = 8; Period <= 48; Period++)
				{
					if( R[Period, 0] > MaxPwr )
						MaxPwr = R[Period, 0];
				}
				for(int Period = 8; Period <= 48; Period++)
				{
					Pwr[Period] = R[Period, 0] / MaxPwr;
				}
			
				//Optionally increase Display Resolution
				if( EnhanceResolution )
				{
					for(int Period = 8; Period <= 48; Period++)
					{
						Pwr[Period] = Math.Pow(Pwr[Period], 3);
					}
				}

				//Compute the dominant cycle using the CG of the spectrum
				double PeakPwr = 0, Spx = 0, Sp = 0;
				for(int Period = 8; Period <= 48; Period++)
				{
					if( Pwr[Period] > PeakPwr )
						PeakPwr = Pwr[Period];
				}				

				//Plot as a Heatmap
				double Color1 = 255, Color2 = 0, Color3 = 0;
				for(int Period = 8; Period < 48; Period++)
				{
					if( Pwr[Period] > 0.5 )
					{
						Color1 = 255;
						Color2 = 255*(2*Pwr[Period] - 1);
					}
					else
					{
						Color1 = 2*255*Pwr[Period];
						Color2 = 0;
					}
					
					Color1 = Math.Min((int)Color1,255); Color1 = Math.Max((int)Color1,0);
					Color2 = Math.Min((int)Color2,255); Color2 = Math.Max((int)Color2,0);
					Color3 = Math.Min((int)Color3,255); Color3 = Math.Max((int)Color3,0);
					
					SetSeriesBarColor(bar, ds[Period], Color.FromArgb(100,(int)Color1,(int)Color2,(int)Color3) );
				}
			}
		}
	}
}
