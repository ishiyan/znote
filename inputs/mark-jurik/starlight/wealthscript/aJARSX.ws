// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JARSX
function AJARSXSeries(Series: Integer; LoLen: Integer; HiLen: Integer; Sensitivity: Float): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JARSX(' + GetDescription(Series) + ',' + IntToStr(LoLen) + ',' + IntToStr(HiLen) + ',' + FloatToStr(Sensitivity) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JARSX (Result, Series, LoLen, HiLen, Sensitivity, IWealthLabAuto);
end;

function AJARSX(Bar: integer; Series: Integer; LoLen: Integer; HiLen: Integer; Sensitivity: Float): float;
begin
  Result := GetSeriesValue(Bar, AJARSXSeries(Series, LoLen, HiLen, Sensitivity));
end;

