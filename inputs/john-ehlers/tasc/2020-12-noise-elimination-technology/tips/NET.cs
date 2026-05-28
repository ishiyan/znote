using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
        public class TASC2020_12 : WealthScript
{
               protected override void Execute()
               {
                       var ds = Close;
                var period = 14;

                        var myrsi2 = new MyRSI(ds,0,period,
                             string.Format("MyRSI v2.0 ({0},{1})",ds.Description,period),true);
                      var net = NET.Series(ds, period, period);
                       var signalLine = EMAModern.Series(net, 5);
                      signalLine.Description = string.Format("Signal line of {0}", net.Description);
                  var bbl = BBandLower.Series(net, 100, 1.0);
                     var bbu = BBandUpper.Series(net, 100, 1.0);
                     
                        for(int bar = GetTradingLoopStartBar( period ); bar < Bars.Count; bar++)
                        {
                               if (IsLastPositionActive)
                               {
                                       if (CrossUnder(bar, net, signalLine))
                                           SellAtMarket( bar + 1, LastPosition );
                          }
                               else
                            {
                                       if(CrossOver(bar,net,signalLine))
                                               BuyAtMarket( bar + 1 );
                        }
                       }

                       var ls = LineStyle.Solid; HideVolume();
                ChartPane paneNET = CreatePane( 40,false,true );
                        PlotSeries( paneNET,net,Color.Blue,ls,2);
                       PlotSeries( paneNET,myrsi2,Color.Red,ls,1);
                     PlotSeries( paneNET,signalLine,Color.LightCoral,ls,1);
                  PlotSeriesFillBand( paneNET, bbl, bbu,
                          Color.FromArgb(255, 176, 196, 222), Color.Transparent, ls, 2);
          }
       }
}
