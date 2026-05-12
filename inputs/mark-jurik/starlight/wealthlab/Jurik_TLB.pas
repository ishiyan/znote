unit Jurik_TLB;

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
// Type Lib: C:\Program Files\Borland\Delphi6\Projects\Jurik\Jurik.tlb (1)
// LIBID: {B79D0901-4467-4244-9858-6F5C326126EA}
// LCID: 0
// Helpfile: 
// DepndLst: 
//   (1) v2.0 stdole, (C:\WINDOWS\system32\STDOLE2.TLB)
//   (2) v1.0 WealthLab, (C:\Program Files\Wealth-Lab, Inc\Wealth-Lab Developer 3.0\WealthLab.exe)
//   (3) v4.0 StdVCL, (C:\WINDOWS\system32\stdvcl40.dll)
// ************************************************************************ //
{$TYPEDADDRESS OFF} // Unit must be compiled without type-checked pointers. 
{$WARN SYMBOL_PLATFORM OFF}
{$WRITEABLECONST ON}
{$VARPROPSETTER ON}
interface

uses Windows, ActiveX, Classes, Graphics, StdVCL, Variants, WealthLab_TLB;
  

// *********************************************************************//
// GUIDS declared in the TypeLibrary. Following prefixes are used:        
//   Type Libraries     : LIBID_xxxx                                      
//   CoClasses          : CLASS_xxxx                                      
//   DISPInterfaces     : DIID_xxxx                                       
//   Non-DISP interfaces: IID_xxxx                                        
// *********************************************************************//
const
  // TypeLibrary Major and minor versions
  JurikMajorVersion = 0;
  JurikMinorVersion = 99;

  LIBID_Jurik: TGUID = '{B79D0901-4467-4244-9858-6F5C326126EA}';

  IID_IIndicator: TGUID = '{51F0C65F-5CF8-4322-BA4F-38A4628996F0}';
  CLASS_Indicator: TGUID = '{A39D9087-1EF4-4592-97E8-20490BE56200}';
type

// *********************************************************************//
// Forward declaration of types defined in TypeLibrary                    
// *********************************************************************//
  IIndicator = interface;
  IIndicatorDisp = dispinterface;

// *********************************************************************//
// Declaration of CoClasses defined in Type Library                       
// (NOTE: Here we map each CoClass to its Default Interface)              
// *********************************************************************//
  Indicator = IIndicator;


// *********************************************************************//
// Interface: IIndicator
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {51F0C65F-5CF8-4322-BA4F-38A4628996F0}
// *********************************************************************//
  IIndicator = interface(IDispatch)
    ['{51F0C65F-5CF8-4322-BA4F-38A4628996F0}']
    procedure JJMA(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; APhase: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JCFB(ADestSeries: Integer; ASourceSeries: Integer; AFractalType: Integer; 
                   ASmooth: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JCCX(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JTPO(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JARSX(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; AHiLen: Integer; 
                    ASensitivity: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JRSX(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JDMX(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXP(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                    const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXM(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                    const AWL: IWealthLabAddOn3); safecall;
    procedure JAVEL(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; AHiLen: Integer; 
                    ASensitivity: Integer; APeriod: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JVEL(ADestSeries: Integer; ASourceSeries: Integer; ADepth: Integer; 
                   const AWL: IWealthLabAddOn3); safecall;
    procedure JVELCFB(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; 
                      AHiLen: Integer; AFractalType: Integer; ASmooth: Integer; 
                      const AWL: IWealthLabAddOn3); safecall;
  end;

// *********************************************************************//
// DispIntf:  IIndicatorDisp
// Flags:     (4416) Dual OleAutomation Dispatchable
// GUID:      {51F0C65F-5CF8-4322-BA4F-38A4628996F0}
// *********************************************************************//
  IIndicatorDisp = dispinterface
    ['{51F0C65F-5CF8-4322-BA4F-38A4628996F0}']
    procedure JJMA(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; APhase: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 1;
    procedure JCFB(ADestSeries: Integer; ASourceSeries: Integer; AFractalType: Integer; 
                   ASmooth: Integer; const AWL: IWealthLabAddOn3); dispid 2;
    procedure JCCX(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 3;
    procedure JTPO(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 4;
    procedure JARSX(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; AHiLen: Integer; 
                    ASensitivity: Integer; const AWL: IWealthLabAddOn3); dispid 5;
    procedure JRSX(ADestSeries: Integer; ASourceSeries: Integer; ALength: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 6;
    procedure JDMX(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 7;
    procedure JDMXP(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                    const AWL: IWealthLabAddOn3); dispid 8;
    procedure JDMXM(ADestSeries: Integer; ASourceSeries: Integer; ALen: Integer; 
                    const AWL: IWealthLabAddOn3); dispid 9;
    procedure JAVEL(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; AHiLen: Integer; 
                    ASensitivity: Integer; APeriod: Integer; const AWL: IWealthLabAddOn3); dispid 10;
    procedure JVEL(ADestSeries: Integer; ASourceSeries: Integer; ADepth: Integer; 
                   const AWL: IWealthLabAddOn3); dispid 11;
    procedure JVELCFB(ADestSeries: Integer; ASourceSeries: Integer; ALoLen: Integer; 
                      AHiLen: Integer; AFractalType: Integer; ASmooth: Integer; 
                      const AWL: IWealthLabAddOn3); dispid 12;
  end;

// *********************************************************************//
// The Class CoIndicator provides a Create and CreateRemote method to          
// create instances of the default interface IIndicator exposed by              
// the CoClass Indicator. The functions are intended to be used by             
// clients wishing to automate the CoClass objects exposed by the         
// server of this typelibrary.                                            
// *********************************************************************//
  CoIndicator = class
    class function Create: IIndicator;
    class function CreateRemote(const MachineName: string): IIndicator;
  end;

implementation

uses ComObj;

class function CoIndicator.Create: IIndicator;
begin
  Result := CreateComObject(CLASS_Indicator) as IIndicator;
end;

class function CoIndicator.CreateRemote(const MachineName: string): IIndicator;
begin
  Result := CreateRemoteComObject(MachineName, CLASS_Indicator) as IIndicator;
end;

end.
