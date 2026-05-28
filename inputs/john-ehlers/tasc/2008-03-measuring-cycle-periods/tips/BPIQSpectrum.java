SpectrumDSRenderer.java
package com.iqpartners.chart.render;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Color;
import com.iqpartners.data.DataSet;
public class SpectrumDSRenderer extends DataSetRenderer {
    /** Constructor */
    public SpectrumDSRenderer() {
    }
    /**
     * Draw a histogram
     */
    @Override
    public void plot(RendererContext rc, DataSet dsRed, DataSet dsGreen, Graphics g) {
        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        Float[] red = dsRed.getData();
        Float[] green = dsGreen.getData();
        for (int i = 0; i = 1) {
                    tickVal = 0;
                    label = "0";
                    g.setColor(ColorSchemeManager.current().label());
                    g.drawString(label, rc.getXMax() + fontDelta + 1, rc.getY(tickVal) + fontDelta);
                    g.setColor(ColorSchemeManager.current().grid());
                    g.drawLine(rc.getXMin(), rc.getY(tickVal), rc.getXMax() - 3, rc.getY(tickVal));
                    int step = (int) (r.getHigh() / 3) + 1;
                    for (int i = step; i  0.5) ? 0.2F : 0.1F;
                    for (float i = step; i  5) {
                for (int n = 8; n  MaxAmpl) {
                    MaxAmpl = Ampl[n];
                }
            }
            for (int n = 8; n  0)) {
                    DB[n] = (float) (-10.0 * Math.log(0.01 / (1 - 0.99 * Ampl[n] / MaxAmpl)) / Math.log(10));
                } else {
                    DB[n] = 0.0f;
                }
                if (DB[n] > 20) {
                    DB[n] = 20.0f;
                }
            }
            float Num = 0.0f;
            float Denom = 0.0f;
            for (int n = 8; n <= 50; n++) {
                if (DB[n] <= 3) {
                    Num = Num + n * (20 - DB[n]);
                    Denom = Denom + (20 - DB[n]);
                }
                if (Denom != 0.0f) {
                    DC.addFloat(Num / Denom, i);
                }
            }
            for (int n = 8; n <= 50; n++) {
                if (DB[n] <= 10) {
                    Color1[n].addFloat(255.0f, i);
                    float color = 255 * (1 - DB[n] / 10);
                    Color2[n].addFloat(color, i);
                } else {
                    float color = 255 * (2 - DB[n] / 10);
                    Color1[n].addFloat(color, i);
                    Color2[n].addFloat(0.0f, i);
                }
            }
        }
        DataSet DomCyc = DataSet.SMA(DC, 10);
        for (int n = 8; n <= 50; n++) {
            Color1[n].setLevel(n);
            Color1[n].setDataSetRenderer(new SpectrumDSRenderer());
            addDataSetPair("DS_" + Integer.toString(n), Color1[n], Color2[n]);
        }
        calculateHigh();
        calculateLow();
    }
    @Override
    public void calculateHigh() {
        high = 50;
    }
    @Override
    public void calculateLow() {
        low = 8;
    }
    public String getOverlayName() {
        // Initiliaze localization
        ResourceBundle messages;
        TranslatedMessages translatedMessages = TranslatedMessages.instance();
        messages = translatedMessages.getBundle();
        return messages.getString("bp_iq_spectrum");
    }
}