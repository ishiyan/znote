// Created by Starlight (extesy@yandex.ru). Compiled into dll by _landy

// JVEL
function AJVELSeries(Series: integer; Depth: integer): integer;
begin
  var sName: string;
  var lib: ComVariant;
  lib := CreateOleObject('Jurik.Indicator');

  sName := 'JVEL(' + GetDescription( Series ) + ',' + FloatToStr( Depth ) + ')';
  Result := FindNamedSeries( sName );
  if Result >= 0 then Exit;
  Result := CreateNamedSeries( sName );

  lib.JVEL (Result, Series, Depth, IWealthLabAuto);
end;

function AJVEL(Bar: integer; Series: Integer; Depth: Integer): float;
begin
  Result := GetSeriesValue(Bar, AJVELSeries(Series, Depth));
end;
