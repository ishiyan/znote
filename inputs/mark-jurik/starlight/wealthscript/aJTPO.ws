// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JTPO
function AJTPOSeries(Series: Integer; Len: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JTPO(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then
    Exit;
  Result := CreateNamedSeries(sName);

  lib.JTPO (Result, Series, Len, IWealthLabAuto);
end;

function AJTPO(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJTPOSeries(Series, Len));
end;
