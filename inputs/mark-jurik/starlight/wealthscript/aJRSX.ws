// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JRSX
function AJRSXSeries(Series: integer; Len: integer) : integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JRSX(' + GetDescription(Series) + ',' + FloatToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JRSX (Result, Series, Len, IWealthLabAuto);
end;

function AJRSX(Bar: integer; Series: integer; Len: integer): float;
begin
  Result := GetSeriesValue(Bar, AJRSXSeries(Series, Len));
end;
