// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JAVEL
function AJAVELSeries(Series: integer; LoLen: integer; HiLen: integer; Sensitivity: float; Period: float): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JAVEL(' + GetDescription(Series) + ',' + FloatToStr(LoLen) + ',' + FloatToStr(HiLen) + ',' + FloatToStr(Sensitivity) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JAVEL (Result, Series, LoLen, HiLen, Sensitivity, Period, IWealthLabAuto);
end;

function AJAVEL(Bar: integer; Series: integer; LoLen: integer; HiLen: integer; Sensitivity: float; Period: float): float;
begin
  Result := GetSeriesValue(Bar, AJAVELSeries(Series, LoLen, HiLen, Sensitivity, Period));
end;


