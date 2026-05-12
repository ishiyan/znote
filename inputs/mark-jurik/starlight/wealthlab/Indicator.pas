unit Indicator;
{  Декомпиляция индикаторов от M.Jurik                   }
{  Created by Starlight (extesy@yandex.ru)               }
{  Адаптация для WealthLab: _landy (email: _al@bk.ru)    }

{$WARN SYMBOL_PLATFORM OFF}

interface

uses
  ComObj, ActiveX, Jurik_TLB, WealthLab_TLB, StdVcl, Calc;

type
  TIndicator = class(TAutoObject, IIndicator)
  protected
    procedure JJMA(ADestSeries, ASourceSeries, ALength, APhase: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JCFB(ADestSeries, ASourceSeries, AFractalType, ASmooth: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JCCX(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JARSX(ADestSeries, ASourceSeries, ALoLen, AHiLen,
      ASensitivity: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JTPO(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JRSX(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMX(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXM(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXP(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JAVEL(ADestSeries, ASourceSeries, ALoLen, AHiLen, ASensitivity,
      APeriod: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JVEL(ADestSeries, ASourceSeries, ADepth: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JVELCFB(ADestSeries, ASourceSeries, ALoLen, AHiLen, AFractalType,
      ASmooth: Integer; const AWL: IWealthLabAddOn3); safecall;
  end;

implementation

uses ComServ;

procedure TIndicator.JJMA(ADestSeries, ASourceSeries, ALength,
  APhase: Integer; const AWL: IWealthLabAddOn3);
var
  SrcA, DestA: TSeries;
  Bar: Integer;
begin
  SetLength (SrcA, AWL.BarCount);

   // Сохраняем данные в локальной памяти
  for Bar := 0 to AWL.BarCount - 1 do
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);

   // Вычисляем по ним индикатор
  DestA := JJMASeries (SrcA, ALength, APhase);

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JCFB(ADestSeries, ASourceSeries, AFractalType,
  ASmooth: Integer; const AWL: IWealthLabAddOn3);
var
  SrcA, DestA: TSeries;
  Bar: Integer;
begin
  SetLength (SrcA, AWL.BarCount);

   // Сохраняем данные в локальной памяти
  for Bar := 0 to AWL.BarCount - 1 do
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);

   // Вычисляем по ним индикатор
  DestA := JCFBSeries (SrcA, AFractalType, ASmooth);

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JCCX(ADestSeries, ASourceSeries, ALength: Integer;
  const AWL: IWealthLabAddOn3);
var
  Bar: integer;
  Value: Double;
  SrcA, DestA, j4A, jLA: TSeries;
  k, abars, ser, diff: integer;
  md: Double;
begin
  SetLength (SrcA, AWL.BarCount);
  SetLength (DestA, AWL.BarCount);

   // Сохраняем данные в локальной памяти (для повышения быстродействия и гибкости)
  for Bar := 0 to AWL.BarCount - 1 do
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);

  k := 0; abars := 0; ser := 0; diff := 0; md := 0;

   // diff := SubtractSeries(JJMASeries(Series, 4, 0), JJMASeries(Series, Len, 0));
  J4A := JJMASeries (SrcA, 4, 0);
  JLA := JJMASeries (SrcA, ALength, 0);
  for Bar := 0 to AWL.BarCount - 1 do
    j4A[Bar] := j4A[Bar] - jLA[Bar];

  for Bar := 1 to High (SrcA) do begin
    if (Bar < 3*ALength) then abars := Bar else abars := 3*ALength;
    md := 0;
    for k := 0 to abars-1 do
      md := md + abs(j4A[Bar-k]);
    md := md * 1.5 / abars;
    if (md > 0.00001) then Value := j4A[Bar] / md else Value := 0;
    DestA[Bar] := Value;
  end;

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JARSX(ADestSeries, ASourceSeries, ALoLen, AHiLen,
  ASensitivity: Integer; const AWL: IWealthLabAddOn3);
var
  Bar, j, k: integer;
  sName: string;
  avg1, avg2, value2, value3, eps: Double;
  SrcA, DestA, Int1A, Int2A: TSeries;
begin
  j := 0; k := 0;
  avg1 := 0; avg2 := 0; value2 := 0; value3 := 0;

  SetLength (SrcA, AWL.BarCount);
  SetLength (DestA, AWL.BarCount);
  SetLength (Int1A, AWL.BarCount);
  SetLength (Int2A, AWL.BarCount);

   // Сохраняем данные в локальной памяти (для повышения быстродействия и гибкости)
  for Bar := 0 to AWL.BarCount - 1 do
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);

  eps := 0.001;

  for Bar := 1 to High(SrcA) do
     Int1A[Bar] := abs(SrcA[Bar] - SrcA[Bar-1]);

  for Bar := 0 to High(SrcA) do begin
    avg1 := 0;
    if (Bar < 99) then k := Bar else k := 99;
    for j := 0 to k do
       avg1 := avg1 + Int1A[Bar-j];
    avg1 := avg1 / (k+1);

    avg2 := 0;
    if (Bar < 9) then k := Bar else k := 9;
    for j := 0 to k do
       avg2 := avg2 + Int1A[Bar-j];
    avg2 := avg2 / (k+1);

    value2 := ASensitivity * ln((eps+avg1) / (eps+avg2));
    value3 := value2 / (1 + abs(value2));
    Int2A[Bar] := ALoLen + (AHiLen-ALoLen) * (1+value3) / 2;
  end;

  DestA := JXRSXSeries (SrcA, Int2A);   //  for Bar .. do @Result[Bar] := JXRSX(Bar, Series, Int2A);

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JTPO(ADestSeries, ASourceSeries, ALength: Integer;
  const AWL: IWealthLabAddOn3);
var
  Bar, J: integer;
  Value: double;
  f0, f8, f10, f18, f20, f28: double;
  f30, f38, f40, f48: integer;
  var6, varA, varE, var12, var14: integer;
  var18, var1C, var20, var24: double;
  arr0, arr1, arr2, arr3: array[0..300] of double;
begin
   // Обнуляем все внутренние переменные (WealthLab делает это автоматом)
  f0 := 0; f8 := 0; f10 := 0; f18 := 0; f20 := 0; f28 := 0;
  f30 := 0; f38 := 0; f40 := 0; f48 := 0;
  var6 := 0; varA := 0; varE := 0; var12 := 0; var14 :=0;
  var18 := 0; var1C := 0; var20 := 0; var24 := 0;

  for J := 0 to 300 do begin
    arr0[J] := 0;
    arr1[J] := 0;
    arr2[J] := 0;
    arr3[J] := 0;
  end;

  for Bar := 0 to AWL.BarCount - 1 do begin
   var14 := 0;
   var1C := 0;
   if (f38 = 0) then begin
      f38 := 1;
      f40 := 0;
      if (ALength-1 >= 2) then f30 := ALength-1 else f30 := 2;
      f48 := f30 + 1;
      f10 := AWL.GetSeriesValue(Bar, ASourceSeries);
      arr0[f38] := AWL.GetSeriesValue(Bar, ASourceSeries);
      f18 := 12 / (f48 * (f48 - 1) * (f48 + 1));
      f20 := (f48 + 1) * 0.5;
   end else begin
     if (f38 <= f48) then f38 := f38 + 1 else f38 := f48 + 1;
     f8 := f10;
     f10 := AWL.GetSeriesValue(Bar, ASourceSeries);
     if (f38 > f48) then begin
        for var6 := 2 to f48 do
           arr0[var6 - 1] := arr0[var6];
        arr0[f48] := AWL.GetSeriesValue(Bar, ASourceSeries);
     end else
        arr0[f38] := AWL.GetSeriesValue(Bar, ASourceSeries);
     if ((f30 >= f38) and (f8 <> f10)) then f40 := 1;
     if ((f30 = f38) and (f40 = 0)) then f38 := 0;
   end;
   if (f38 >= f48) then begin
      for varA := 1 to f48 do begin
         arr2[varA] := varA;
         arr3[varA] := varA;
         arr1[varA] := arr0[varA];
      end;
      for varA := 1 to f48-1 do begin
         var24 := arr1[varA];
         var12 := varA;
         var6 := varA + 1;
         for var6 := varA + 1 to f48 do
            if (arr1[var6] < var24) then begin
               var24 := arr1[var6];
               var12 := var6;
            end;
         var20 := arr1[varA];
         arr1[varA] := arr1[var12];
         arr1[var12] := var20;
         var20 := arr2[varA];
         arr2[varA] := arr2[var12];
         arr2[var12] := var20;
      end;
      varA := 1;
      while (f48 > varA) do begin
         var6 := varA + 1;
         var14 := 1;
         var1C := arr3[varA];
         while (var14 <> 0) do begin
            if (arr1[varA] <> arr1[var6]) then begin
               if (var6 - varA > 1) then begin
                  var1C := var1C / (var6 - varA);
                  varE := varA;
                  for varE := varA to var6-1 do
                     arr3[varE] := var1C;
               end;
               var14 := 0;
            end else begin
               var1C := var1C + arr3[var6];
               var6 := var6 + 1;
            end;
         end;
         varA := var6;
      end;
      var1C := 0;
      for varA := 1 to f48 do
         var1C := var1C + (arr3[varA] - f20) * (arr2[varA] - f20);
      var18 := f18 * var1C;
   end else
      var18 := 0;

    Value := var18;
    AWL.SetSeriesValue(Bar, ADestSeries, Value);
  end;
end;

procedure TIndicator.JRSX(ADestSeries, ASourceSeries, ALength: Integer;
  const AWL: IWealthLabAddOn3);
var
  Bar: integer;
  sName: string;
  Value: Double;
  f0, f88, f90: integer;
  f8, f10, f18, f20, f28, f30, f38, f40, f48, f50, f58, f60, f68, f70, f78, f80: Double;
  v4, v8, vC, v10, v14, v18, v1C, v20: Double;
begin
  f0 := 0; f88 := 0; f90 := 0;
  f8 := 0; f10 := 0; f18 := 0; f20 := 0; f28 := 0; f30 := 0; f38 := 0; f40 := 0;
  f48 := 0; f50 := 0; f58 := 0; f60 := 0; f68 := 0; f70 := 0; f78 := 0; f80 := 0;
  v4 := 0; v8 := 0; vC := 0; v10 := 0; v14 := 0; v18 := 0; v1C := 0; v20 := 0;

  for Bar := 0 to AWL.BarCount - 1 do
  begin
    if (f90 = 0) then begin
      f90 := 1;
      f0 := 0;
      if (ALength-1 >= 5) then f88 := ALength-1 else f88 := 5;
      f8 := 100*AWL.GetSeriesValue(Bar, ASourceSeries);
      f18 := 3 / (ALength + 2);
      f20 := 1 - f18;
    end else begin
      if (f88 <= f90) then f90 := f88 + 1 else f90 := f90 + 1;
      f10 := f8;
      f8 := 100*AWL.GetSeriesValue(Bar, ASourceSeries);
      v8 := f8 - f10;
      f28 := f20 * f28 + f18 * v8;
      f30 := f18 * f28 + f20 * f30;
      vC := f28 * 1.5 - f30 * 0.5;
      f38 := f20 * f38 + f18 * vC;
      f40 := f18 * f38 + f20 * f40;
      v10 := f38 * 1.5 - f40 * 0.5;
      f48 := f20 * f48 + f18 * v10;
      f50 := f18 * f48 + f20 * f50;
      v14 := f48 * 1.5 - f50 * 0.5;
      f58 := f20 * f58 + f18 * abs(v8);
      f60 := f18 * f58 + f20 * f60;
      v18 := f58 * 1.5 - f60 * 0.5;
      f68 := f20 * f68 + f18 * v18;
      f70 := f18 * f68 + f20 * f70;
      v1C := f68 * 1.5 - f70 * 0.5;
      f78 := f20 * f78 + f18 * v1C;
      f80 := f18 * f78 + f20 * f80;
      v20 := f78 * 1.5 - f80 * 0.5;
      if ((f88 >= f90) and (f8 <> f10)) then f0 := 1;
      if ((f88 = f90) and (f0 = 0)) then f90 := 0;
    end;
    if ((f88 < f90) and (v20 > 1.0e-10)) then begin
      v4 := (v14 / v20 + 1) * 50;
      if (v4 > 100) then v4 := 100;
      if (v4 < 0) then v4 := 0;
    end else
      v4 := 50;
    Value := v4;
    AWL.SetSeriesValue(Bar, ADestSeries, Value);
  end;
end;

procedure TIndicator.JDMX(ADestSeries, ASourceSeries, ALen: Integer;
  const AWL: IWealthLabAddOn3);
var
  SrcA, DestA, LowA, HighA: TSeries;
  Bar: Integer;
begin
  SetLength (SrcA, AWL.BarCount);
  SetLength (HighA, AWL.BarCount);
  SetLength (LowA, AWL.BarCount);

   // Сохраняем данные в локальной памяти
  for Bar := 0 to AWL.BarCount - 1 do begin
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);
    HighA[Bar] := AWL.PriceHigh(Bar);
    LowA[Bar] := AWL.PriceLow(Bar);
  end;

   // Вычисляем по ним индикатор
  DestA := JDMXSeries (SrcA, HighA, LowA, ALen);

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JDMXM(ADestSeries, ASourceSeries, ALen: Integer;
  const AWL: IWealthLabAddOn3);
var
  SrcA, DestA, LowA, HighA: TSeries;
  Bar: Integer;
begin
  SetLength (SrcA, AWL.BarCount);
  SetLength (HighA, AWL.BarCount);
  SetLength (LowA, AWL.BarCount);

   // Сохраняем данные в локальной памяти
  for Bar := 0 to AWL.BarCount - 1 do begin
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);
    HighA[Bar] := AWL.PriceHigh(Bar);
    LowA[Bar] := AWL.PriceLow(Bar);
  end;

   // Вычисляем по ним индикатор
  DestA := JDMXMinusSeries (SrcA, HighA, LowA, ALen);

   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

procedure TIndicator.JDMXP(ADestSeries, ASourceSeries, ALen: Integer;
  const AWL: IWealthLabAddOn3);
var
  SrcA, DestA, LowA, HighA: TSeries;
  Bar: Integer;
begin
  SetLength (SrcA, AWL.BarCount);
  SetLength (HighA, AWL.BarCount);
  SetLength (LowA, AWL.BarCount);

   // Сохраняем данные в локальной памяти
  for Bar := 0 to AWL.BarCount - 1 do begin
    SrcA[Bar] := AWL.GetSeriesValue(Bar, ASourceSeries);
    HighA[Bar] := AWL.PriceHigh(Bar);
    LowA[Bar] := AWL.PriceLow(Bar);
  end;

   // Вычисляем по ним индикатор
  DestA := JDMXPlusSeries (SrcA, HighA, LowA, ALen);

   // Возвращаем результаты обратно в WealthLab
  for Bar := 0 to AWL.BarCount - 1 do
    AWL.SetSeriesValue(Bar, ADestSeries, DestA[Bar]);
end;

function GetSeries (ASrcIdx: Integer; const AWL: IWealthLabAddOn3): TSeries;
var
  Bar: Integer;
begin
    // Проверяем на наличие данных в кэше
  { .. }

    // Если не нашли, копируем из WealthLab
  SetLength (Result, AWL.BarCount);
  for Bar := 0 to AWL.BarCount - 1 do
    Result[Bar] := AWL.GetSeriesValue(Bar, ASrcIdx);
end;

procedure PutSeries (const DestA: TSeries; ADestIdx: Integer; const AWL: IWealthLabAddOn3);
var
  Bar: Integer;
begin
   // Возвращаем результаты обрано в WealthLab
  for Bar := 0 to High (DestA) do
    AWL.SetSeriesValue(Bar, ADestIdx, DestA[Bar]);
end;

procedure TIndicator.JAVEL(ADestSeries, ASourceSeries, ALoLen, AHiLen,
  ASensitivity, APeriod: Integer; const AWL: IWealthLabAddOn3);
begin
  PutSeries (JAVELSeries (GetSeries (ASourceSeries, AWL),
    ALoLen, AHiLen, ASensitivity, APeriod), ADestSeries, AWL);
end;

procedure TIndicator.JVEL(ADestSeries, ASourceSeries, ADepth: Integer;
  const AWL: IWealthLabAddOn3);
begin
   // Получаем данные, вычисляем индикатор, возвращаем результаты обрано в WealthLab
  PutSeries (JVELSeries(GetSeries(ASourceSeries, AWL), ADepth), ADestSeries, AWL);
end;

procedure TIndicator.JVELCFB(ADestSeries, ASourceSeries, ALoLen, AHiLen,
  AFractalType, ASmooth: Integer; const AWL: IWealthLabAddOn3);
begin
  PutSeries (JVELCFBSeries(GetSeries(ASourceSeries, AWL), ALoLen, AHiLen, AFractalType, ASmooth), ADestSeries, AWL);
end;

initialization
  TAutoObjectFactory.Create(ComServer, TIndicator, Class_Indicator,
    ciMultiInstance, tmApartment);
end.
