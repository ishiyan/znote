unit WealthLab_TLB;

// ************************************************************************ //
// WARNING                                                                    
// -------                                                                    
// The types declared in this file were generated from data read from a       
// Type Library. If this type library is explicitly or indirectly (via        
// another type library referring to this type library) re-imported, or the   
// 'Refresh' command of the Type Library Editor activated while editing the   
// Type Library, the contents of this file will be regenerated and all        
// manual modifications will be lost.                                         
// ************************************************************************ //

// PASTLWTR : $Revision:   1.130.1.0.1.0.1.6  $
// File generated on 22.06.2005 17:49:10 from Type Library described below.

// ************************************************************************  //
// Type Lib: C:\Program Files\Wealth-Lab, Inc\Wealth-Lab Developer 3.0\WealthLab.exe (1)
// LIBID: {0E7B08D3-3C2C-450F-8AFF-56B6681FF949}
// LCID: 0
// Helpfile: 
// DepndLst: 
//   (1) v2.0 stdole, (C:\WINDOWS\system32\STDOLE2.TLB)
// Parent TypeLibrary:
//   (0) v0.99 Jurik, (C:\Program Files\Borland\Delphi6\Projects\Jurik\Jurik.tlb)
// ************************************************************************ //
{$TYPEDADDRESS OFF} // Unit must be compiled without type-checked pointers. 
{$WARN SYMBOL_PLATFORM OFF}
{$WRITEABLECONST ON}
{$VARPROPSETTER ON}
interface

uses Windows, ActiveX, Classes, Graphics, StdVCL, Variants;
  

// *********************************************************************//
// GUIDS declared in the TypeLibrary. Following prefixes are used:        
//   Type Libraries     : LIBID_xxxx                                      
//   CoClasses          : CLASS_xxxx                                      
//   DISPInterfaces     : DIID_xxxx                                       
//   Non-DISP interfaces: IID_xxxx                                        
// *********************************************************************//
const
  // TypeLibrary Major and minor versions
  WealthLabMajorVersion = 1;
  WealthLabMinorVersion = 0;

  LIBID_WealthLab: TGUID = '{0E7B08D3-3C2C-450F-8AFF-56B6681FF949}';

  IID_IWL3: TGUID = '{C533B87D-35BD-4DD9-9342-505C5D3DB8D9}';
  CLASS_WL3: TGUID = '{2D938932-5A0D-4187-802C-B1B226A73250}';
  IID_IWealthLabAlert3: TGUID = '{7E90EC7D-0B7C-478A-9B2E-087BE27B2C8A}';
  IID_IWealthLabPaintHook3: TGUID = '{52885F0C-0C0F-459E-A852-4E761AB790F7}';
  IID_IWealthLabStrings3: TGUID = '{58C5163B-1137-4F26-BE49-88FB36767FB0}';
  IID_IWealthLabBars3: TGUID = '{DBD2163C-0DDF-418C-B33E-A858588D14D1}';
  IID_IWealthLabRTUpdate3: TGUID = '{B156F55D-C8EB-48CD-B208-79B11539AB31}';
  IID_IWealthLabAddOn3: TGUID = '{CFFD9D91-C3B4-4A0E-8857-0D921410083F}';
  IID_IWealthLabEOD3: TGUID = '{6D882A9B-92B7-4AA2-B7B9-A46D5106C044}';
  IID_IWealthLabRT3: TGUID = '{D0094852-6143-4F3B-98F2-9CE3D97F1ACB}';
  IID_IWealthLabQuoteUpdate3: TGUID = '{A9C56942-D02B-45CC-BEA2-F14D811DBCC3}';
  IID_IWealthLabChart3: TGUID = '{BCA09198-01C8-45C0-99F4-C6DEBB2ED047}';
  IID_IWealthLabChartStyle3: TGUID = '{B0B7D42A-A099-413E-B3CD-351870AA652F}';
  IID_IWealthLabConnection3: TGUID = '{7E6B4954-F684-4811-8C27-4CB5B6FD18E4}';
  IID_IWealthLabBroker3: TGUID = '{F69866BA-AD3B-4DC0-8CC3-DEFAD5C6F6A4}';
  IID_IWealthLabBrokerUpdate3: TGUID = '{3C215795-D637-4924-8A59-7272E07DBF2A}';
  IID_IWealthLabBroker3B: TGUID = '{56229677-44A0-4BDE-840D-7F10E599F97B}';

// *********************************************************************//
// Declaration of Enumerations defined in Type Library                    
// *********************************************************************//
// Constants for enum AlertTypeEnum
type
  AlertTypeEnum = TOleEnum;
const
  alertBuy = $00000000;
  alertSell = $00000001;
  alertShort = $00000002;
  alertCover = $00000003;

// Constants for enum OrderTypeEnum
type
  OrderTypeEnum = TOleEnum;
const
  orderMarket = $00000000;
  orderLimit = $00000001;
  orderStop = $00000002;

// Constants for enum PositionTypeEnum
type
  PositionTypeEnum = TOleEnum;
const
  posLong = $00000000;
  posShort = $00000001;

// Constants for enum BarIntervalEnum
type
  BarIntervalEnum = TOleEnum;
const
  biMinutes = $00000000;
  biDaily = $00000001;
  biTicks = $00000002;
  biSeconds = $00000003;
  biWeekly = $00000004;
  biMonthly = $00000005;

// Constants for enum SecurityTypeEnum
type
  SecurityTypeEnum = TOleEnum;
const
  securityStock = $00000000;
  securityFuture = $00000001;

type

// *********************************************************************//
// Forward declaration of types defined in TypeLibrary                    
// *********************************************************************//
  IWL3 = interface;
  IWL3Disp = dispinterface;
  IWealthLabAlert3 = interface;
  IWealthLabAlert3Disp = dispinterface;
  IWealthLabPaintHook3 = interface;
  IWealthLabPaintHook3Disp = dispinterface;
  IWealthLabStrings3 = interface;
  IWealthLabStrings3Disp = dispinterface;
  IWealthLabBars3 = interface;
  IWealthLabBars3Disp = dispinterface;
  IWealthLabRTUpdate3 = interface;
  IWealthLabRTUpdate3Disp = dispinterface;
  IWealthLabAddOn3 = interface;
  IWealthLabAddOn3Disp = dispinterface;
  IWealthLabEOD3 = interface;
  IWealthLabEOD3Disp = dispinterface;
  IWealthLabRT3 = interface;
  IWealthLabRT3Disp = dispinterface;
  IWealthLabQuoteUpdate3 = interface;
  IWealthLabQuoteUpdate3Disp = dispinterface;
  IWealthLabChart3 = interface;
  IWealthLabChart3Disp = dispinterface;
  IWealthLabChartStyle3 = interface;
  IWealthLabChartStyle3Disp = dispinterface;
  IWealthLabConnection3 = interface;
  IWealthLabConnection3Disp = dispinterface;
  IWealthLabBroker3 = interface;
  IWealthLabBroker3Disp = dispinterface;
  IWealthLabBrokerUpdate3 = interface;
  IWealthLabBrokerUpdate3Disp = dispinterface;
  IWealthLabBroker3B = interface;
  IWealthLabBroker3BDisp = dispinterface;

// *********************************************************************//
// Declaration of CoClasses defined in Type Library                       
// (NOTE: Here we map each CoClass to its Default Interface)              
// *********************************************************************//
  WL3 = IWL3;


// *********************************************************************//
// Declaration of structures, unions and aliases.                         
// *********************************************************************//
  PDouble1 = ^Double; {*}


// *********************************************************************//
// Interface: IWL3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {C533B87D-35BD-4DD9-9342-505C5D3DB8D9}
// *********************************************************************//
  IWL3 = interface(IDispatch)
    ['{C533B87D-35BD-4DD9-9342-505C5D3DB8D9}']
    procedure ExecuteScript(const Script: WideString; const WatchList: WideString; 
                            const Symbol: WideString); safecall;
    procedure WebUpdate(const DataSource: WideString); safecall;
    procedure AddAlert(const Symbol: WideString; AlertType: AlertTypeEnum; Shares: Integer; 
                       OrderType: OrderTypeEnum; AlertPrice: Double); safecall;
    procedure ActivateAlertManager(Activate: WordBool); safecall;
    procedure SuspendAlerts(Suspend: WordBool); safecall;
    procedure DeleteAlerts(const Symbol: WideString); safecall;
    function GetAlertList(const Symbol: WideString): WideString; safecall;
    procedure InstallAlertHook(const Hook: IWealthLabAlert3); safecall;
    procedure BidAskFilter(Filter: WordBool); safecall;
    procedure CloseWindows; safecall;
    procedure ActivateQuoteManager(Activate: WordBool); safecall;
    function SimBarCount: Integer; safecall;
    function SimDate(Bar: Integer): TDateTime; safecall;
    function SimTradeCount: Integer; safecall;
    function SimTradeInfo(Trade: Integer): WideString; safecall;
    function ExecuteScriptTimed(const Script: WideString; const WatchList: WideString; 
                                const Symbol: WideString): Integer; safecall;
    function WatchListSymbols(const WatchList: WideString): WideString; safecall;
    function WatchListNames: WideString; safecall;
    procedure SetChartScriptRange(RangeType: Integer; RangeValue: Integer; StartDate: TDateTime; 
                                  EndDate: TDateTime); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWL3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {C533B87D-35BD-4DD9-9342-505C5D3DB8D9}
// *********************************************************************//
  IWL3Disp = dispinterface
    ['{C533B87D-35BD-4DD9-9342-505C5D3DB8D9}']
    procedure ExecuteScript(const Script: WideString; const WatchList: WideString; 
                            const Symbol: WideString); dispid 201;
    procedure WebUpdate(const DataSource: WideString); dispid 202;
    procedure AddAlert(const Symbol: WideString; AlertType: AlertTypeEnum; Shares: Integer; 
                       OrderType: OrderTypeEnum; AlertPrice: Double); dispid 203;
    procedure ActivateAlertManager(Activate: WordBool); dispid 204;
    procedure SuspendAlerts(Suspend: WordBool); dispid 205;
    procedure DeleteAlerts(const Symbol: WideString); dispid 206;
    function GetAlertList(const Symbol: WideString): WideString; dispid 207;
    procedure InstallAlertHook(const Hook: IWealthLabAlert3); dispid 208;
    procedure BidAskFilter(Filter: WordBool); dispid 209;
    procedure CloseWindows; dispid 210;
    procedure ActivateQuoteManager(Activate: WordBool); dispid 211;
    function SimBarCount: Integer; dispid 212;
    function SimDate(Bar: Integer): TDateTime; dispid 213;
    function SimTradeCount: Integer; dispid 214;
    function SimTradeInfo(Trade: Integer): WideString; dispid 215;
    function ExecuteScriptTimed(const Script: WideString; const WatchList: WideString; 
                                const Symbol: WideString): Integer; dispid 216;
    function WatchListSymbols(const WatchList: WideString): WideString; dispid 217;
    function WatchListNames: WideString; dispid 218;
    procedure SetChartScriptRange(RangeType: Integer; RangeValue: Integer; StartDate: TDateTime; 
                                  EndDate: TDateTime); dispid 219;
  end;

// *********************************************************************//
// Interface: IWealthLabAlert3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {7E90EC7D-0B7C-478A-9B2E-087BE27B2C8A}
// *********************************************************************//
  IWealthLabAlert3 = interface(IDispatch)
    ['{7E90EC7D-0B7C-478A-9B2E-087BE27B2C8A}']
    procedure Trigger(const Symbol: WideString; Shares: Integer; AlertType: AlertTypeEnum; 
                      OrderType: OrderTypeEnum; AlertPrice: Double; ExecutePrice: Double; 
                      Bid: Double; Ask: Double; High: Double; Low: Double; OpenPrice: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabAlert3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {7E90EC7D-0B7C-478A-9B2E-087BE27B2C8A}
// *********************************************************************//
  IWealthLabAlert3Disp = dispinterface
    ['{7E90EC7D-0B7C-478A-9B2E-087BE27B2C8A}']
    procedure Trigger(const Symbol: WideString; Shares: Integer; AlertType: AlertTypeEnum; 
                      OrderType: OrderTypeEnum; AlertPrice: Double; ExecutePrice: Double; 
                      Bid: Double; Ask: Double; High: Double; Low: Double; OpenPrice: Double); dispid 201;
  end;

// *********************************************************************//
// Interface: IWealthLabPaintHook3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {52885F0C-0C0F-459E-A852-4E761AB790F7}
// *********************************************************************//
  IWealthLabPaintHook3 = interface(IDispatch)
    ['{52885F0C-0C0F-459E-A852-4E761AB790F7}']
    procedure Paint(DC: Integer; Width: Integer; Height: Integer; Offset: Integer; 
                    BarSpacing: Integer; Top: Integer; Bottom: Integer; PreBars: WordBool; 
                    const WL: IWealthLabAddOn3); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabPaintHook3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {52885F0C-0C0F-459E-A852-4E761AB790F7}
// *********************************************************************//
  IWealthLabPaintHook3Disp = dispinterface
    ['{52885F0C-0C0F-459E-A852-4E761AB790F7}']
    procedure Paint(DC: Integer; Width: Integer; Height: Integer; Offset: Integer; 
                    BarSpacing: Integer; Top: Integer; Bottom: Integer; PreBars: WordBool; 
                    const WL: IWealthLabAddOn3); dispid 201;
  end;

// *********************************************************************//
// Interface: IWealthLabStrings3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {58C5163B-1137-4F26-BE49-88FB36767FB0}
// *********************************************************************//
  IWealthLabStrings3 = interface(IDispatch)
    ['{58C5163B-1137-4F26-BE49-88FB36767FB0}']
    procedure Add(const Value: WideString); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabStrings3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {58C5163B-1137-4F26-BE49-88FB36767FB0}
// *********************************************************************//
  IWealthLabStrings3Disp = dispinterface
    ['{58C5163B-1137-4F26-BE49-88FB36767FB0}']
    procedure Add(const Value: WideString); dispid 201;
  end;

// *********************************************************************//
// Interface: IWealthLabBars3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {DBD2163C-0DDF-418C-B33E-A858588D14D1}
// *********************************************************************//
  IWealthLabBars3 = interface(IDispatch)
    ['{DBD2163C-0DDF-418C-B33E-A858588D14D1}']
    procedure Add(Date: TDateTime; Open: Double; High: Double; Low: Double; Close: Double; 
                  Volume: Integer); safecall;
    procedure AddOpenInterest(Date: TDateTime; Open: Double; High: Double; Low: Double; 
                              Close: Double; Volume: Integer; OpenInterest: Integer); safecall;
    procedure AddBarData(Date: TDateTime; Open: Double; High: Double; Low: Double; Close: Double; 
                         Volume: Double; OpenInterest: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabBars3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {DBD2163C-0DDF-418C-B33E-A858588D14D1}
// *********************************************************************//
  IWealthLabBars3Disp = dispinterface
    ['{DBD2163C-0DDF-418C-B33E-A858588D14D1}']
    procedure Add(Date: TDateTime; Open: Double; High: Double; Low: Double; Close: Double; 
                  Volume: Integer); dispid 201;
    procedure AddOpenInterest(Date: TDateTime; Open: Double; High: Double; Low: Double; 
                              Close: Double; Volume: Integer; OpenInterest: Integer); dispid 202;
    procedure AddBarData(Date: TDateTime; Open: Double; High: Double; Low: Double; Close: Double; 
                         Volume: Double; OpenInterest: Double); dispid 203;
  end;

// *********************************************************************//
// Interface: IWealthLabRTUpdate3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {B156F55D-C8EB-48CD-B208-79B11539AB31}
// *********************************************************************//
  IWealthLabRTUpdate3 = interface(IDispatch)
    ['{B156F55D-C8EB-48CD-B208-79B11539AB31}']
    procedure Update; safecall;
    procedure UpdateGhostBar(Open: Double; High: Double; Low: Double; Close: Double; Volume: Integer); safecall;
    procedure UpdateBidAsk(Bid: Double; Ask: Double); safecall;
    procedure UpdateGhostBarBidAsk(Open: Double; High: Double; Low: Double; Close: Double; 
                                   Volume: Integer; Bid: Double; Ask: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabRTUpdate3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {B156F55D-C8EB-48CD-B208-79B11539AB31}
// *********************************************************************//
  IWealthLabRTUpdate3Disp = dispinterface
    ['{B156F55D-C8EB-48CD-B208-79B11539AB31}']
    procedure Update; dispid 201;
    procedure UpdateGhostBar(Open: Double; High: Double; Low: Double; Close: Double; Volume: Integer); dispid 202;
    procedure UpdateBidAsk(Bid: Double; Ask: Double); dispid 204;
    procedure UpdateGhostBarBidAsk(Open: Double; High: Double; Low: Double; Close: Double; 
                                   Volume: Integer; Bid: Double; Ask: Double); dispid 205;
  end;

// *********************************************************************//
// Interface: IWealthLabAddOn3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {CFFD9D91-C3B4-4A0E-8857-0D921410083F}
// *********************************************************************//
  IWealthLabAddOn3 = interface(IDispatch)
    ['{CFFD9D91-C3B4-4A0E-8857-0D921410083F}']
    function ClosePosition(Position: Integer; Bar: Integer; Price: Double; 
                           OrderType: OrderTypeEnum; const SignalName: WideString): WordBool; safecall;
    function OpenPosition(Bar: Integer; PositionType: PositionTypeEnum; Shares: Integer; 
                          Price: Double; OrderType: OrderTypeEnum; const SignalName: WideString): WordBool; safecall;
    function BarCount: Integer; safecall;
    function Date(Bar: Integer): TDateTime; safecall;
    function GetSeriesValue(Bar: Integer; Series: Integer): Double; safecall;
    function LastPosition: Integer; safecall;
    function PriceClose(Bar: Integer): Double; safecall;
    function PriceOpen(Bar: Integer): Double; safecall;
    function PriceHigh(Bar: Integer): Double; safecall;
    function PriceLow(Bar: Integer): Double; safecall;
    function Volume(Bar: Integer): Integer; safecall;
    procedure SetSeriesValue(Bar: Integer; Series: Integer; Value: Double); safecall;
    function GetPositionData(Position: Integer): Double; safecall;
    function PositionActive(Position: Integer): WordBool; safecall;
    function PositionCount: Integer; safecall;
    function PositionEntryBar(Position: Integer): Integer; safecall;
    function PositionEntryPrice(Position: Integer): Double; safecall;
    function PositionExitBar(Position: Integer): Integer; safecall;
    function PositionExitPrice(Position: Integer): Double; safecall;
    function PositionLong(Position: Integer): WordBool; safecall;
    function PositionShares(Position: Integer): Integer; safecall;
    procedure AddScanColumn(const Name: WideString; Value: Double); safecall;
    procedure SetPositionData(Position: Integer; Value: Double); safecall;
    procedure InstallPaintHook(const Hook: IWealthLabPaintHook3); safecall;
    function BarToX(Bar: Integer): Integer; safecall;
    function PriceToY(Price: Double): Integer; safecall;
    procedure PopulateSeries(Series: Integer; var Values: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabAddOn3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {CFFD9D91-C3B4-4A0E-8857-0D921410083F}
// *********************************************************************//
  IWealthLabAddOn3Disp = dispinterface
    ['{CFFD9D91-C3B4-4A0E-8857-0D921410083F}']
    function ClosePosition(Position: Integer; Bar: Integer; Price: Double; 
                           OrderType: OrderTypeEnum; const SignalName: WideString): WordBool; dispid 201;
    function OpenPosition(Bar: Integer; PositionType: PositionTypeEnum; Shares: Integer; 
                          Price: Double; OrderType: OrderTypeEnum; const SignalName: WideString): WordBool; dispid 202;
    function BarCount: Integer; dispid 203;
    function Date(Bar: Integer): TDateTime; dispid 204;
    function GetSeriesValue(Bar: Integer; Series: Integer): Double; dispid 205;
    function LastPosition: Integer; dispid 206;
    function PriceClose(Bar: Integer): Double; dispid 207;
    function PriceOpen(Bar: Integer): Double; dispid 208;
    function PriceHigh(Bar: Integer): Double; dispid 209;
    function PriceLow(Bar: Integer): Double; dispid 210;
    function Volume(Bar: Integer): Integer; dispid 211;
    procedure SetSeriesValue(Bar: Integer; Series: Integer; Value: Double); dispid 212;
    function GetPositionData(Position: Integer): Double; dispid 213;
    function PositionActive(Position: Integer): WordBool; dispid 214;
    function PositionCount: Integer; dispid 215;
    function PositionEntryBar(Position: Integer): Integer; dispid 216;
    function PositionEntryPrice(Position: Integer): Double; dispid 217;
    function PositionExitBar(Position: Integer): Integer; dispid 218;
    function PositionExitPrice(Position: Integer): Double; dispid 219;
    function PositionLong(Position: Integer): WordBool; dispid 220;
    function PositionShares(Position: Integer): Integer; dispid 221;
    procedure AddScanColumn(const Name: WideString; Value: Double); dispid 222;
    procedure SetPositionData(Position: Integer; Value: Double); dispid 223;
    procedure InstallPaintHook(const Hook: IWealthLabPaintHook3); dispid 224;
    function BarToX(Bar: Integer): Integer; dispid 225;
    function PriceToY(Price: Double): Integer; dispid 226;
    procedure PopulateSeries(Series: Integer; var Values: Double); dispid 227;
  end;

// *********************************************************************//
// Interface: IWealthLabEOD3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {6D882A9B-92B7-4AA2-B7B9-A46D5106C044}
// *********************************************************************//
  IWealthLabEOD3 = interface(IDispatch)
    ['{6D882A9B-92B7-4AA2-B7B9-A46D5106C044}']
    function GetSecurityName(const Symbol: WideString): WideString; safecall;
    function CreateDataSource: WideString; safecall;
    procedure FillSymbols(const DSString: WideString; const Symbols: IWealthLabStrings3); safecall;
    procedure LoadSymbol(const DSString: WideString; const Symbol: WideString; 
                         const Bars: IWealthLabBars3; StartDate: TDateTime; EndDate: TDateTime; 
                         MaxBars: Integer); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabEOD3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {6D882A9B-92B7-4AA2-B7B9-A46D5106C044}
// *********************************************************************//
  IWealthLabEOD3Disp = dispinterface
    ['{6D882A9B-92B7-4AA2-B7B9-A46D5106C044}']
    function GetSecurityName(const Symbol: WideString): WideString; dispid 201;
    function CreateDataSource: WideString; dispid 202;
    procedure FillSymbols(const DSString: WideString; const Symbols: IWealthLabStrings3); dispid 203;
    procedure LoadSymbol(const DSString: WideString; const Symbol: WideString; 
                         const Bars: IWealthLabBars3; StartDate: TDateTime; EndDate: TDateTime; 
                         MaxBars: Integer); dispid 204;
  end;

// *********************************************************************//
// Interface: IWealthLabRT3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {D0094852-6143-4F3B-98F2-9CE3D97F1ACB}
// *********************************************************************//
  IWealthLabRT3 = interface(IDispatch)
    ['{D0094852-6143-4F3B-98F2-9CE3D97F1ACB}']
    function GetSecurityName(const Symbol: WideString): WideString; safecall;
    procedure CloseRequest; safecall;
    procedure OpenRequest(const Symbol: WideString; NumBars: Integer; RequestType: BarIntervalEnum; 
                          BarInterval: Integer; FilterMarketHours: WordBool; MarketOpen: TDateTime; 
                          MarketClose: TDateTime; const Bars: IWealthLabBars3; 
                          const UpdateSink: IWealthLabRTUpdate3); safecall;
    function SupportsRequest(RequestType: BarIntervalEnum): WordBool; safecall;
    procedure AssignConnectionStatus(const Conn: IWealthLabConnection3); safecall;
    function SupportsQuotes: WordBool; safecall;
    procedure AddSymbol(const Symbol: WideString; Item: Integer); safecall;
    procedure RemoveSymbol(const Symbol: WideString; Item: Integer); safecall;
    procedure ClearSymbols; safecall;
    procedure ActivateQuotes(const Update: IWealthLabQuoteUpdate3); safecall;
    procedure DeactivateQuotes; safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabRT3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {D0094852-6143-4F3B-98F2-9CE3D97F1ACB}
// *********************************************************************//
  IWealthLabRT3Disp = dispinterface
    ['{D0094852-6143-4F3B-98F2-9CE3D97F1ACB}']
    function GetSecurityName(const Symbol: WideString): WideString; dispid 201;
    procedure CloseRequest; dispid 202;
    procedure OpenRequest(const Symbol: WideString; NumBars: Integer; RequestType: BarIntervalEnum; 
                          BarInterval: Integer; FilterMarketHours: WordBool; MarketOpen: TDateTime; 
                          MarketClose: TDateTime; const Bars: IWealthLabBars3; 
                          const UpdateSink: IWealthLabRTUpdate3); dispid 203;
    function SupportsRequest(RequestType: BarIntervalEnum): WordBool; dispid 204;
    procedure AssignConnectionStatus(const Conn: IWealthLabConnection3); dispid 205;
    function SupportsQuotes: WordBool; dispid 206;
    procedure AddSymbol(const Symbol: WideString; Item: Integer); dispid 207;
    procedure RemoveSymbol(const Symbol: WideString; Item: Integer); dispid 208;
    procedure ClearSymbols; dispid 209;
    procedure ActivateQuotes(const Update: IWealthLabQuoteUpdate3); dispid 210;
    procedure DeactivateQuotes; dispid 211;
  end;

// *********************************************************************//
// Interface: IWealthLabQuoteUpdate3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {A9C56942-D02B-45CC-BEA2-F14D811DBCC3}
// *********************************************************************//
  IWealthLabQuoteUpdate3 = interface(IDispatch)
    ['{A9C56942-D02B-45CC-BEA2-F14D811DBCC3}']
    procedure UpdateQuote(const Symbol: WideString; TimeStamp: TDateTime; Price: Double; 
                          Size: Integer; Open: Double; High: Double; Low: Double; Bid: Double; 
                          Ask: Double; Item: Integer; Change: Double; ChangePct: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabQuoteUpdate3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {A9C56942-D02B-45CC-BEA2-F14D811DBCC3}
// *********************************************************************//
  IWealthLabQuoteUpdate3Disp = dispinterface
    ['{A9C56942-D02B-45CC-BEA2-F14D811DBCC3}']
    procedure UpdateQuote(const Symbol: WideString; TimeStamp: TDateTime; Price: Double; 
                          Size: Integer; Open: Double; High: Double; Low: Double; Bid: Double; 
                          Ask: Double; Item: Integer; Change: Double; ChangePct: Double); dispid 201;
  end;

// *********************************************************************//
// Interface: IWealthLabChart3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {BCA09198-01C8-45C0-99F4-C6DEBB2ED047}
// *********************************************************************//
  IWealthLabChart3 = interface(IDispatch)
    ['{BCA09198-01C8-45C0-99F4-C6DEBB2ED047}']
    function BarCount: Integer; safecall;
    function Date(Bar: Integer): TDateTime; safecall;
    function PriceClose(Bar: Integer): Double; safecall;
    function PriceOpen(Bar: Integer): Double; safecall;
    function PriceHigh(Bar: Integer): Double; safecall;
    function PriceLow(Bar: Integer): Double; safecall;
    function Volume(Bar: Integer): Integer; safecall;
    function BarToX(Bar: Integer): Integer; safecall;
    function PriceToY(Price: Double): Integer; safecall;
    procedure SetBarWidth(Bar: Integer; Width: Integer); safecall;
    function BarSpacing: Integer; safecall;
    function GetBarWidth(Bar: Integer): Integer; safecall;
    function ColorUp: Integer; safecall;
    function ColorDown: Integer; safecall;
    function ColorBackground: Integer; safecall;
    function GetSettingsValue(const ItemName: WideString): WideString; safecall;
    procedure SetSettingsValue(const ItemName: WideString; const Value: WideString); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabChart3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {BCA09198-01C8-45C0-99F4-C6DEBB2ED047}
// *********************************************************************//
  IWealthLabChart3Disp = dispinterface
    ['{BCA09198-01C8-45C0-99F4-C6DEBB2ED047}']
    function BarCount: Integer; dispid 201;
    function Date(Bar: Integer): TDateTime; dispid 202;
    function PriceClose(Bar: Integer): Double; dispid 203;
    function PriceOpen(Bar: Integer): Double; dispid 204;
    function PriceHigh(Bar: Integer): Double; dispid 205;
    function PriceLow(Bar: Integer): Double; dispid 206;
    function Volume(Bar: Integer): Integer; dispid 207;
    function BarToX(Bar: Integer): Integer; dispid 208;
    function PriceToY(Price: Double): Integer; dispid 209;
    procedure SetBarWidth(Bar: Integer; Width: Integer); dispid 210;
    function BarSpacing: Integer; dispid 211;
    function GetBarWidth(Bar: Integer): Integer; dispid 212;
    function ColorUp: Integer; dispid 213;
    function ColorDown: Integer; dispid 214;
    function ColorBackground: Integer; dispid 215;
    function GetSettingsValue(const ItemName: WideString): WideString; dispid 216;
    procedure SetSettingsValue(const ItemName: WideString; const Value: WideString); dispid 217;
  end;

// *********************************************************************//
// Interface: IWealthLabChartStyle3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {B0B7D42A-A099-413E-B3CD-351870AA652F}
// *********************************************************************//
  IWealthLabChartStyle3 = interface(IDispatch)
    ['{B0B7D42A-A099-413E-B3CD-351870AA652F}']
    procedure Initialize(const Chart: IWealthLabChart3); safecall;
    procedure Render(DC: Integer; Bar: Integer; X: Integer; Width: Integer; 
                     const Chart: IWealthLabChart3; FirstBar: WordBool); safecall;
    function HasCustomSettings: WordBool; safecall;
    procedure InvokeCustomSettings(const Chart: IWealthLabChart3); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabChartStyle3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {B0B7D42A-A099-413E-B3CD-351870AA652F}
// *********************************************************************//
  IWealthLabChartStyle3Disp = dispinterface
    ['{B0B7D42A-A099-413E-B3CD-351870AA652F}']
    procedure Initialize(const Chart: IWealthLabChart3); dispid 201;
    procedure Render(DC: Integer; Bar: Integer; X: Integer; Width: Integer; 
                     const Chart: IWealthLabChart3; FirstBar: WordBool); dispid 202;
    function HasCustomSettings: WordBool; dispid 203;
    procedure InvokeCustomSettings(const Chart: IWealthLabChart3); dispid 204;
  end;

// *********************************************************************//
// Interface: IWealthLabConnection3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {7E6B4954-F684-4811-8C27-4CB5B6FD18E4}
// *********************************************************************//
  IWealthLabConnection3 = interface(IDispatch)
    ['{7E6B4954-F684-4811-8C27-4CB5B6FD18E4}']
    procedure Connect; safecall;
    procedure StartRead; safecall;
    procedure EndRead; safecall;
    procedure Disconnect; safecall;
    procedure Warning(ErrorCode: Integer; const Message: WideString); safecall;
    procedure Failure(ErrorCode: Integer; const Message: WideString); safecall;
    procedure Recover(const Message: WideString); safecall;
    function GetDataFolder: WideString; safecall;
    function GetHardwareFingerprint: WideString; safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabConnection3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {7E6B4954-F684-4811-8C27-4CB5B6FD18E4}
// *********************************************************************//
  IWealthLabConnection3Disp = dispinterface
    ['{7E6B4954-F684-4811-8C27-4CB5B6FD18E4}']
    procedure Connect; dispid 201;
    procedure StartRead; dispid 202;
    procedure EndRead; dispid 203;
    procedure Disconnect; dispid 204;
    procedure Warning(ErrorCode: Integer; const Message: WideString); dispid 205;
    procedure Failure(ErrorCode: Integer; const Message: WideString); dispid 206;
    procedure Recover(const Message: WideString); dispid 207;
    function GetDataFolder: WideString; dispid 208;
    function GetHardwareFingerprint: WideString; dispid 209;
  end;

// *********************************************************************//
// Interface: IWealthLabBroker3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {F69866BA-AD3B-4DC0-8CC3-DEFAD5C6F6A4}
// *********************************************************************//
  IWealthLabBroker3 = interface(IDispatch)
    ['{F69866BA-AD3B-4DC0-8CC3-DEFAD5C6F6A4}']
    procedure Login(const Broker: IWealthLabBrokerUpdate3; const Conn: IWealthLabConnection3); safecall;
    function PlaceTrade(Order: AlertTypeEnum; Shares: Integer; const Symbol: WideString; 
                        OrderType: OrderTypeEnum; Price: Double; GTC: WordBool; 
                        SecurityType: SecurityTypeEnum): Integer; safecall;
    procedure CancelTrade(OrderID: Integer); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabBroker3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {F69866BA-AD3B-4DC0-8CC3-DEFAD5C6F6A4}
// *********************************************************************//
  IWealthLabBroker3Disp = dispinterface
    ['{F69866BA-AD3B-4DC0-8CC3-DEFAD5C6F6A4}']
    procedure Login(const Broker: IWealthLabBrokerUpdate3; const Conn: IWealthLabConnection3); dispid 201;
    function PlaceTrade(Order: AlertTypeEnum; Shares: Integer; const Symbol: WideString; 
                        OrderType: OrderTypeEnum; Price: Double; GTC: WordBool; 
                        SecurityType: SecurityTypeEnum): Integer; dispid 202;
    procedure CancelTrade(OrderID: Integer); dispid 203;
  end;

// *********************************************************************//
// Interface: IWealthLabBrokerUpdate3
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {3C215795-D637-4924-8A59-7272E07DBF2A}
// *********************************************************************//
  IWealthLabBrokerUpdate3 = interface(IDispatch)
    ['{3C215795-D637-4924-8A59-7272E07DBF2A}']
    procedure TradeSuccess(OrderID: Integer); safecall;
    procedure TradeFailure(OrderID: Integer; ErrorCode: Integer; const Message: WideString); safecall;
    procedure CancelSuccess(OrderID: Integer; TimeStamp: TDateTime); safecall;
    procedure CancelFailure(OrderID: Integer; ErrorCode: Integer; const Message: WideString); safecall;
    procedure AccountInfo(AccountValue: Double; BuyingPower: Double); safecall;
    procedure TradeFill(OrderID: Integer; TimeStamp: TDateTime; Shares: Integer; Price: Double); safecall;
    procedure AddActiveAlert(OrderID: Integer; const Symbol: WideString; Shares: Integer; 
                             Position: AlertTypeEnum; Order: OrderTypeEnum; Price: Double); safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabBrokerUpdate3Disp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {3C215795-D637-4924-8A59-7272E07DBF2A}
// *********************************************************************//
  IWealthLabBrokerUpdate3Disp = dispinterface
    ['{3C215795-D637-4924-8A59-7272E07DBF2A}']
    procedure TradeSuccess(OrderID: Integer); dispid 204;
    procedure TradeFailure(OrderID: Integer; ErrorCode: Integer; const Message: WideString); dispid 205;
    procedure CancelSuccess(OrderID: Integer; TimeStamp: TDateTime); dispid 206;
    procedure CancelFailure(OrderID: Integer; ErrorCode: Integer; const Message: WideString); dispid 207;
    procedure AccountInfo(AccountValue: Double; BuyingPower: Double); dispid 201;
    procedure TradeFill(OrderID: Integer; TimeStamp: TDateTime; Shares: Integer; Price: Double); dispid 202;
    procedure AddActiveAlert(OrderID: Integer; const Symbol: WideString; Shares: Integer; 
                             Position: AlertTypeEnum; Order: OrderTypeEnum; Price: Double); dispid 203;
  end;

// *********************************************************************//
// Interface: IWealthLabBroker3B
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {56229677-44A0-4BDE-840D-7F10E599F97B}
// *********************************************************************//
  IWealthLabBroker3B = interface(IWealthLabBroker3)
    ['{56229677-44A0-4BDE-840D-7F10E599F97B}']
    function PlaceTradeB(Order: AlertTypeEnum; Shares: Integer; const Symbol: WideString; 
                         OrderType: OrderTypeEnum; Price: Double; GTC: WordBool; 
                         SecurityType: SecurityTypeEnum; Decimals: Integer): Integer; safecall;
  end;

// *********************************************************************//
// DispIntf:  IWealthLabBroker3BDisp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {56229677-44A0-4BDE-840D-7F10E599F97B}
// *********************************************************************//
  IWealthLabBroker3BDisp = dispinterface
    ['{56229677-44A0-4BDE-840D-7F10E599F97B}']
    function PlaceTradeB(Order: AlertTypeEnum; Shares: Integer; const Symbol: WideString; 
                         OrderType: OrderTypeEnum; Price: Double; GTC: WordBool; 
                         SecurityType: SecurityTypeEnum; Decimals: Integer): Integer; dispid 301;
    procedure Login(const Broker: IWealthLabBrokerUpdate3; const Conn: IWealthLabConnection3); dispid 201;
    function PlaceTrade(Order: AlertTypeEnum; Shares: Integer; const Symbol: WideString; 
                        OrderType: OrderTypeEnum; Price: Double; GTC: WordBool; 
                        SecurityType: SecurityTypeEnum): Integer; dispid 202;
    procedure CancelTrade(OrderID: Integer); dispid 203;
  end;

// *********************************************************************//
// The Class CoWL3 provides a Create and CreateRemote method to          
// create instances of the default interface IWL3 exposed by              
// the CoClass WL3. The functions are intended to be used by             
// clients wishing to automate the CoClass objects exposed by the         
// server of this typelibrary.                                            
// *********************************************************************//
  CoWL3 = class
    class function Create: IWL3;
    class function CreateRemote(const MachineName: string): IWL3;
  end;

implementation

uses ComObj;

class function CoWL3.Create: IWL3;
begin
  Result := CreateComObject(CLASS_WL3) as IWL3;
end;

class function CoWL3.CreateRemote(const MachineName: string): IWL3;
begin
  Result := CreateRemoteComObject(MachineName, CLASS_WL3) as IWL3;
end;

end.
