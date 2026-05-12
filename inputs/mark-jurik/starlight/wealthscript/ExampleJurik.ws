{
  Created by Starlight (extesy@yandex.ru).
  Compiled into dll by _landy

  Перед началом работы dll необходимо зарегистрировать в системе командой:
  regsvr32 jurik.dll
  Если этого не сделать, будет выдаваться сообщение об ошибке "Invalid class string"

  jurik.dll экспортирует следующий интерфейс:

type
  TIndicator = class(TAutoObject, IIndicator)
  protected
    procedure JJMA(ADestSeries, ASourceSeries, ALength, APhase: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JCFB(ADestSeries, ASourceSeries, AFractalType, ASmooth: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JCCX(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JARSX(ADestSeries, ASourceSeries, ALoLen, AHiLen,
      ASensitivity: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JTPO(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JRSX(ADestSeries, ASourceSeries, ALength: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMX(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXM(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JDMXP(ADestSeries, ASourceSeries, ALen: Integer;
      const AWL: IWealthLabAddOn3); safecall;
    procedure JAVEL(ADestSeries, ASourceSeries, ALoLen, AHiLen, ASensitivity,
      APeriod: Integer; const AWL: IWealthLabAddOn3); safecall;
    procedure JVEL(ADestSeries, ASourceSeries, ADepth: Integer;
      const AWL: IWealthLabAddOn3); safecall;
  end;

  Пример использования в скрипте:

var lib: ComVariant;
var hhPanel: Integer;

begin
  lib := CreateOleObject('Jurik.Indicator');   // Создаем OLE-объект Jurik.Indicator

   // Строим индикатор JAVEL на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);                 // Создаем панель
  h2 := CreateSeries;                                     // Пустая серия для значений индикатора
  lib.JAVEL (h2, #Close, 14, 14, 2, 2, IWealthLabAuto);   // Вычисляем
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JAVEL');    // Рисуем
end;
}

var lib: ComVariant;
var h1, h2, h3, h4, hPanel: Integer;

begin
  lib := CreateOleObject('Jurik.Indicator');   // Создаем OLE-объект Jurik.Indicator
  
   // Строим 2 JJMA на графика котировок
  h1 := CreateSeries;
  lib.JJMA (h1, #Close, 24, 0, IWealthLabAuto);
  PlotSeries (h1, 0, #Red, #Thin);

  h1 := CreateSeries;
  lib.JJMA (h1, #Close, 12, 0, IWealthLabAuto);
  PlotSeries (h1, 0, #Blue, #Thin);

   // Строим JCFB во всех четырех вариантах на панели вверху графика котировок
  hPanel := CreatePane (60, true, true);

  h2 := CreateSeries;
  lib.JCFB (h2, #Close, 1, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JCFB');

  h2 := CreateSeries;
  lib.JCFB (h2, #Close, 2, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Red, #Thin);

  h2 := CreateSeries;
  lib.JCFB (h2, #Close, 3, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Green, #Thin);

  h2 := CreateSeries;
  lib.JCFB (h2, #Close, 4, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Black, #Thin);

   // Строим JVELCFB во всех четырех вариантах на панели вверху графика котировок
  hPanel := CreatePane (60, true, true);

  h2 := CreateSeries;
  lib.JVELCFB (h2, #Close, 5, 26, 1, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JCFB');

  h2 := CreateSeries;
  lib.JVELCFB (h2, #Close, 5, 26, 2, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Red, #Thin);

  h2 := CreateSeries;
  lib.JVELCFB (h2, #Close, 5, 26, 3, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Green, #Thin);

  h2 := CreateSeries;
  lib.JVELCFB (h2, #Close, 5, 26, 4, 14, IWealthLabAuto);
  PlotSeries (h2, hPanel, #Black, #Thin);

   // Строим JCCX на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JCCX (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JCCX');

   // Строим JTPO на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JTPO (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Gray, #Thin, 'JTPO');

   // Строим JARSX и JRSX на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JARSX (h2, #Close, 5, 14, 5, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Green, #Thin, 'JARSX');
  h2 := CreateSeries;
  lib.JRSX (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JRSX');
  
   // Строим JDMX на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JDMX (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JDMX');

  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JDMXP (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Red, #Thin, 'JDMX+');
  h2 := CreateSeries;
  lib.JDMXM (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Green, #Thin, 'JDMX-');

   // Строим JAVEL на панели внизу графика котировок
  hPanel := CreatePane (60, false, true);
  h2 := CreateSeries;
  lib.JAVEL (h2, #Close, 10, 14, 2, 2, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Blue, #Thin, 'JAVEL');

  h2 := CreateSeries;
  lib.JVEL (h2, #Close, 14, IWealthLabAuto);
  PlotSeriesLabel (h2, hPanel, #Red, #Thin, 'JVEL');
end;