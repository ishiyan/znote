// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JJMA
function AJJMASeries(Series: Integer; Len: Integer; Phase: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JJMA(' + GetDescription(Series) + ',' + IntToStr(Len) + ',' + IntToStr(Phase) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JJMA (Result, Series, Len, Phase, IWealthLabAuto);
end;

function AJJMA(Bar: integer; Series: Integer; Len: Integer; Phase: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJJMASeries(Series, Len, Phase));
end;
