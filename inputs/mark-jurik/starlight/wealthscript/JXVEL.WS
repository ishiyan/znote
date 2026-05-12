// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JXVELaux1(Series: integer; DepthSeries: integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var jrc05, jrc06, jrc07, jrc08, jrc09: float;
  var jrc02, jrc04, jrc10: integer;

  sName := 'JXVELaux1(' + GetDescription(Series) + ',' + GetDescription(DepthSeries) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  for Bar := 0 to BarCount() - 1 do
  begin
    jrc02 := ceil(@DepthSeries[Bar]);
    jrc04 := jrc02 + 1;
    if (Bar < jrc04) then continue;
    jrc05 := jrc04 * (jrc04+1) / 2;
    jrc06 := jrc05 * (2*jrc04+1) / 3;
    jrc07 := jrc05 * jrc05 * jrc05 - jrc06 * jrc06;
    jrc08 := 0;
    jrc09 := 0;
    for jrc10 := 0 to jrc02 do
    begin
      jrc08 := jrc08 + @Series[Bar-jrc10] * (jrc04 - jrc10);
      jrc09 := jrc09 + @Series[Bar-jrc10] * (jrc04 - jrc10) * (jrc04 - jrc10);
    end;
    @Result[Bar] := (jrc09*jrc05 - jrc08*jrc06) / jrc07;
  end;
end;

function JXVELaux3(Series: integer; Period: float): integer;
begin
  var Bar: integer;
  var sName: string;

  sName := 'JXVELaux3(' + GetDescription(Series) + ',' + FloatToStr(Period) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  var input1, jrc02, jrc03, jrc04, jrc05, jrc07, jrc08, jrc09, jrc10, jrc12, jrc13, jrc14, jrc16, jrc17, jrc18, jrc19, jrc20, jrc21, jrc22, jrc23, jrc24, jrc25: float;
  var jrc01, jrc06, jrc11, jrc15, jrc26, jrc27, jrc28, jrc29: integer;
  var jrc30: array[0..1000] of float;

  jrc01 := 30;
  jrc02 := 0.0001;
  jrc28 := 1;
  jrc29 := 1;

  for Bar := 0 to BarCount() - 1 do
  begin
    input1 := @Series[Bar];
    jrc27 := Bar;
    if (Bar = 0) then jrc26 := jrc27;
    if (Bar > 0) then begin
      if (jrc24 <= 0) then jrc24 := 1001;
      jrc24 := jrc24 - 1;
      jrc30[jrc24] := input1;
    end;
    if (jrc27 < jrc26 + jrc01) then jrc20 := input1 else begin
    	jrc03 := min(500, max(jrc02, Period));
    	jrc07 := min(jrc01, ceil(jrc03));
    	jrc04 := 0.86 - 0.55 / sqrt(jrc03);
    	jrc05 := 1 - exp(-ln(4) / jrc03 / 2);
    	jrc06 := int(max(jrc01 + 1, ceil(2*jrc03)));
    	jrc11 := int(min(jrc27 - jrc26 + 1, jrc06));
    	jrc12 := jrc11 * (jrc11+1) * (jrc11-1) / 12;
    	jrc13 := (jrc11+1) / 2;
    	jrc14 := (jrc11-1) / 2;
    	jrc09 := 0;
    	jrc10 := 0;
    	for jrc15 := jrc11 - 1 downto 0 do begin
    		jrc23 := (jrc24 + jrc15) mod 1001;
    		jrc09 := jrc09 + jrc30[jrc23];
		    jrc10 := jrc10 + jrc30[jrc23] * (jrc14 - jrc15);
    	end;
    	jrc16 := jrc10 / jrc12;
      jrc17 := jrc09 / jrc11 - jrc16 * jrc13;
      jrc18 := 0;
    	for jrc15 := jrc11 - 1 downto 0 do begin
    		jrc17 := jrc17 + jrc16;
        jrc23 := (jrc24+jrc15) mod 1001;
  		  jrc18 := jrc18 + abs(jrc30[jrc23] - jrc17);
    	end;
      jrc25 := 1.2 * jrc18 / jrc11;
      if (jrc11 < jrc06) then jrc25 := jrc25 * power(jrc06 / jrc11, 0.25);
      if (jrc28 = 1) then begin
        jrc28 := 0;
        jrc19 := jrc25;
      end else jrc19 := jrc19 + (jrc25 - jrc19) * jrc05;
      jrc19 := max(jrc02, jrc19);
      if (jrc29 = 1) then begin
        jrc29 := 0;
    		jrc08 := (jrc30[jrc24] - jrc30[(jrc24+jrc07) mod 1001]) / jrc07;
    	end;
      jrc21 := input1 - (jrc20 + jrc08 * jrc04);
    	jrc22 := 1 - exp(-abs(jrc21) / jrc19 / jrc03);
      jrc08 := jrc22 * jrc21 + jrc08 * jrc04;
    	jrc20 := jrc20 + jrc08;
    end;
    @Result[Bar] := jrc20;
  end;
end;

function JXVELSeries(Series: integer; DepthSeries: integer; Period: float): integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JXVEL(' + GetDescription(Series) + ',' + GetDescription(DepthSeries) + ',' + FloatToStr(Period) + ')';
  Result := FindNamedSeries( sName );
  if Result >= 0 then
    Exit;
  Result := CreateNamedSeries( sName );

  for Bar := 0 to BarCount() - 1 do
    @Result[Bar] := GetSeriesValue(Bar, JXVELaux3(JXVELaux1(Series, DepthSeries), Period));
end;

function JXVEL(Bar: integer; Series: integer; DepthSeries: integer; Period: float): float;
begin
  Result := GetSeriesValue(Bar, JXVELSeries(Series, DepthSeries, Period));
end;
