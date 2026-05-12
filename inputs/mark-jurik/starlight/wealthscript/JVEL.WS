// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JVELaux1(Series: integer; Depth: integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var jrc04, jrc05, jrc06, jrc07, jrc08, jrc09: float;
  var jrc01, jrc02, jrc10: integer;

  sName := 'JVELaux1(' + GetDescription(Series) + ',' + FloatToStr(Depth) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  jrc01 := Series;
  jrc02 := Depth;
  jrc04 := jrc02 + 1;
  jrc05 := jrc04 * (jrc04+1) / 2;
  jrc06 := jrc05 * (2*jrc04+1) / 3;
  jrc07 := jrc05 * jrc05 * jrc05 - jrc06 * jrc06;
  for Bar := jrc02 to BarCount() - 1 do
  begin
    jrc08 := 0;
    jrc09 := 0;
    for jrc10 := 0 to jrc02 do
    begin
      jrc08 := jrc08 + @jrc01[Bar-jrc10] * (jrc04 - jrc10);
      jrc09 := jrc09 + @jrc01[Bar-jrc10] * (jrc04 - jrc10) * (jrc04 - jrc10);
    end;
    @Result[Bar] := (jrc09*jrc05 - jrc08*jrc06) / jrc07;
  end;
end;

function JVELaux3(Series: integer): integer;
begin
  var Bar: integer;
  var sName: string;

  sName := 'JVELaux3(' + GetDescription(Series) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  var JR02, JR04, JR05, JR08, JR09, JR10, JR12, JR13, JR14, JR16, JR17, JR19, JR20, JR22, JR23, JR28: float;
  var JR01, JR03, JR06, JR07, JR11, JR15, JR18, JR24, JR25, JR26, JR27, JR29: integer;
  var JR21, JR21a, JR21b: float;
  var JR40, JR41 : array[0..99] of float;

  JR01 := 30;
  JR02 := 0.0001;

  for Bar := JR01 to BarCount() - 1 do
  begin
    JR27 := Bar;
    If Bar = JR01 then begin
	    JR28 := 0;
    	for JR29 := 1 to JR01-1 do
      	if @Series[Bar-JR29] = @Series[Bar-JR29-1] then JR28 := JR28 + 1;
      if JR28 < (JR01-1) then JR26 := JR27-JR01 else JR26 := JR27;
    	JR18 := 0;
    	JR25 := 0;
    	JR21 := @Series[Bar-1];
    	JR03 := 3;
    	JR04 := 0.86 - 0.55 / sqrt(JR03);
    	JR05 := 1 - exp(-ln(4) / JR03);
    	JR06 := JR01+1;
    	JR07 := 3;
    	JR08 := (@Series[Bar] - @Series[Bar-JR07]) / JR07;
    	JR11 := Int(min(1+JR27-JR26, JR06));
    	for JR15 := JR11-1 downto 1 do begin
    		if JR25 <= 0 then JR25 := 100;
    		JR25 := JR25-1;
    		JR41[JR25] := @Series[Bar-JR15];
    	end;
    end;
    If JR25 <= 0 then JR25 := 100;
    JR25 := JR25-1;
    JR41[JR25] := @Series[Bar];
    if JR11 <= JR01 then begin
    	if Bar = JR01 then JR21 := @Series[Bar] else JR21 := sqrt(JR05)*@Series[Bar] + (1-sqrt(JR05))*JR21a;
    	if Bar > JR01+1 then JR08 := (JR21 - JR21b)/2 else JR08 := 0;
      JR11 := JR11 + 1;
    end else begin
    	If JR11 <= JR06 then begin
    		JR12 := JR11 * (JR11+1) * (JR11-1) / 12;
    		JR13 := (JR11+1)/2;
		    JR14 := (JR11-1)/2;
    		JR09 := 0;
		    JR10 := 0;
    		for JR15 := JR11-1 downto 0 do begin
		    	JR24 := (JR25+JR15) mod 100;
    			JR09 := JR09 + JR41[JR24];
		    	JR10 := JR10 + JR41[JR24]*(JR14 - JR15);
    		end;
    		JR16 := JR10/JR12;
		    JR17 := (JR09/JR11) - (JR16*JR13);
    		JR19 := 0;
		    for JR15 := JR11-1 downto 0 do begin
    			JR17 := JR17+JR16;
		    	JR24 := (JR25+JR15) mod 100;
    			JR40[JR15] := abs(JR41[JR24]-JR17);
		    	JR19 := JR19 + JR40[JR15];
    		end;
    		JR20 := (JR19/JR11) * power(JR06/JR11, 0.25);
		    JR11 := JR11+1;
    	end else begin
    		if (Bar mod 1000)=0 then begin
		    	JR09 := 0;
    			JR10 := 0;
		    	for JR15 := JR06-1 downto 0 do begin
				    JR24 := (JR25+JR15) mod 100;
    				JR09 := JR09 + JR41[JR24];
		    		JR10 := JR10 + JR41[JR24]*(JR14 - JR15);
    			end;
		    end else begin
    			JR24 := (JR25+JR06) mod 100;
		    	JR10 := JR10 - JR09 + JR41[JR24]*JR13 + @Series[Bar]*JR14;
    			JR09 := JR09 - JR41[JR24] + @Series[Bar];
		    end;
    		if JR18 <= 0 then JR18 := JR06;
    		JR18 := JR18 - 1;
		    JR19 := JR19 - JR40[JR18];
    		JR16 := JR10/JR12;
		    JR17 := (JR09/JR06) + (JR16*JR14);
    		JR40[JR18] := abs(@Series[Bar]-JR17);
		    JR19 := max(JR02, (JR19 + JR40[JR18]));
    		JR20 := JR20 + ((JR19/JR06) - JR20) * JR05;
    	end;
    	JR20 := max(JR02, JR20);
    	JR22 := @Series[Bar] - (JR21 + JR08*JR04);
    	JR23 := 1-exp(-abs(JR22)/JR20/JR03);
    	JR08 := JR23*JR22 + JR08*JR04;
    	JR21 := JR21 + JR08;
    end;
    JR21b := JR21a; JR21a := JR21;
    @Result[Bar] := JR21;
  end;
end;

function JVELSeries(Series: integer; Depth: integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JVEL(' + GetDescription( Series ) + ',' + FloatToStr( Depth ) + ')';
  Result := FindNamedSeries( sName );
  if Result >= 0 then
    Exit;
  Result := CreateNamedSeries( sName );

  for Bar := 0 to BarCount() - 1 do
    @Result[Bar] := GetSeriesValue(Bar, JVELaux3(JVELaux1(Series, Depth)));
end;

function JVEL(Bar: integer; Series: Integer; Depth: Integer): float;
begin
  Result := GetSeriesValue(Bar, JVELSeries(Series, Depth));
end;
