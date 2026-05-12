unit Calc;
{  Декомпиляция индикаторов от M.Jurik          }
{  Created by Starlight (extesy@yandex.ru)      }

interface
uses
  Math;

type
  TSeries = array of Double;            // Серия данных

function JJMASeries (const SrcA: TSeries; ALength, APhase: Integer): TSeries;

function JCFBSeries (const SrcA: TSeries; AFractalType: Integer; ASmooth: Integer): TSeries;
function JVELCFBSeries(SrcA: TSeries; ALoDepth, AHiDepth, AFractalType, ASmooth: integer): TSeries;

function JXRSXSeries (const SrcA, LenA: TSeries): TSeries;

function JAVELSeries (const SrcA: TSeries; ALoLen, AHiLen: Integer; ASensitivity, APeriod: Double): TSeries;
function JXVELSeries (const SrcA: TSeries; DepthSrcA: TSeries; APeriod: Double): TSeries;
function JVELSeries (const SrcA: TSeries; ADepth: integer): TSeries;

function JDMXminusSeries (const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;
function JDMXplusSeries (const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;
function JDMXSeries (const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;

implementation

function JJMASeries(const SrcA: TSeries; ALength, APhase: Integer): TSeries;
var
  Bar, k: integer;
  Value: Double;
  v, v1, v2, v3, v4, s8, s10, s18, s20: Double;
  i, v5, v6, s28, s30, s38, s40, s48, s50, s58, s60, s68, s70: integer;
  f8, f10, f18, f20, f28, f30, f38, f40, f48, f50, f58, f60, f68, f70, f78, f80,
    f88, f90, f98, fA0, fA8, fB0, fB8, fC0, fC8, fD0: Double;
  f0, fD8, fE0, fE8, fF0, fF8: integer;
  list: array[0..127] of Double;
  ring: array[0..127] of Double;
  ring2: array[0..10] of Double;
  buffer: array[0..61] of Double;

begin
  SetLength (Result, High (SrcA) + 1);

   // Обнуление всех внутренних переменных
  v := 0; v1 := 0; v2 := 0; v3 := 0; v4 := 0; s8 := 0; s10 := 0; s18 := 0;
  s20 := 0; i := 0; v5 := 0; v6 := 0; s28 := 0; s30 := 0; s38 := 0; s40 := 0;
  s48 := 0; s50 := 0; s58 := 0; s60 := 0; s68 := 0; s70 := 0; f8 := 0;
  f10 := 0; f18 := 0; f20 := 0; f28 := 0; f30 := 0; f38 := 0; f40 := 0;
  f48 := 0; f50 := 0; f58 := 0; f60 := 0; f68 := 0; f70 := 0; f78 := 0;
  f80 := 0; f88 := 0; f90 := 0; f98 := 0; fA0 := 0; fA8 := 0; fB0 := 0;
  fB8 := 0; fC0 := 0; fC8 := 0; fD0 := 0; f0 := 0; fD8 := 0; fE0 := 0;
  fE8 := 0; fF0 := 0; fF8 := 0;

  FillChar (list,SizeOf(list), 0);
  FillChar (ring,SizeOf(ring), 0);
  FillChar (ring2,SizeOf(ring2), 0);
  FillChar (buffer,SizeOf(buffer), 0);

  s28 := 63;
  s30 := 64;
  for i := 1 to s28 do list[i] := -1000000;
  for i := s30 to 127 do list[i] := 1000000;
  f0 := 1;

  if (ALength <= 1) then
    f80 := 1.0E-10
  else
    f80 := (ALength - 1) / 2;
  if (APhase < -100) then
    f10 := 0.5
  else if (APhase > 100) then
    f10 := 2.5
  else
    f10 := APhase / 100 + 1.5;

  v1 := ln(sqrt(f80));
  v2 := v1;
  if (v1 / ln(2.0) + 2 < 0) then
    v3 := 0
  else
    v3 := v2 / ln(2.0) + 2;
  f98 := v3;

  if (0.5 <= f98 - 2) then
    f88 := f98 - 2
  else
    f88 := 0.5;
  f78 := sqrt(f80) * f98;
  f90 := f78 / (f78 + 1);
  f80 := f80 * 0.9;
  f50 := f80 / (f80 + 2);

  for Bar := 0 to High (SrcA) do begin
    if (fF0 < 61) then begin
      fF0 := fF0 + 1;
      buffer[fF0] := SrcA[Bar];
    end;
    if (fF0 > 30) then begin
      if (f0 <> 0) then begin
        f0 := 0;
        v5 := 0;
        for i := 1 to 29 do
          if (buffer[i + 1] <> buffer[i]) then v5 := 1;
        fD8 := v5 * 30;
        if (fD8 = 0) then f38 := SrcA[Bar] else f38 := buffer[1];
        f18 := f38;
        if (fD8 > 29) then fD8 := 29;
      end
      else
        fD8 := 0;

      for i := fD8 downto 0 do begin
        if (i = 0) then
          f8 := SrcA[Bar]
        else
          f8 := buffer[31 - i];
        f28 := f8 - f18;
        f48 := f8 - f38;
        if (abs(f28) > abs(f48)) then v2 := abs(f28) else v2 := abs(f48);
        fA0 := v2;
        v := fA0 + 1.0E-10;

        if (s48 <= 1) then s48 := 127 else s48 := s48 - 1;
        if (s50 <= 1) then s50 := 10 else s50 := s50 - 1;
        if (s70 < 128) then s70 := s70 + 1;
        s8 := s8 + v - ring2[s50];
        ring2[s50] := v;
        if (s70 > 10) then s20 := s8 / 10 else s20 := s8 / s70;

        if (s70 > 127) then begin
          s10 := ring[s48];
          ring[s48] := s20;
          s68 := 64;
          s58 := s68;
          while (s68 > 1) do begin
            if (list[s58] < s10) then begin
              s68 := s68 div 2;
              s58 := s58 + s68;
            end
            else if (list[s58] <= s10) then begin
              s68 := 1;
            end
            else begin
              s68 := s68 div 2;
              s58 := s58 - s68;
            end
          end
        end
        else begin
          ring[s48] := s20;

          if (s28 + s30 > 127) then begin
            s30 := s30 - 1;
            s58 := s30;
          end
          else begin
            s28 := s28 + 1;
            s58 := s28;
          end;
          if (s28 > 96) then
            s38 := 96
          else
            s38 := s28;
          if (s30 < 32) then
            s40 := 32
          else
            s40 := s30;
        end;
        s68 := 64;
        s60 := s68;
        while (s68 > 1) do begin
          if (list[s60] >= s20) then begin
            if (list[s60 - 1] <= s20) then begin
              s68 := 1;
            end
            else begin
              s68 := s68 div 2;
              s60 := s60 - s68;
            end
          end
          else begin
            s68 := s68 div 2;
            s60 := s60 + s68;
          end;
          if ((s60 = 127) and (s20 > list[127])) then
            s60 := 128;
        end;
        if (s70 > 127) then begin
          if (s58 >= s60) then begin
            if ((s38 + 1 > s60) and (s40 - 1 < s60)) then
              s18 := s18 + s20
            else if ((s40 > s60) and (s40 - 1 < s58)) then
              s18 := s18 + list[s40 - 1];
          end
          else if (s40 >= s60) then begin
            if ((s38 + 1 < s60) and (s38 + 1 > s58)) then
              s18 := s18 + list[s38 + 1];
          end
          else if (s38 + 2 > s60) then
            s18 := s18 + s20
          else if ((s38 + 1 < s60) and (s38 + 1 > s58)) then
            s18 := s18 + list[s38 + 1];

          if (s58 > s60) then begin
            if ((s40 - 1 < s58) and (s38 + 1 > s58)) then
              s18 := s18 - list[s58]
            else if ((s38 < s58) and (s38 + 1 > s60)) then
              s18 := s18 - list[s38];
          end
          else begin
            if ((s38 + 1 > s58) and (s40 - 1 < s58)) then
              s18 := s18 - list[s58]
            else if ((s40 > s58) and (s40 < s60)) then
              s18 := s18 - list[s40];
          end
        end;

        if (s58 <= s60) then begin
          if (s58 >= s60) then
            list[s60] := s20
          else begin
            for k := s58 + 1 to s60 - 1 do
              list[k - 1] := list[k];
            list[s60 - 1] := s20;
          end
        end
        else begin
          for k := s58 - 1 downto s60 do
            list[k + 1] := list[k];
          list[s60] := s20;
        end;

        if (s70 <= 127) then begin
          s18 := 0;
          for k := s40 to s38 do
            s18 := s18 + list[k];
        end;

        f60 := s18 / (s38 - s40 + 1);

        if (fF8 + 1 > 31) then
          fF8 := 31
        else
          fF8 := fF8 + 1;
        if (fF8 <= 30) then begin
          if (f28 > 0) then f18 := f8 else f18 := f8 - f28 * f90;
          if (f48 < 0) then f38 := f8 else f38 := f8 - f48 * f90;
          fB8 := SrcA[Bar];
          if (fF8 <> 30) then
            continue;
          fC0 := SrcA[Bar];

          if (ceil(f78) >= 1) then v4 := ceil(f78) else v4 := 1;
          fE8 := Trunc(v4);
          if (floor(f78) >= 1) then v2 := floor(f78) else v2 := 1;
          fE0 := Trunc(v2);
          if (fE8 = fE0) then
            f68 := 1
          else begin
            v4 := fE8 - fE0;
            f68 := (f78 - fE0) / v4;
          end;
          if (fE0 <= 29) then v5 := fE0 else v5 := 29;
          if (fE8 <= 29) then v6 := fE8 else v6 := 29;
          fA8 := (SrcA[Bar] - buffer[fF0 - v5]) * (1 - f68) / fE0 +
            (SrcA[Bar] - buffer[fF0 - v6]) * f68 / fE8;
        end
        else begin
          if (f98 >= power(fA0 / f60, f88)) then
            v1 := power(fA0 / f60, f88)
          else
            v1 := f98;
          if (v1 < 1) then
            v2 := 1.0
          else begin
            if (f98 >= power(fA0 / f60, f88))
              then v3 := power(fA0 / f60, f88)
              else v3 := f98;
            v2 := v3;
          end;
          f58 := v2;
          f70 := power(f90, sqrt(f58));
          if (f28 > 0) then f18 := f8 else f18 := f8 - f28 * f70;
          if (f48 < 0) then f38 := f8 else f38 := f8 - f48 * f70;
        end;
      end;

      if (fF8 > 30) then begin
        f30 := power(f50, f58);
        fC0 := (1 - f30) * SrcA[Bar] + f30 * fC0;
        fC8 := (SrcA[Bar] - fC0) * (1 - f50) + f50 * fC8;
        fD0 := f10 * fC8 + fC0;
        f20 := f30 * -2;
        f40 := f30 * f30;
        fB0 := f20 + f40 + 1;
        fA8 := (fD0 - fB8) * fB0 + f40 * fA8;
        fB8 := fB8 + fA8;
      end;
    end;

    Value := fB8;
    Result[Bar] := Value;
  end;
end;

function JCFBaux(SrcA: TSeries; Depth: Integer): TSeries;
var
  Bar: integer;
  Value: Double;
  jrc04, jrc05, jrc06, jrc08: Double;
  jrc07: integer;
  IntA: TSeries;
begin
  SetLength (Result, High(SrcA) + 1);
  jrc04 := 0; jrc05 := 0;
  jrc06 := 0; jrc08 := 0;
  jrc07 := 0;

  SetLength (IntA, High(SrcA) + 1);
  for Bar := 1 to High (SrcA) do
    IntA[Bar] := abs(SrcA[Bar] - SrcA[Bar-1]);

  for Bar := Depth to High (SrcA) - 1 do begin
    if Bar <= Depth*2 then begin
      jrc04 := 0;
      jrc05 := 0;
      jrc06 := 0;
      for jrc07 := 0 to Depth-1 do begin
        jrc04 := jrc04 + abs(SrcA[Bar-jrc07] - SrcA[Bar-jrc07-1]);
        jrc05 := jrc05 + (Depth - jrc07) * abs(SrcA[Bar-jrc07] - SrcA[Bar-jrc07-1]);
        jrc06 := jrc06 + SrcA[Bar-jrc07-1];
      end
    end else begin
      jrc05 := jrc05 - jrc04 + IntA[Bar] * Depth;
      jrc04 := jrc04 - IntA[Bar-Depth] + IntA[Bar];
      jrc06 := jrc06 - SrcA[Bar-Depth-1] + SrcA[Bar-1];
    end;
    jrc08 := abs(Depth * SrcA[Bar] - jrc06);
    if (jrc05 = 0) then Value := 0 else Value := jrc08 / jrc05;
    Result[Bar] := Value;
  end;
end;

function JCFB24(SrcA: TSeries; Smooth: Integer): TSeries;
var
  Bar: integer;
  Value: Double;
  er1, er2, er3, er4, er5, er6, er7, er8: TSeries;
  er20, er21, er29: integer;
  er15, er16, er17, er18, er19: Double;
  er22, er23: array[1..8] of Double;
begin
  SetLength (Result, High(SrcA) + 1);
  er20 := 0; er21 := 0; er29 := 0; er15 := 0; er16 := 0; er17 := 0; er18 := 0;
  er19 := 0;
  FillChar (er22, sizeof(er22), 0);
  FillChar (er23, sizeof(er23), 0);

  er15 := 1;
  er16 := 1;
  er19 := 20;
  er29 := Smooth;

  er1 := JCFBaux (SrcA, 2);     //  er1 := JCFBaux(Series, 2);
  er2 := JCFBaux (SrcA, 3);     //  JCFBaux(Series, 3);
  er3 := JCFBaux (SrcA, 4);     //  JCFBaux(Series, 4);
  er4 := JCFBaux (SrcA, 6);     //  JCFBaux(Series, 6);
  er5 := JCFBaux (SrcA, 8);     //  JCFBaux(Series, 8);
  er6 := JCFBaux (SrcA, 12);    //  JCFBaux(Series, 12);
  er7 := JCFBaux (SrcA, 16);    //  JCFBaux(Series, 16);
  er8 := JCFBaux (SrcA, 24);    //  JCFBaux(Series, 24);

  for Bar := 1 to High (SrcA) do begin
    if (Bar <= er29) then begin
      for er21 := 1 to 8 do
        er23[er21] := 0;
    	for er20 := 0 to Bar-1 do begin
    	  er23[1] := er23[1] + er1[Bar-er20];
          er23[2] := er23[2] + er2[Bar-er20];
    	  er23[3] := er23[3] + er3[Bar-er20];
          er23[4] := er23[4] + er4[Bar-er20];
    	  er23[5] := er23[5] + er5[Bar-er20];
          er23[6] := er23[6] + er6[Bar-er20];
	  er23[7] := er23[7] + er7[Bar-er20];
          er23[8] := er23[8] + er8[Bar-er20];
    	end;
    	for er21 := 1 to 8 do
    	  er23[er21] := er23[er21] / Bar;
    end else begin
    	er23[1] := er23[1] + (er1[Bar] - er1[Bar-er29]) / er29;
        er23[2] := er23[2] + (er2[Bar] - er2[Bar-er29]) / er29;
    	er23[3] := er23[3] + (er3[Bar] - er3[Bar-er29]) / er29;
        er23[4] := er23[4] + (er4[Bar] - er4[Bar-er29]) / er29;
    	er23[5] := er23[5] + (er5[Bar] - er5[Bar-er29]) / er29;
        er23[6] := er23[6] + (er6[Bar] - er6[Bar-er29]) / er29;
    	er23[7] := er23[7] + (er7[Bar] - er7[Bar-er29]) / er29;
      er23[8] := er23[8] + (er8[Bar] - er8[Bar-er29]) / er29;
    end;
    if Bar > 5 then begin
    	er15 := 1;
    	er22[8] := er15 * er23[8];
        er15 := er15 * (1 - er22[8]);
    	er22[6] := er15 * er23[6];
        er15 := er15 * (1 - er22[6]);
    	er22[4] := er15 * er23[4];
        er15 := er15 * (1 - er22[4]);
    	er22[2] := er15 * er23[2];
    	er16 := 1;
    	er22[7] := er16 * er23[7];
        er16 := er16 * (1 - er22[7]);
    	er22[5] := er16 * er23[5];
        er16 := er16 * (1 - er22[5]);
    	er22[3] := er16 * er23[3];
        er16 := er16 * (1 - er22[3]);
    	er22[1] := er16 * er23[1];
    	er17 := er22[1]*er22[1]*2 + er22[3]*er22[3]*4 +
              er22[5]*er22[5]*8 + er22[7]*er22[7]*16 +
              er22[2]*er22[2]*3 + er22[4]*er22[4]*6 +
              er22[6]*er22[6]*12 + er22[8]*er22[8]*24;
    	er18 := er22[1]*er22[1] + er22[3]*er22[3] +
              er22[5]*er22[5] + er22[7]*er22[7] +
              er22[2]*er22[2] + er22[4]*er22[4] +
              er22[6]*er22[6] + er22[8]*er22[8];
      if (er18 = 0) then er19 := 0 else er19 := er17 / er18;
    end;
    Result[Bar] := er19;
  end;
end;

function JCFB48(SrcA: TSeries; Smooth: Integer): TSeries;
var
  Bar: integer;
  Value: Double;
  er1, er2, er3, er4, er5, er6, er7, er8, er9, er10: TSeries;
  er20, er21, er29: integer;
  er15, er16, er17, er18, er19: Double;
  er22, er23: array[1..10] of Double;
begin
  SetLength (Result, High(SrcA) + 1);
  er20 := 0; er21 := 0; er29 := 0;
  er15 := 0; er16 := 0; er17 := 0; er18 := 0; er19 := 0;

  FillChar (er22, sizeof(er22), 0);
  FillChar (er23, sizeof(er23), 0);

  er15 := 1;
  er16 := 1;
  er19 := 20;
  er29 := Smooth;

  er1 := JCFBaux(SrcA, 2);
  er2 := JCFBaux(SrcA, 3);
  er3 := JCFBaux(SrcA, 4);
  er4 := JCFBaux(SrcA, 6);
  er5 := JCFBaux(SrcA, 8);
  er6 := JCFBaux(SrcA, 12);
  er7 := JCFBaux(SrcA, 16);
  er8 := JCFBaux(SrcA, 24);
  er9 := JCFBaux(SrcA, 32);
  er10 := JCFBaux(SrcA, 48);

  for Bar := 1 to High(SrcA) do begin
    if Bar <= er29 then begin
      for er21 := 1 to 10 do
        er23[er21] := 0;
      for er20 := 0 to Bar-1 do begin
        er23[1] := er23[1] + er1[Bar-er20];
        er23[2] := er23[2] + er2[Bar-er20];
        er23[3] := er23[3] + er3[Bar-er20];
        er23[4] := er23[4] + er4[Bar-er20];
        er23[5] := er23[5] + er5[Bar-er20];
        er23[6] := er23[6] + er6[Bar-er20];
        er23[7] := er23[7] + er7[Bar-er20];
        er23[8] := er23[8] + er8[Bar-er20];
        er23[9] := er23[9] + er9[Bar-er20];
        er23[10] := er23[10] + er10[Bar-er20];
      end;
      for er21 := 1 to 10 do
        er23[er21] := er23[er21] / Bar;
    end else begin
      er23[1] := er23[1] + (er1[Bar] - er1[Bar-er29]) / er29;
      er23[2] := er23[2] + (er2[Bar] - er2[Bar-er29]) / er29;
      er23[3] := er23[3] + (er3[Bar] - er3[Bar-er29]) / er29;
      er23[4] := er23[4] + (er4[Bar] - er4[Bar-er29]) / er29;
      er23[5] := er23[5] + (er5[Bar] - er5[Bar-er29]) / er29;
      er23[6] := er23[6] + (er6[Bar] - er6[Bar-er29]) / er29;
      er23[7] := er23[7] + (er7[Bar] - er7[Bar-er29]) / er29;
      er23[8] := er23[8] + (er8[Bar] - er8[Bar-er29]) / er29;
      er23[9] := er23[9] + (er9[Bar] - er9[Bar-er29]) / er29;
      er23[10] := er23[10] + (er10[Bar] - er10[Bar-er29]) / er29;
    end;
    if Bar > 5 then begin
      er15 := 1;
      er22[10] := er15 * er23[10];
      er15 := er15 * (1 - er22[10]);
      er22[8] := er15 * er23[8];
      er15 := er15 * (1 - er22[8]);
      er22[6] := er15 * er23[6];
      er15 := er15 * (1 - er22[6]);
      er22[4] := er15 * er23[4];
      er15 := er15 * (1 - er22[4]);
      er22[2] := er15 * er23[2];
      er16 := 1;
      er22[9] := er16 * er23[9];
      er16 := er16 * (1 - er22[9]);
      er22[7] := er16 * er23[7];
      er16 := er16 * (1 - er22[7]);
      er22[5] := er16 * er23[5];
      er16 := er16 * (1 - er22[5]);
      er22[3] := er16 * er23[3];
      er16 := er16 * (1 - er22[3]);
      er22[1] := er16 * er23[1];
      er17 := er22[1]*er22[1]*2 + er22[3]*er22[3]*4 +
              er22[5]*er22[5]*8 + er22[7]*er22[7]*16 +
              er22[9]*er22[9]*32 + er22[2]*er22[2]*3 +
              er22[4]*er22[4]*6 + er22[6]*er22[6]*12 +
              er22[8]*er22[8]*24 + er22[10]*er22[10]*48;
      er18 := er22[1]*er22[1] + er22[3]*er22[3] +
              er22[5]*er22[5] + er22[7]*er22[7] +
              er22[9]*er22[9] + er22[2]*er22[2] +
              er22[4]*er22[4] + er22[6]*er22[6] +
              er22[8]*er22[8] + er22[10]*er22[10];
      if (er18 = 0) then er19 := 0 else er19 := er17 / er18;
    end;
    Result[Bar] := er19;
  end;
end;


function JCFB96(SrcA: TSeries; Smooth: Integer): TSeries;
var
  Bar: integer;
  Value: Double;
  er1, er2, er3, er4, er5, er6, er7, er8, er9, er10, er11, er12: TSeries;
  er20, er21, er29: integer;
  er15, er16, er17, er18, er19: Double;
  er22, er23: array[1..12] of Double;
begin
  SetLength (Result, High(SrcA) + 1);
  er20 := 0; er21 := 0; er29 := 0;
  er15 := 0; er16 := 0; er17 := 0; er18 := 0; er19 := 0;

  FillChar (er22, sizeof(er22), 0);
  FillChar (er23, sizeof(er23), 0);

  er15 := 1;
  er16 := 1;
  er19 := 20;
  er29 := Smooth;

  er1 := JCFBaux(SrcA, 2);
  er2 := JCFBaux(SrcA, 3);
  er3 := JCFBaux(SrcA, 4);
  er4 := JCFBaux(SrcA, 6);
  er5 := JCFBaux(SrcA, 8);
  er6 := JCFBaux(SrcA, 12);
  er7 := JCFBaux(SrcA, 16);
  er8 := JCFBaux(SrcA, 24);
  er9 := JCFBaux(SrcA, 32);
  er10 := JCFBaux(SrcA, 48);
  er11 := JCFBaux(SrcA, 64);
  er12 := JCFBaux(SrcA, 96);

  for Bar := 1 to High (SrcA) do begin
    if Bar <= er29 then begin
      for er21 := 1 to 12 do
        er23[er21] := 0;
      for er20 := 0 to Bar-1 do begin
        er23[1] := er23[1] + er1[Bar-er20];
        er23[2] := er23[2] + er2[Bar-er20];
        er23[3] := er23[3] + er3[Bar-er20];
        er23[4] := er23[4] + er4[Bar-er20];
        er23[5] := er23[5] + er5[Bar-er20];
        er23[6] := er23[6] + er6[Bar-er20];
        er23[7] := er23[7] + er7[Bar-er20];
        er23[8] := er23[8] + er8[Bar-er20];
        er23[9] := er23[9] + er9[Bar-er20];
        er23[10] := er23[10] + er10[Bar-er20];
        er23[11] := er23[11] + er11[Bar-er20];
        er23[12] := er23[12] + er12[Bar-er20];
      end;
      for er21 := 1 to 12 do
        er23[er21] := er23[er21] / Bar;
    end else begin
      er23[1] := er23[1] + (er1[Bar] - er1[Bar-er29]) / er29;
      er23[2] := er23[2] + (er2[Bar] - er2[Bar-er29]) / er29;
      er23[3] := er23[3] + (er3[Bar] - er3[Bar-er29]) / er29;
      er23[4] := er23[4] + (er4[Bar] - er4[Bar-er29]) / er29;
      er23[5] := er23[5] + (er5[Bar] - er5[Bar-er29]) / er29;
      er23[6] := er23[6] + (er6[Bar] - er6[Bar-er29]) / er29;
      er23[7] := er23[7] + (er7[Bar] - er7[Bar-er29]) / er29;
      er23[8] := er23[8] + (er8[Bar] - er8[Bar-er29]) / er29;
      er23[9] := er23[9] + (er9[Bar] - er9[Bar-er29]) / er29;
      er23[10] := er23[10] + (er10[Bar] - er10[Bar-er29]) / er29;
      er23[11] := er23[11] + (er11[Bar] - er11[Bar-er29]) / er29;
      er23[12] := er23[12] + (er12[Bar] - er12[Bar-er29]) / er29;
    end;
    if Bar > 5 then begin
      er15 := 1;
      er22[12] := er15 * er23[12];
      er15 := er15 * (1 - er22[12]);
      er22[10] := er15 * er23[10];
      er15 := er15 * (1 - er22[10]);
      er22[8] := er15 * er23[8];
      er15 := er15 * (1 - er22[8]);
      er22[6] := er15 * er23[6];
      er15 := er15 * (1 - er22[6]);
      er22[4] := er15 * er23[4];
      er15 := er15 * (1 - er22[4]);
      er22[2] := er15 * er23[2];
      er16 := 1;
      er22[11] := er16 * er23[11];
      er16 := er16 * (1 - er22[11]);
      er22[9] := er16 * er23[9];
      er16 := er16 * (1 - er22[9]);
      er22[7] := er16 * er23[7];
      er16 := er16 * (1 - er22[7]);
      er22[5] := er16 * er23[5];
      er16 := er16 * (1 - er22[5]);
      er22[3] := er16 * er23[3];
      er16 := er16 * (1 - er22[3]);
      er22[1] := er16 * er23[1];
      er17 := er22[1]*er22[1]*2 + er22[3]*er22[3]*4 +
              er22[5]*er22[5]*8 + er22[7]*er22[7]*16 +
              er22[9]*er22[9]*32 + er22[11]*er22[11]*64 +
              er22[2]*er22[2]*3 + er22[4]*er22[4]*6 +
              er22[6]*er22[6]*12 + er22[8]*er22[8]*24 +
              er22[10]*er22[10]*48 + er22[12]*er22[12]*96;
      er18 := er22[1]*er22[1] + er22[3]*er22[3] +
              er22[5]*er22[5] + er22[7]*er22[7] +
              er22[9]*er22[9] + er22[11]*er22[11] +
              er22[2]*er22[2] + er22[4]*er22[4] +
              er22[6]*er22[6] + er22[8]*er22[8] +
              er22[10]*er22[10] + er22[12]*er22[12];
      if (er18 = 0) then er19 := 0 else er19 := er17 / er18;
    end;
    Result[Bar] := er19;
  end;
end;

function JCFB192(SrcA: TSeries; Smooth: Integer): TSeries;
var
  Bar: integer;
  Value: Double;
  er1, er2, er3, er4, er5, er6, er7, er8, er9, er10, er11, er12, er13, er14: TSeries;
  er20, er21, er29: integer;
  er15, er16, er17, er18, er19: Double;
  er22, er23: array[1..14] of Double;
begin
  SetLength (Result, High(SrcA) + 1);
  er20 := 0; er21 := 0; er29 := 0;
  er15 := 0; er16 := 0; er17 := 0; er18 := 0; er19 := 0;

  FillChar (er22, sizeof(er22), 0);
  FillChar (er23, sizeof(er23), 0);

  er15 := 1;
  er16 := 1;
  er19 := 20;
  er29 := Smooth;

  er1 := JCFBaux(SrcA, 2);
  er2 := JCFBaux(SrcA, 3);
  er3 := JCFBaux(SrcA, 4);
  er4 := JCFBaux(SrcA, 6);
  er5 := JCFBaux(SrcA, 8);
  er6 := JCFBaux(SrcA, 12);
  er7 := JCFBaux(SrcA, 16);
  er8 := JCFBaux(SrcA, 24);
  er9 := JCFBaux(SrcA, 32);
  er10 := JCFBaux(SrcA, 48);
  er11 := JCFBaux(SrcA, 64);
  er12 := JCFBaux(SrcA, 96);
  er13 := JCFBaux(SrcA, 128);
  er14 := JCFBaux(SrcA, 192);

  for Bar := 1 to High (SrcA) do
  begin
    if Bar <= er29 then begin
      for er21 := 1 to 14 do
        er23[er21] := 0;
      for er20 := 0 to Bar-1 do begin
        er23[1] := er23[1] + er1[Bar-er20];
        er23[2] := er23[2] + er2[Bar-er20];
        er23[3] := er23[3] + er3[Bar-er20];
        er23[4] := er23[4] + er4[Bar-er20];
        er23[5] := er23[5] + er5[Bar-er20];
        er23[6] := er23[6] + er6[Bar-er20];
        er23[7] := er23[7] + er7[Bar-er20];
        er23[8] := er23[8] + er8[Bar-er20];
        er23[9] := er23[9] + er9[Bar-er20];
        er23[10] := er23[10] + er10[Bar-er20];
        er23[11] := er23[11] + er11[Bar-er20];
        er23[12] := er23[12] + er12[Bar-er20];
        er23[13] := er23[13] + er13[Bar-er20];
        er23[14] := er23[14] + er14[Bar-er20];
      end;
      for er21 := 1 to 14 do
        er23[er21] := er23[er21] / Bar;
    end else begin
      er23[1] := er23[1] + (er1[Bar] - er1[Bar-er29]) / er29;
      er23[2] := er23[2] + (er2[Bar] - er2[Bar-er29]) / er29;
      er23[3] := er23[3] + (er3[Bar] - er3[Bar-er29]) / er29;
      er23[4] := er23[4] + (er4[Bar] - er4[Bar-er29]) / er29;
      er23[5] := er23[5] + (er5[Bar] - er5[Bar-er29]) / er29;
      er23[6] := er23[6] + (er6[Bar] - er6[Bar-er29]) / er29;
      er23[7] := er23[7] + (er7[Bar] - er7[Bar-er29]) / er29;
      er23[8] := er23[8] + (er8[Bar] - er8[Bar-er29]) / er29;
      er23[9] := er23[9] + (er9[Bar] - er9[Bar-er29]) / er29;
      er23[10] := er23[10] + (er10[Bar] - er10[Bar-er29]) / er29;
      er23[11] := er23[11] + (er11[Bar] - er11[Bar-er29]) / er29;
      er23[12] := er23[12] + (er12[Bar] - er12[Bar-er29]) / er29;
      er23[13] := er23[13] + (er13[Bar] - er13[Bar-er29]) / er29;
      er23[14] := er23[14] + (er14[Bar] - er14[Bar-er29]) / er29;
    end;
    if Bar > 5 then begin
      er15 := 1;
      er22[14] := er15 * er23[14];
      er15 := er15 * (1 - er22[14]);
      er22[12] := er15 * er23[12];
      er15 := er15 * (1 - er22[12]);
      er22[10] := er15 * er23[10];
      er15 := er15 * (1 - er22[10]);
      er22[8] := er15 * er23[8];
      er15 := er15 * (1 - er22[8]);
      er22[6] := er15 * er23[6];
      er15 := er15 * (1 - er22[6]);
      er22[4] := er15 * er23[4];
      er15 := er15 * (1 - er22[4]);
      er22[2] := er15 * er23[2];
      er16 := 1;
      er22[13] := er16 * er23[13];
      er16 := er16 * (1 - er22[13]);
      er22[11] := er16 * er23[11];
      er16 := er16 * (1 - er22[11]);
      er22[9] := er16 * er23[9];
      er16 := er16 * (1 - er22[9]);
      er22[7] := er16 * er23[7];
      er16 := er16 * (1 - er22[7]);
      er22[5] := er16 * er23[5];
      er16 := er16 * (1 - er22[5]);
      er22[3] := er16 * er23[3];
      er16 := er16 * (1 - er22[3]);
      er22[1] := er16 * er23[1];
      er17 := er22[1]*er22[1]*2 + er22[3]*er22[3]*4 +
              er22[5]*er22[5]*8 + er22[7]*er22[7]*16 +
              er22[9]*er22[9]*32 + er22[11]*er22[11]*64 +
              er22[13]*er22[13]*128 + er22[2]*er22[2]*3 +
              er22[4]*er22[4]*6 + er22[6]*er22[6]*12 +
              er22[8]*er22[8]*24 + er22[10]*er22[10]*48 +
              er22[12]*er22[12]*96 + er22[14]*er22[14]*192;
      er18 := er22[1]*er22[1] + er22[3]*er22[3] +
              er22[5]*er22[5] + er22[7]*er22[7] +
              er22[9]*er22[9] + er22[11]*er22[11] +
              er22[13]*er22[13] + er22[2]*er22[2] +
              er22[4]*er22[4] + er22[6]*er22[6] +
              er22[8]*er22[8] + er22[10]*er22[10] +
              er22[12]*er22[12] + er22[14]*er22[14];
      if (er18 = 0) then er19 := 0 else er19 := er17 / er18;
    end;
    Result[Bar] := er19;
  end;
end;

function JCFBSeries(const SrcA: TSeries; AFractalType: Integer; ASmooth: Integer): TSeries;
var
  Bar: integer;
begin
  SetLength (Result, High(SrcA) + 1);
  case AFractalType of
    1: Result := JCFB24(SrcA, ASmooth);
    2: Result := JCFB48(SrcA, ASmooth);
    3: Result := JCFB96(SrcA, ASmooth);
    4: Result := JCFB192(SrcA, ASmooth);
  end;
end;

function JXRSXSeries (const SrcA, LenA: TSeries): TSeries;
// Вычисляет RSX переменной длины, заданной отдельно на каждом баре (в серии LenA)
var
  Bar: integer;
  Value: Double;
  f0, f88, f90: integer;
  f8, f10, f18, f20, f28, f30, f38, f40, f48, f50, f58, f60, f68, f70, f78, f80: Double;
  v4, v8, vC, v10, v14, v18, v1C, v20: Double;
begin
  SetLength (Result, High(SrcA)+1);

  f0 := 0; f88 := 0; f90 := 0;
  f8 := 0; f10 := 0; f18 := 0; f20 := 0; f28 := 0; f30 := 0; f38 := 0; f40 := 0;
  f48 := 0; f50 := 0; f58 := 0; f60 := 0; f68 := 0; f70 := 0; f78 := 0; f80 := 0;
  v4 := 0; v8 := 0; vC := 0; v10 := 0; v14 := 0; v18 := 0; v1C := 0; v20 := 0;

  for Bar := 0 to High (SrcA) do begin
    if (f90 = 0) then begin
      f90 := 1;
      f0 := 0;
      if (Trunc(LenA[Bar])-1 >= 5) then f88 := Trunc(LenA[Bar])-1 else f88 := 5;
      f8 := 100*SrcA[Bar];
      f18 := 3 / (Trunc(LenA[Bar]) + 2);
      f20 := 1 - f18;
    end else begin
      if (f88 <= f90) then f90 := f88 + 1 else f90 := f90 + 1;
      f10 := f8;
      f8 := 100*SrcA[Bar];
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
    Result[Bar] := Value;
  end;
end;

function JXVELaux1(const SrcA: TSeries; DepthSeries: TSeries): TSeries;
var
  Bar: integer;
  jrc05, jrc06, jrc07, jrc08, jrc09: Double;
  jrc02, jrc04, jrc10: integer;
begin
  SetLength (Result, High(SrcA)+1);
  jrc05 := 0; jrc06 := 0; jrc07 := 0; jrc08 := 0; jrc09 := 0;
  jrc02 := 0; jrc04 := 0; jrc10 := 0;

  for Bar := 0 to High (SrcA) do
  begin
    jrc02 := ceil(DepthSeries[Bar]);
    jrc04 := jrc02 + 1;
    if (Bar < jrc04) then continue;
    jrc05 := jrc04 * (jrc04+1) / 2;
    jrc06 := jrc05 * (2*jrc04+1) / 3;
    jrc07 := jrc05 * jrc05 * jrc05 - jrc06 * jrc06;
    jrc08 := 0;
    jrc09 := 0;
    for jrc10 := 0 to jrc02 do begin
      jrc08 := jrc08 + SrcA[Bar-jrc10] * (jrc04 - jrc10);
      jrc09 := jrc09 + SrcA[Bar-jrc10] * (jrc04 - jrc10) * (jrc04 - jrc10);
    end;
    Result[Bar] := (jrc09*jrc05 - jrc08*jrc06) / jrc07;
  end;
end;

function JXVELaux3(const SrcA: TSeries; Period: Double): TSeries;
var
  Bar: integer;
  input1, jrc02, jrc03, jrc04, jrc05, jrc08, jrc09, jrc10, jrc12, jrc13: Double;
  jrc14, jrc16, jrc17, jrc18, jrc19, jrc20, jrc21, jrc22, jrc25: Double;
  jrc01, jrc06, jrc07, jrc11, jrc15, jrc23, jrc24, jrc26, jrc27, jrc28, jrc29: integer;
  jrc30: array[0..1000] of Double;
begin
  SetLength (Result, High(SrcA)+1);

  input1 := 0; jrc02 := 0; jrc03 := 0; jrc04 := 0; jrc05 := 0; jrc07 := 0; jrc08 := 0;
  jrc09 := 0; jrc10 := 0; jrc12 := 0; jrc13 := 0; jrc14 := 0; jrc16 := 0; jrc17 := 0;
  jrc18 := 0; jrc19 := 0; jrc20 := 0; jrc21 := 0; jrc22 := 0; jrc23 := 0; jrc24 := 0;
  jrc25 := 0; jrc01 := 0; jrc06 := 0; jrc11 := 0; jrc15 := 0; jrc26 := 0; jrc27 := 0;
  jrc28 := 0; jrc29 := 0;
  FillChar (jrc30, SizeOf(jrc30), 0);

  jrc01 := 30;
  jrc02 := 0.0001;
  jrc28 := 1;
  jrc29 := 1;

  for Bar := 0 to High (SrcA) do begin
    input1 := SrcA[Bar];
    jrc27 := Bar;
    if (Bar = 0) then jrc26 := jrc27;
    if (Bar > 0) then begin
      if (jrc24 <= 0) then jrc24 := 1001;
      jrc24 := jrc24 - 1;
      jrc30[jrc24] := input1;
    end;
    if (jrc27 < jrc26 + jrc01) then jrc20 := input1 else begin
    	jrc03 := min(500, max(jrc02, Period));
    	jrc07 := min(jrc01, ceil(jrc03));
    	jrc04 := 0.86 - 0.55 / sqrt(jrc03);
    	jrc05 := 1 - exp(-ln(4) / jrc03 / 2);
    	jrc06 := Trunc(max(jrc01 + 1, ceil(2*jrc03)));
    	jrc11 := Trunc(min(jrc27 - jrc26 + 1, jrc06));
    	jrc12 := jrc11 * (jrc11+1) * (jrc11-1) / 12;
    	jrc13 := (jrc11+1) / 2;
    	jrc14 := (jrc11-1) / 2;
    	jrc09 := 0;
    	jrc10 := 0;
    	for jrc15 := jrc11 - 1 downto 0 do begin
    		jrc23 := (jrc24 + jrc15) mod 1001;
    		jrc09 := jrc09 + jrc30[jrc23];
		    jrc10 := jrc10 + jrc30[jrc23] * (jrc14 - jrc15);
    	end;
    	jrc16 := jrc10 / jrc12;
      jrc17 := jrc09 / jrc11 - jrc16 * jrc13;
      jrc18 := 0;
    	for jrc15 := jrc11 - 1 downto 0 do begin
    		jrc17 := jrc17 + jrc16;
        jrc23 := (jrc24+jrc15) mod 1001;
  		  jrc18 := jrc18 + abs(jrc30[jrc23] - jrc17);
    	end;
      jrc25 := 1.2 * jrc18 / jrc11;
      if (jrc11 < jrc06) then jrc25 := jrc25 * power(jrc06 / jrc11, 0.25);
      if (jrc28 = 1) then begin
        jrc28 := 0;
        jrc19 := jrc25;
      end else jrc19 := jrc19 + (jrc25 - jrc19) * jrc05;
      jrc19 := max(jrc02, jrc19);
      if (jrc29 = 1) then begin
        jrc29 := 0;
    		jrc08 := (jrc30[jrc24] - jrc30[(jrc24+jrc07) mod 1001]) / jrc07;
    	end;
      jrc21 := input1 - (jrc20 + jrc08 * jrc04);
    	jrc22 := 1 - exp(-abs(jrc21) / jrc19 / jrc03);
      jrc08 := jrc22 * jrc21 + jrc08 * jrc04;
    	jrc20 := jrc20 + jrc08;
    end;
    Result[Bar] := jrc20;
  end;
end;

function JXVELSeries(const SrcA: TSeries; DepthSrcA: TSeries; APeriod: Double): TSeries;
begin
  //  for Bar := 0 to High (SrcA) do
  //    @Result[Bar] := GetSeriesValue(Bar, JXVELaux3(JXVELaux1(Series, DepthSeries), Period));
  Result := JXVELaux3(JXVELaux1(SrcA, DepthSrcA), APeriod);
end;

function JVELaux1(const SrcA: TSeries; Depth: integer): TSeries;
var
  Bar: integer;
  jrc04, jrc05, jrc06, jrc07, jrc08, jrc09: Double;
  jrc01: TSeries;
  jrc02, jrc10: integer;
begin
  SetLength (Result, High(SrcA)+1);
  jrc04 := 0; jrc05 := 0; jrc06 := 0; jrc07 := 0; jrc08 := 0; jrc09 := 0;

  jrc01 := SrcA;
  jrc02 := Depth;
  jrc04 := jrc02 + 1;
  jrc05 := jrc04 * (jrc04+1) / 2;
  jrc06 := jrc05 * (2*jrc04+1) / 3;
  jrc07 := jrc05 * jrc05 * jrc05 - jrc06 * jrc06;
  for Bar := jrc02 to High (SrcA) do
  begin
    jrc08 := 0;
    jrc09 := 0;
    for jrc10 := 0 to jrc02 do
    begin
      jrc08 := jrc08 + jrc01[Bar-jrc10] * (jrc04 - jrc10);
      jrc09 := jrc09 + jrc01[Bar-jrc10] * (jrc04 - jrc10) * (jrc04 - jrc10);
    end;
    Result[Bar] := (jrc09*jrc05 - jrc08*jrc06) / jrc07;
  end;
end;

function JVELaux3(const SrcA: TSeries): TSeries;
var
  Bar: integer;
  JR02, JR04, JR05, JR08, JR09, JR10, JR12, JR13, JR14, JR16, JR17, JR19, JR20, JR22, JR23, JR28: Double;
  JR01, JR03, JR06, JR07, JR11, JR15, JR18, JR24, JR25, JR26, JR27, JR29: integer;
  JR21, JR21a, JR21b: Double;
  JR40, JR41 : array[0..99] of Double;
begin
  SetLength (Result, High(SrcA)+1);
  JR02 := 0; JR04 := 0; JR05 := 0; JR08 := 0; JR09 := 0; JR10 := 0; JR12 := 0; JR13 := 0;
  JR14 := 0; JR16 := 0; JR17 := 0; JR19 := 0; JR20 := 0; JR22 := 0; JR23 := 0; JR28 := 0;
  JR01 := 0; JR03 := 0; JR06 := 0; JR07 := 0; JR11 := 0; JR15 := 0; JR18 := 0;
  JR24 := 0; JR25 := 0; JR26 := 0; JR27 := 0; JR29 := 0;

  JR21 := 0; JR21a := 0; JR21b := 0;

  FillChar (JR40, SizeOf(JR40), 0);
  FillChar (JR41, SizeOf(JR41), 0);

  JR01 := 30;
  JR02 := 0.0001;

  for Bar := JR01 to High (SrcA) do
  begin
    JR27 := Bar;
    If Bar = JR01 then begin
	    JR28 := 0;
    	for JR29 := 1 to JR01-1 do
      	if SrcA[Bar-JR29] = SrcA[Bar-JR29-1] then JR28 := JR28 + 1;
      if JR28 < (JR01-1) then JR26 := JR27-JR01 else JR26 := JR27;
    	JR18 := 0;
    	JR25 := 0;
    	JR21 := SrcA[Bar-1];
    	JR03 := 3;
    	JR04 := 0.86 - 0.55 / sqrt(JR03);
    	JR05 := 1 - exp(-ln(4) / JR03);
    	JR06 := JR01+1;
    	JR07 := 3;
    	JR08 := (SrcA[Bar] - SrcA[Bar-JR07]) / JR07;
    	JR11 := Trunc(min(1+JR27-JR26, JR06));
    	for JR15 := JR11-1 downto 1 do begin
    		if JR25 <= 0 then JR25 := 100;
    		JR25 := JR25-1;
    		JR41[JR25] := SrcA[Bar-JR15];
    	end;
    end;
    If JR25 <= 0 then JR25 := 100;
    JR25 := JR25-1;
    JR41[JR25] := SrcA[Bar];
    if JR11 <= JR01 then begin
    	if Bar = JR01 then JR21 := SrcA[Bar] else JR21 := sqrt(JR05)*SrcA[Bar] + (1-sqrt(JR05))*JR21a;
    	if Bar > JR01+1 then JR08 := (JR21 - JR21b)/2 else JR08 := 0;
      JR11 := JR11 + 1;
    end else begin
    	If JR11 <= JR06 then begin
    		JR12 := JR11 * (JR11+1) * (JR11-1) / 12;
    		JR13 := (JR11+1)/2;
                JR14 := (JR11-1)/2;
    		JR09 := 0;
                JR10 := 0;
    		for JR15 := JR11-1 downto 0 do begin
		    	JR24 := (JR25+JR15) mod 100;
    			JR09 := JR09 + JR41[JR24];
		    	JR10 := JR10 + JR41[JR24]*(JR14 - JR15);
    		end;
    		JR16 := JR10/JR12;
		JR17 := (JR09/JR11) - (JR16*JR13);
    		JR19 := 0;
		for JR15 := JR11-1 downto 0 do begin
    			JR17 := JR17+JR16;
		    	JR24 := (JR25+JR15) mod 100;
    			JR40[JR15] := abs(JR41[JR24]-JR17);
		    	JR19 := JR19 + JR40[JR15];
    		end;
    		JR20 := (JR19/JR11) * power(JR06/JR11, 0.25);
		    JR11 := JR11+1;
    	end else begin
    		if (Bar mod 1000)=0 then begin
		    	JR09 := 0;
    			JR10 := 0;
		    	for JR15 := JR06-1 downto 0 do begin
				    JR24 := (JR25+JR15) mod 100;
    				JR09 := JR09 + JR41[JR24];
		    		JR10 := JR10 + JR41[JR24]*(JR14 - JR15);
    			end;
		    end else begin
    			JR24 := (JR25+JR06) mod 100;
		    	JR10 := JR10 - JR09 + JR41[JR24]*JR13 + SrcA[Bar]*JR14;
    			JR09 := JR09 - JR41[JR24] + SrcA[Bar];
		    end;
    		if JR18 <= 0 then JR18 := JR06;
    		JR18 := JR18 - 1;
		    JR19 := JR19 - JR40[JR18];
    		JR16 := JR10/JR12;
		    JR17 := (JR09/JR06) + (JR16*JR14);
    		JR40[JR18] := abs(SrcA[Bar]-JR17);
		    JR19 := max(JR02, (JR19 + JR40[JR18]));
    		JR20 := JR20 + ((JR19/JR06) - JR20) * JR05;
    	end;
    	JR20 := max(JR02, JR20);
    	JR22 := SrcA[Bar] - (JR21 + JR08*JR04);
    	JR23 := 1-exp(-abs(JR22)/JR20/JR03);
    	JR08 := JR23*JR22 + JR08*JR04;
    	JR21 := JR21 + JR08;
    end;
    JR21b := JR21a; JR21a := JR21;
    Result[Bar] := JR21;
  end;
end;

function JVELSeries(const SrcA: TSeries; ADepth: integer): TSeries;
var
  Bar: integer;
  Value: Double;
begin
   //  for Bar := 0 to High (SrcA) do
   //    @Result[Bar] := GetSeriesValue(Bar, JVELaux3(JVELaux1(Series, Depth)));
  Result := JVELaux3(JVELaux1(SrcA, ADepth));
end;

function JAVELSeries(const SrcA: TSeries; ALoLen, AHiLen: Integer; ASensitivity, APeriod: Double): TSeries;
var
  Bar, j, k: integer;
  avg1, avg2, value2, value3: Double;
  eps: Double;
  value1, value4: TSeries;
begin
  SetLength (Result, High(SrcA)+1);
  SetLength (value1, High(SrcA)+1);
  SetLength (value4, High(SrcA)+1);

  eps := 0.001;
  for Bar := 1 to High(SrcA) do
     value1[Bar] := abs(SrcA[Bar] - SrcA[Bar-1]);

  for Bar := 0 to High(SrcA) do begin
    avg1 := 0;
    if (Bar < 99) then k := Bar else k := 99;
    for j := 0 to k do
       avg1 := avg1 + value1[Bar-j];
    avg1 := avg1 / (k+1);

    avg2 := 0;
    if (Bar < 9) then k := Bar else k := 9;
    for j := 0 to k do
       avg2 := avg2 + value1[Bar-j];
    avg2 := avg2 / (k+1);

    value2 := ASensitivity * ln((eps+avg1) / (eps+avg2));
    value3 := value2 / (1 + abs(value2));
    value4[Bar] := ALoLen + (AHiLen-ALoLen) * (1+value3) / 2;
  end;

  //  for Bar := 0 to High(SrcA) do
  //    Result[Bar] := GetSeriesValue(Bar, JXVELaux3(JXVELaux1(Series, value4), Period));
  Result := JXVELaux3(JXVELaux1(SrcA, value4), APeriod);
end;

function TrueRangeSeries (const CloseA, HighA, LowA: TSeries): TSeries;
var
  Bar: Integer;
  m1, m2, m3: Double;
begin
  SetLength (Result, High(CloseA)+1);
  // TR = max(abs(High - Low), abs(High - Closei-1), abs(Low - Closei-1)).
  for Bar := 2 to High (CloseA) do begin
    m1 := abs(HighA[Bar] - LowA[Bar]);
    m2 := abs(HighA[Bar] - CloseA [Bar-1]);
    m3 := abs(LowA[Bar] - CloseA [Bar-1]);
    Result[Bar] := Max (Max (m1, m2), m3);
  end;
end;

function JDMXplusSeries(const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;
var
  upward, numer, denom: TSeries;
  Bar: integer;
  v1, v2, Value: Double;
begin
  SetLength (Result, High(SrcA)+1);
  SetLength (upward, High(SrcA)+1);
  SetLength (numer, High(SrcA)+1);
  SetLength (denom, High(SrcA)+1);

  for Bar := 1 to High (SrcA) do begin
    v1 := 100 * (HighA[Bar] - HighA[Bar-1]);
    v2 := 100 * (LowA[Bar-1] - LowA[Bar]);
    if ((v1 > v2) and (v1 > 0)) then upward[Bar] := v1 else upward[Bar] := 0;
  end;

  numer := JJMASeries(upward, ALen, -100);
  denom := JJMASeries(TrueRangeSeries(SrcA, HighA, LowA), ALen, -100);

  for Bar := 0 to High (SrcA) do begin
    if (denom[Bar] > 0.00001) and (Bar > 40)
      then Value := 100 * numer[Bar] / denom[Bar]
      else Value := 0;
    Result[Bar] := Value;
  end;
end;

function JDMXminusSeries(const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;
var
  downward, numer, denom: TSeries;
  Bar: integer;
  v1, v2, Value: Double;
begin
  SetLength (Result, High(SrcA)+1);
  SetLength (downward, High(SrcA)+1);
  SetLength (numer, High(SrcA)+1);
  SetLength (denom, High(SrcA)+1);

  for Bar := 1 to High (SrcA) do begin
    v1 := 100 * (HighA[Bar] - HighA[Bar-1]);
    v2 := 100 * (LowA[Bar-1] - LowA[Bar]);
    if ((v2 > v1) and (v2 > 0)) then downward[Bar] := v2 else downward[Bar] := 0;
  end;

  numer := JJMASeries(downward, ALen, -100);
  denom := JJMASeries(TrueRangeSeries(SrcA, HighA, LowA), ALen, -100);

  for Bar := 0 to High (SrcA) do begin
    if (denom[Bar] > 0.00001) and (Bar > 40)
      then Value := 100 * numer[Bar] / denom[Bar]
      else Value := 0;
    Result[Bar] := Value;
  end;
end;

function JDMXSeries(const SrcA, HighA, LowA: TSeries; ALen: Integer): TSeries;
var
  DMXplus, DMXminus: TSeries;
  Bar: integer;
  Value: Double;
begin
  SetLength (Result, High(SrcA)+1);

  DMXplus := JDMXplusSeries(SrcA, HighA, LowA, ALen);
  DMXminus := JDMXminusSeries(SrcA, HighA, LowA, ALen);

  for Bar := 0 to High (SrcA) do begin
    if (DMXplus[Bar] + DMXminus[Bar] > 0.00001)
      then Value := 100 * (DMXplus[Bar] - DMXminus[Bar]) / (DMXplus[Bar] + DMXminus[Bar])
      else Value := 0;
    Result[Bar] := Value;
  end;
end;

function JVELCFBSeries(SrcA: TSeries; ALoDepth, AHiDepth, AFractalType, ASmooth: integer): TSeries;
var
  vl, cfb: TSeries;
  Bar: integer;
  sr, cfbmin, cfbmax, Value: Double;
begin
  sr := 0; cfbmin := 0; cfbmax := 0;

  cfbmin := 99999;
  cfbmax := 0;
  cfb := JCFBSeries(SrcA, AFractalType, ASmooth);

   // В серии vl формируются периоды индикатора на каждом баре
  SetLength (vl, High(SrcA)+1);
  for Bar := 0 to High(SrcA) do begin
    if cfb[Bar] > cfbmax then cfbmax := cfb[Bar];
    if cfb[Bar] < cfbmin then cfbmin := cfb[Bar];
    if (cfbmax > cfbmin) then sr := (cfb[Bar] - cfbmin) / (cfbmax - cfbmin) else sr := 0.5;
    vl[Bar] := Trunc(ALoDepth + sr * (AHiDepth - ALoDepth));
  end;

  Result := JXVELaux3(JXVELaux1(SrcA, vl), 3);
end;

end.

