// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function floor(value: float): integer;
begin
  if (value = int(value)) then result := int(value) else
  if (value > 0) then result := int(value) else result := int(value)-1;
end;

function ceil(value: float): integer;
begin
  if (value = int(value)) then result := int(value) else
  if (value > 0) then result := int(value)+1 else result := int(value);
end;

function JJMASeries(Series: Integer; Len: Integer; Phase: Integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JJMA(' + GetDescription(Series) + ',' + IntToStr(Len) + ',' + IntToStr(Phase) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  var v, v1, v2, v3, v4, s8, s10, s18, s20: float;
  var i, v5, v6, s28, s30, s38, s40, s48, s50, s58, s60, s68, s70: integer;
  var f8, f10, f18, f20, f28, f30, f38, f40, f48, f50, f58, f60, f68, f70, f78, f80, f88, f90, f98, fA0, fA8, fB0, fB8, fC0, fC8, fD0: float;
  var f0, fD8, fE0, fE8, fF0, fF8: integer;
  var list: array[0..127] of float;
  var ring: array[0..127] of float;
  var ring2: array[0..10] of float;
  var buffer: array[0..61] of float;

  s28 := 63;
  s30 := 64;
  for i := 1 to s28 do
    list[i] := -1000000;
  for i := s30 to 127 do
    list[i] := 1000000;
  f0 := 1;

  if (Len <= 1) then f80 := 1.0e-10 else f80 := (Len - 1) / 2;
  if (phase < -100) then f10 := 0.5
  else if (phase > 100) then f10 := 2.5
  else f10 := phase / 100 + 1.5;

  v1 := ln(sqrt(f80));
  v2 := v1;
  if (v1 / ln(2.0) + 2 < 0) then v3 := 0 else v3 := v2 / ln(2.0) + 2;
  f98 := v3;

  if (0.5 <= f98 - 2) then f88 := f98 - 2 else f88 := 0.5;
  f78 := sqrt(f80) * f98;
  f90 := f78 / (f78 + 1);
  f80 := f80 * 0.9;
  f50 := f80 / (f80 + 2);

  for Bar := 0 to BarCount() - 1 do
  begin
    if (fF0 < 61) then begin
      fF0 := fF0 + 1;
      buffer[fF0] := @Series[Bar];
    end;
    if (fF0 > 30) then begin
      if (f0 <> 0) then begin
        f0 := 0;
        v5 := 0;
        for i := 1 to 29 do
          if (buffer[i+1] <> buffer[i]) then v5 := 1;
        fD8 := v5*30;
        if (fD8 = 0) then f38 := @Series[Bar] else f38 := buffer[1];
        f18 := f38;
        if (fD8 > 29) then fD8 := 29;
      end else
        fD8 := 0;

      for i := fD8 downto 0 do begin
        if (i = 0) then f8 := @Series[Bar] else f8 := buffer[31-i];
        f28 := f8 - f18;
        f48 := f8 - f38;
        if (abs(f28) > abs(f48)) then v2 := abs(f28) else v2 := abs(f48);
        fA0 := v2;
        v := fA0 + 1.0e-10;

        if (s48 <= 1) then s48 := 127 else s48 := s48 - 1;
        if (s50 <= 1) then s50 := 10 else s50 := s50 - 1;
        if (s70 < 128) then s70 := s70 + 1;
        s8 := s8 + v - ring2[s50];
        ring2[s50] := v;
        if (s70 > 10) then s20 := s8 / 10 else s20 := s8 / s70;

   if (s70 > 127) then begin
      s10 := ring[s48];
      ring[s48] := s20;
      s68 := 64;
      s58 := s68;
      while (s68 > 1) do begin
         if (list[s58] < s10) then begin
            s68 := s68 / 2;
            s58 := s58 + s68;
         end else
         if (list[s58] <= s10) then begin
            s68 := 1;
         end else begin
            s68 := s68 / 2;
            s58 := s58 - s68;
         end
      end
   end else begin
      ring[s48] := s20;

      if (s28 + s30 > 127) then begin
         s30 := s30 - 1;
         s58 := s30;
      end else begin
         s28 := s28 + 1;
         s58 := s28;
      end;
      if (s28 > 96) then s38 := 96 else s38 := s28;
      if (s30 < 32) then s40 := 32 else s40 := s30;
   end;
   s68 := 64;
   s60 := s68;
   while (s68 > 1) do begin
      if (list[s60] >= s20) then begin
         if (list[s60 - 1] <= s20) then begin
            s68 := 1;
         end else begin
            s68 := s68 / 2;
            s60 := s60 - s68;
         end
      end else begin
         s68 := s68 / 2;
         s60 := s60 + s68;
      end;
      if ((s60 = 127) and (s20 > list[127])) then s60 := 128;
   end;
   if (s70 > 127) then begin
      if (s58 >= s60) then begin
         if ((s38 + 1 > s60) and (s40 - 1 < s60)) then s18 := s18 + s20 else
         if ((s40 > s60) and (s40 - 1 < s58)) then s18 := s18 + list[s40 - 1];
      end else
      if (s40 >= s60) then begin
         if ((s38 + 1 < s60) and (s38 + 1 > s58)) then s18 := s18 + list[s38 + 1];
      end else
      if (s38 + 2 > s60) then s18 := s18 + s20 else
      if ((s38 + 1 < s60) and (s38 + 1 > s58)) then s18 := s18 + list[s38 + 1];

      if (s58 > s60) then begin
         if ((s40 - 1 < s58) and (s38 + 1 > s58)) then s18 := s18 - list[s58] else
         if ((s38 < s58) and (s38 + 1 > s60)) then s18 := s18 - list[s38];
      end else begin
         if ((s38 + 1 > s58) and (s40 - 1 < s58)) then s18 := s18 - list[s58] else
         if ((s40 > s58) and (s40 < s60)) then s18 := s18 - list[s40];
      end
   end;

   if (s58 <= s60) then begin
      if (s58 >= s60) then list[s60] := s20 else begin
         for i := s58 + 1 to s60 - 1 do
            list[i - 1] := list[i];
         list[s60 - 1] := s20;
      end
   end else begin
      for i := s58 - 1 downto s60 do
         list[i + 1] := list[i];
      list[s60] := s20;
   end;

   if (s70 <= 127) then begin
      s18 := 0;
      for i := s40 to s38 do
         s18 := s18 + list[i];
   end;

   f60 := s18 / (s38 - s40 + 1);

        if (fF8 + 1 > 31) then fF8 := 31 else fF8 := fF8 + 1;
        if (fF8 <= 30) then begin
          if (f28 > 0) then f18 := f8 else f18 := f8 - f28 * f90;
          if (f48 < 0) then f38 := f8 else f38 := f8 - f48 * f90;
          fB8 := @Series[Bar];
          if (fF8 <> 30) then continue;
          fC0 := @Series[Bar];

          if (ceil(f78) >= 1) then v4 := ceil(f78) else v4 := 1;
          fE8 := int(v4);
          if (floor(f78) >= 1) then v2 := floor(f78) else v2 := 1;
          fE0 := int(v2);
          if (fE8 = fE0) then f68 := 1
          else begin
            v4 := fE8 - fE0;
            f68 := (f78 - fE0) / v4;
          end;
          if (fE0 <= 29) then v5 := fE0 else v5 := 29;
          if (fE8 <= 29) then v6 := fE8 else v6 := 29;
          fA8 := (@Series[Bar] - buffer[fF0 - v5]) * (1 - f68) / fE0 + (@Series[Bar] - buffer[fF0 - v6]) * f68 / fE8;
        end else begin
          if (f98 >= power(fA0/f60, f88)) then v1 := power(fA0/f60, f88) else v1 := f98;
          if (v1 < 1) then v2 := 1.0
          else begin
            if (f98 >= power(fA0/f60, f88)) then v3 := power(fA0/f60, f88) else v3 := f98;
            v2 := v3;
          end;
          f58 := v2;
          f70 := power(f90, sqrt(f58));
          if (f28 > 0) then f18 := f8 else f18 := f8 - f28 * f70;
          if (f48 < 0) then f38 := f8 else f38 := f8 - f48 * f70;
        end;
      end;

      if (fF8 > 30) then begin
        f30 := power(f50, f58);
        fC0 := (1 - f30) * @Series[Bar] + f30 * fC0;
        fC8 := (@Series[Bar] - fC0) * (1 - f50) + f50 * fC8;
        fD0 := f10 * fC8 + fC0;
        f20 := f30 * -2;
        f40 := f30 * f30;
        fB0 := f20 + f40 + 1;
        fA8 := (fD0 - fB8) * fB0 + f40 * fA8;
        fB8 := fB8 + fA8;
      end;
    end;

    Value := fB8;
    SetSeriesValue(Bar, Result, Value);
  end;
end;

function JJMA(Bar: integer; Series: Integer; Len: Integer; Phase: Integer): float;
begin
  Result := GetSeriesValue(Bar, JJMASeries(Series, Len, Phase));
end;
