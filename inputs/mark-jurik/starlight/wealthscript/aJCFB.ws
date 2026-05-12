// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JCFB
function AJCFBSeries(Series: Integer; FractalType: Integer; Smooth: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JCFB(' + GetDescription(Series) + ',' + IntToStr(FractalType) + ',' + IntToStr(Smooth) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JCFB (Result, Series, FractalType, Smooth, IWealthLabAuto);
end;

function AJCFB(Bar: integer; Series: Integer; FractalType: Integer; Smooth: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJCFBSeries(Series, FractalType, Smooth));
end;
