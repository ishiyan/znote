//+------------------------------------------------------------------+
//|                                                     Blau_CSI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Candlestick Index (William Blau)"        // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 13           // number of buffers used
#property indicator_plots   1            // number of graphic plots
//--- horizontal levels
#property indicator_level1 -25           // level #0
#property indicator_level2 25            // level #1
#property indicator_levelcolor Silver    // level line color
#property indicator_levelstyle STYLE_DOT // level line
#property indicator_levelwidth 1         // level line width
//--- scale
#property indicator_minimum -100         // lower bound
#property indicator_maximum 100          // upper bound
//--- graphic plot #0 (Main)
#property indicator_label1  "CSI"        // label of graphic plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // line width
//--- input parameters
input int    q=1;  // q - period of Candlestick Momentum
input int    r=20; // r - 1st EMA, applied to Candlestick Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice1=PRICE_CLOSE; // AppliedPrice1 - price type [close]
input ENUM_APPLIED_PRICE AppliedPrice2=PRICE_OPEN;  // AppliedPrice2 - price type [open]
//--- dynamic arrays
double MainBuffer[];      // CSI (graphic plot #0)
double Price1Buffer[];    // price array [close price]
double Price2Buffer[];    // price array [open price]
double LLBuffer[];        // lowest prices (q bars)
double HHBuffer[];        // highest prices (q bars)
double CMtmBuffer[];      // q-period Candlestic Momentum
double EMA_CMtmBuffer[];  // r-period 1st EMA
double DEMA_CMtmBuffer[]; // s-period 2nd EMA
double TEMA_CMtmBuffer[]; // u-period 3rd EMA
double HHLLBuffer[];      // q-period price range
double EMA_HHLLBuffer[];  // r-period 1st EMA (price range)
double DEMA_HHLLBuffer[]; // s-period 2nd EMA (price range)
double TEMA_HHLLBuffer[]; // u-period 3rd EMA (price range)
//--- global variables
int    begin1, begin2, begin3, begin4; // starting indexes
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);               // CSI
   // buffers for intermediate calculations
   SetIndexBuffer(1,Price1Buffer,INDICATOR_CALCULATIONS);     // price array [close]
   SetIndexBuffer(2,Price2Buffer,INDICATOR_CALCULATIONS);     // price array [open]
   SetIndexBuffer(3,LLBuffer,INDICATOR_CALCULATIONS);         // lowest prices (q bars)
   SetIndexBuffer(4,HHBuffer,INDICATOR_CALCULATIONS);         // highest prices (q bars)
   SetIndexBuffer(5,CMtmBuffer,INDICATOR_CALCULATIONS);       // q-period Candlestick Momentum
   SetIndexBuffer(6,EMA_CMtmBuffer,INDICATOR_CALCULATIONS);   // r-period 1st EMA
   SetIndexBuffer(7,DEMA_CMtmBuffer,INDICATOR_CALCULATIONS);  // s-period 2nd EMA
   SetIndexBuffer(8,TEMA_CMtmBuffer,INDICATOR_CALCULATIONS);  // u-period 3rd EMA
   SetIndexBuffer(9,HHLLBuffer,INDICATOR_CALCULATIONS);       // q-period Price Range
   SetIndexBuffer(10,EMA_HHLLBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA (price range)
   SetIndexBuffer(11,DEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA (price range)
   SetIndexBuffer(12,TEMA_HHLLBuffer,INDICATOR_CALCULATIONS); // u-period 3rd EMA (price range)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"CSI");             // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,-25);         // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,25);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level line color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level line style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level line width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level #0 description "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level #1 description "Overbought"
//--- scale
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // lower bound
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // upper bound
*/
//---
   begin1=q-1;        //                             - CMtmBuffer[], HHLLBuffer[], LLBuffer[], HHBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice1)+","+PriceName(AppliedPrice2)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_CSI("+shortname+")");
//--- OnInit done
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(
                const int rates_total,     // rates total
                const int prev_calculated, // bars, calculated at previous call
                const datetime &Time[],    // Time
                const double &Open[],      // Open
                const double &High[],      // High
                const double &Low[],       // Low
                const double &Close[],     // Close
                const long &TickVolume[],  // Tick Volume
                const long &Volume[],      // Real Volume
                const int &Spread[]        // Spread
               )
  {
   int i,k,pos;
   double min,max;
   double value1,value2;
//--- check rates
   if(rates_total<rates_total_min) return(0);
//--- calculation of Price1Buffer[] and Price2Buffer[]
   CalculatePriceBuffer(
                        AppliedPrice1,       // applied price [close]
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        Price1Buffer         // target array
                       );
   CalculatePriceBuffer(AppliedPrice2,rates_total,prev_calculated,Open,High,Low,Close,Price2Buffer);
//--- calculation of cmtm and q-period price range
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // 
      for(i=0;i<pos;i++)       // 
        {
         CMtmBuffer[i]=0.0;    // zero values
         HHLLBuffer[i]=0.0;    //
         LLBuffer[i]=0.0;      //
         HHBuffer[i]=0.0;      //
        }
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of CMtmBuffer[], HHLLBuffer[], LLBuffer[], HHBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      // CMtmBuffer[] - q-периодный моментум свечи
      CMtmBuffer[i]=Price1Buffer[i]-Price2Buffer[i-(q-1)];
      // LLBuffer[] - search for the lowest price (q bars)
      // HHBuffer[] - search for the highes price (q bars)
      min=1000000.0;
      max=-1000000.0;
      for(k=i-(q-1);k<=i;k++)
        {
         if(min>Low[k])  min=Low[k];
         if(max<High[k]) max=High[k];
        }
      LLBuffer[i]=min;
      HHBuffer[i]=max;
      // HHLLBuffer[] - price range (q bars)
      HHLLBuffer[i]=HHBuffer[i]-LLBuffer[i];
     }
//--- EMA smoothing
   // 1st EMA(r)
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           CMtmBuffer,      // input array
                           EMA_CMtmBuffer   // target array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,HHLLBuffer,EMA_HHLLBuffer);
   // 2nd EMA(s)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_CMtmBuffer,DEMA_CMtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_HHLLBuffer,DEMA_HHLLBuffer);
   // 3rd EMA(u)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_CMtmBuffer,TEMA_CMtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_HHLLBuffer,TEMA_HHLLBuffer);
//--- calculation of CSI (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // 
      for(i=0;i<pos;i++)       // 
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_CMtmBuffer[i];
      value2=TEMA_HHLLBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+