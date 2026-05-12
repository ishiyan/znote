// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JVELCFBSeries(Series: integer; LoDepth: integer; HiDepth: integer; FractalType: integer; Smooth: integer): integer;
begin
  var vl, cfb, Bar: integer;
  var sName: string;
  var sr, cfbmin, cfbmax, Value: float;

  sName := 'JVELCFB(' + GetDescription(Series) + ',' + IntToStr(LoDepth) + ',' + IntToStr(HiDepth) + ',' + IntToStr(FractalType) + ',' + IntToStr(Smooth) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then
    Exit;
  Result := CreateNamedSeries(sName);

  cfbmin := 99999;
  cfbmax := 0;
  cfb := JCFBSeries(Series, FractalType, Smooth);
  vl := CreateSeries;

  for Bar := 0 to BarCount() - 1 do
  begin
    if @cfb[Bar] > cfbmax then cfbmax := @cfb[Bar];
    if @cfb[Bar] < cfbmin then cfbmin := @cfb[Bar];
    if (cfbmax > cfbmin) then sr := (@cfb[Bar] - cfbmin) / (cfbmax - cfbmin) else sr := 0.5;
    @vl[Bar] := int(LoDepth + sr * (HiDepth - LoDepth));
  end;

  for Bar := 0 to BarCount() - 1 do
  begin
    @Result[Bar] := GetSeriesValue(Bar, JXVELaux3(JXVELaux1(Series, vl), 3));
  end;
end;

function JVELCFB(Bar: integer; Series: integer; LoDepth: integer; HiDepth: integer; FractalType: integer; Smooth: integer): float;
begin
  Result := GetSeriesValue(Bar, JVELCFBSeries(Series, LoDepth, HiDepth, FractalType, Smooth));
end;
