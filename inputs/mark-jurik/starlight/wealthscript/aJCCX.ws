// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JCCX
function AJCCXSeries(Series: Integer; Len: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JCCX(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JCCX (Result, Series, Len, IWealthLabAuto);
end;

function AJCCX(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJCCXSeries(Series, Len));
end;


