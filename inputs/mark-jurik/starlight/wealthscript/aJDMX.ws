// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JDMX
function AJDMXSeries(Series: Integer; Len: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JDMX(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JDMX (Result, Series, Len, IWealthLabAuto);
end;

function AJDMX(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJDMXSeries(Series, Len));
end;
