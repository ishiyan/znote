// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JTPOSeries(Series: Integer; Len: Integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JTPO(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then
    Exit;
  Result := CreateNamedSeries(sName);

  var f0, f8, f10, f18, f20, f28: float;
  var f30, f38, f40, f48: integer;
  var var6, varA, varE, var12, var14: integer;
  var var18, var1C, var20, var24: float;
  var arr0, arr1, arr2, arr3: array[0..300] of float;

  for Bar := 0 to BarCount() - 1 do
  begin

   var14 := 0;
   var1C := 0;
   if (f38 = 0) then begin
      f38 := 1;
      f40 := 0;
      if (Len-1 >= 2) then f30 := Len-1 else f30 := 2;
      f48 := f30 + 1;
      f10 := @Series[Bar];
      arr0[f38] := @Series[Bar];
      f18 := 12 / (f48 * (f48 - 1) * (f48 + 1));
      f20 := (f48 + 1) * 0.5;
   end else begin
     if (f38 <= f48) then f38 := f38 + 1 else f38 := f48 + 1;
     f8 := f10;
     f10 := @Series[Bar];
     if (f38 > f48) then begin
        for var6 := 2 to f48 do
           arr0[var6 - 1] := arr0[var6];
        arr0[f48] := @Series[Bar];
     end else
        arr0[f38] := @Series[Bar];
     if ((f30 >= f38) and (f8 <> f10)) then f40 := 1;
     if ((f30 = f38) and (f40 = 0)) then f38 := 0;
   end;
   if (f38 >= f48) then begin
      for varA := 1 to f48 do begin
         arr2[varA] := varA;
         arr3[varA] := varA;
         arr1[varA] := arr0[varA];
      end;
      for varA := 1 to f48-1 do begin
         var24 := arr1[varA];
         var12 := varA;
         var6 := varA + 1;
         for var6 := varA + 1 to f48 do
            if (arr1[var6] < var24) then begin
               var24 := arr1[var6];
               var12 := var6;
            end;
         var20 := arr1[varA];
         arr1[varA] := arr1[var12];
         arr1[var12] := var20;
         var20 := arr2[varA];
         arr2[varA] := arr2[var12];
         arr2[var12] := var20;
      end;
      varA := 1;
      while (f48 > varA) do begin
         var6 := varA + 1;
         var14 := 1;
         var1C := arr3[varA];
         while (var14 <> 0) do begin
            if (arr1[varA] <> arr1[var6]) then begin
               if (var6 - varA > 1) then begin
                  var1C := var1C / (var6 - varA);
                  varE := varA;
                  for varE := varA to var6-1 do
                     arr3[varE] := var1C;
               end;
               var14 := 0;
            end else begin
               var1C := var1C + arr3[var6];
               var6 := var6 + 1;
            end;
         end;
         varA := var6;
      end;
      var1C := 0;
      for varA := 1 to f48 do
         var1C := var1C + (arr3[varA] - f20) * (arr2[varA] - f20);
      var18 := f18 * var1C;
   end else
      var18 := 0;

    Value := var18;
    @Result[Bar] := Value;
  end;
end;

function JTPO(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, JTPOSeries(Series, Len));
end;

