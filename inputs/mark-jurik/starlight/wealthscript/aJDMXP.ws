// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JDMX+
function AJDMXplusSeries(Series: Integer; Len: Integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JDMXplus(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  lib.JDMXP (Result, Series, Len, IWealthLabAuto);
end;
