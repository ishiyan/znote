// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JVELCFB
function AJVELCFBSeries(Series: integer; LoDepth: integer; HiDepth: integer; FractalType: integer; Smooth: integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JVELCFB(' + GetDescription(Series) + ',' + IntToStr(LoDepth) + ',' + IntToStr(HiDepth) + ',' + IntToStr(FractalType) + ',' + IntToStr(Smooth) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JVELCFB (Result, Series, LoDepth, HiDepth, FractalType, Smooth, IWealthLabAuto);
end;

function AJVELCFB(Bar: integer; Series: integer; LoDepth: integer; HiDepth: integer; FractalType: integer; Smooth: integer): float;
begin
  Result := GetSeriesValue(Bar, AJVELCFBSeries(Series, LoDepth, HiDepth, FractalType, Smooth));
end;
