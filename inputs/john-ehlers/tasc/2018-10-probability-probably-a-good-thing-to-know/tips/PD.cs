using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using TASCIndicators;	//required
using System.IO;		//required for plotting
using System.Windows.Forms.DataVisualization.Charting;
//1. Click "References...", then "Other Assemblies..." > "Add a reference"
//2. In "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\" (or "Framework" on 32-bit systems),
//choose and okay "System.Windows.Forms.DataVisualization.dll"

namespace WealthLab.Strategies
{
	public class MyStrategy : WealthScript
	{
		protected override void Execute()
		{
			var rrsi = RocketRSI.Series(Close,8,10);
			ChartPane paneRocketRSI = CreatePane(40,true,true);				PlotSeries(paneRocketRSI,rrsi,Color.DarkBlue,LineStyle.Solid,2);
			
			double[] bin = new double[61];			
			for(int bar = GetTradingLoopStartBar(10 * 3); bar < Bars.Count; bar++) {
				for(int i = 1; i <= 60; i++)				
				//Bin the indicator values in Bins from -3 to +3
				{
					double j = (i - 31) / 10d;
					double k = (i - 30) / 10d;
					if( rrsi[bar] > j && rrsi[bar] <= k)
						bin[i] = bin[i] + 1;
				}
			}

			Chart chart = new Chart();						
			//Histogram chart
			chart.Width = 600;
			string name = "Bins";
			chart.ChartAreas.Add(name);
			chart.ChartAreas[0].AxisX.MajorGrid.Enabled = chart.ChartAreas[0].AxisY.MajorGrid.Enabled = false;
			chart.ChartAreas[0].AxisX.Title = "Deviation";	
			//Custom axis titles
			chart.ChartAreas[0].AxisY.Title = "Occurences";
			chart.Series.Add(name);
			chart.Series[name].ChartType = SeriesChartType.Column;

			for(int b = 0; b < bin.GetLength(0); b++)
				chart.Series[name].Points.AddXY( (b - 31)/10d, bin[b]);
			
			using (MemoryStream memStream = new MemoryStream()) {
				chart.SaveImage(memStream, ChartImageFormat.Png);				
				Image img = Image.FromStream(memStream);
				DrawImage( PricePane, img, Bars.Count-50, Close[Bars.Count-50], false );
			}
		}
	}
}
