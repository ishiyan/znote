
using System;
using System.Linq;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
 
/*           Butterworth band stop filter          */
/*              www.mosismath.com                  */


namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {
        public int order = 3;

        public const int datapoints = 1000; // number of datapoints for the interpolation
        double f = 20.0;
        double fs = 10000.0;
        double fc = 500.0;
        double fg = 100.0;

        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];

        public double[] za;
        public double[] zb;

        class TButterworth
        {
            int order;
            public double[] a_z;
            public double[] b_z;
            private double[] a_s = { 1.0 };
            private double[] b_s = { 1.0 };
            private double tc = 1.0;
            double deltaOmeaga;

            public TButterworth(int iOrder, double dFcut, double dFs, double dFgap)
            {
                order = iOrder;
                tc = 2.0 * Math.PI * dFcut / dFs;
                deltaOmeaga = dFgap / Math.Sqrt((dFcut - dFgap / 2) * (dFcut + dFgap / 2));
                a_z = new double[order + 1];
                b_z = new double[1];
            }


            public void CalcButterworth(int order)
            {
                int i = 1;
                double[] poly = new double[3];
                double[] poly2 = new double[2];
                poly[0] = 1.0;

                if (order % 2 == 0)
                {
                    poly[2] = 1.0;
                    for (i = 1; i <= order / 2; i++)
                    {
                        poly[1] = 2.0 * Math.Cos((2 * i - 1) * Math.PI / 2 / order);
                        a_s = Poly.Mult(a_s, poly);
                    }
                }
                else
                {
                    poly2[0] = 1.0;
                    poly2[1] = 1.0;
                    a_s = Poly.Mult(a_s, poly2);
                    poly[2] = 1.0;
                    for (i = 2; i <= (order + 1) / 2; i++)
                    {
                        poly[1] = 2.0 * Math.Cos((i - 1) * Math.PI / order);
                        a_s = Poly.Mult(a_s, poly);
                    }
                }
            }

            public void BandFilterTransformation()
            {
                int i, j;
                double[] tempA = { 1.0 , 0.0, 1.0 }; // s^2 + 1
                double[] tempB = { deltaOmeaga, 0.0 };   // s * deltaQ
                
                List<double[]> bandPar = new List<double[]>();
                for (i = 0; i <= order; i++)
                {
                    double[] tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempB, order - i));
                    tempEl = Poly.Mult(tempEl, a_s[i]);
                    bandPar.Insert(i, tempEl);
                }
                Array.Resize(ref  a_s, bandPar.ElementAt(bandPar.Count-1).Length);
                for (i = 0; i < a_s.Length; i++)
                {
                    a_s[a_s.Length - 1 - i] = 0;
                    for (j = 0; j < bandPar.Count; j++)
                    {
                        if(i < bandPar.ElementAt(j).Length)
                          a_s[a_s.Length - 1 - i] = a_s[a_s.Length - 1 - i] + bandPar.ElementAt(j)[bandPar.ElementAt(j).Length - 1 - i];
                    }
                }
                b_s = Poly.Power(tempA,  order);
            }

            
            public void TransformToZPlane()
            {
                int i, j;
                double[] tempA = new double[2];
                List<double[]> aa = new List<double[]>();
                List<double[]> bb = new List<double[]>();

                for (i = 0; i < a_s.Length; i++)
                {
                    aa.Add(new double[] { 1, -1 });
                }
                for (i = 0; i < b_s.Length; i++)
                {
                    bb.Add(new double[] { 1, -1 });
                }
                tempA[0] = 1; 
                tempA[1] = 1;
                for (i = 0; i < a_s.Length; i++)
                {
                    double[] tempEl = aa.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, a_s.Length - 1 - i));
                    tempEl = Poly.Mult(tempEl, a_s[i] * Math.Pow(2.0 / tc, a_s.Length - 1 - i));
                    aa.RemoveAt(i);
                    aa.Insert(i, tempEl);
                }

                for (i = 0; i < b_s.Length; i++)
                {
                    double[] tempEl = bb.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, b_s.Length - 1 - i));
                    tempEl = Poly.Mult(tempEl, b_s[i] * Math.Pow(2.0 / tc, b_s.Length - 1 - i));
                    bb.RemoveAt(i);
                    bb.Insert(i, tempEl);
                }

                a_z = new double[aa.Count];
                for (i = 0; i < a_z.Length; i++)
                {
                    a_z[i] = 0;
                    for (j = 0; j < aa.Count; j++)
                        a_z[i] = a_z[i] + aa.ElementAt(j)[i];
                }

                b_z = new double[bb.Count];
                for (i = 0; i < b_z.Length; i++)
                {
                    b_z[i] = 0;
                    for (j = 0; j < bb.Count; j++)
                        b_z[i] = b_z[i] + bb.ElementAt(j)[i];
                }

                for (i =0; i < b_z.Length; i++)
                {
                    b_z[i] = b_z[i] / a_z[0];
                }
                for (i = a_z.Length-1; i >= 0; i--)
                {
                    a_z[i] = a_z[i] / a_z[0];
                }       
            }
        }

      

        public MainWin()
        {       
            InitializeComponent();
            tbSampleF.Text = Math.Round(fs, 1).ToString();
            tbCutoffF.Text = Math.Round(fc, 1).ToString();
            tbSign.Text = Math.Round(f, 1).ToString();
            tbGap.Text = Math.Round(fg, 1).ToString();
        }

 
        public void DrawGraph(int maxPoints, double minX, double maxX, bool doClear)
        {
            Point p1, p2;
            int j;
            double maxTime = -1.0;
            double maxVal = -1.0;
            double minVal = 1.0;
            double scalefactor;
            bool drawCeroline;
            for (j = 0; j < maxPoints - 1; j++)
            {
                if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                {
                    if (maxTime < t_in[j])
                        maxTime = t_in[j];
                    if (maxVal < y_in[j])
                        maxVal = y_in[j];
                    if (minVal > y_in[j])
                        minVal = y_in[j];
                }
            }
            maxTime = maxTime * 1.05;
            maxTime = maxTime * 1.05;
            if (minVal < 0)
            {
                if (maxVal > 0)
                {
                    if (maxVal > Math.Abs(minVal))
                        scalefactor = pGraph.Height / maxVal / 2.2;
                    else
                        scalefactor = pGraph.Height / Math.Abs(minVal) / 2.2;
                }
                else
                    scalefactor = 5.0;
                drawCeroline = true;
            }
            else
            {
                scalefactor = pGraph.Height / (maxVal) / 1.1;
                drawCeroline = false;
            }
            p1 = new Point();
            p2 = new Point();
            Graphics g = pGraph.CreateGraphics();
            if (doClear)
                g.Clear(Color.White);
            Pen bluePen = new Pen(Color.Blue, 2);
            Pen redPen = new Pen(Color.Red, 2);
            Pen blackPen = new Pen(Color.Black, 2);
            if (drawCeroline)
            {
                p1.X = 0;
                p1.Y = (pGraph.Height / 2);
                p2.X = pGraph.Width;
                p2.Y = (pGraph.Height / 2);
                g.DrawLine(blackPen, p1, p2);
            }
            bluePen.Width = 1;
            if (maxTime > 0) // draw interpolated graph
            {
                for (j = 0; j < maxPoints - 1; j++)
                {
                    if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                    {
                        p1.X = Convert.ToInt32(t_in[j] * pGraph.Width / (double)maxTime);
                        p2.X = Convert.ToInt32(t_in[j + 1] * pGraph.Width / (double)maxTime);
                        if (drawCeroline)
                        {
                            p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_in[j] * scalefactor));
                            p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_in[j + 1] * scalefactor));
                        }
                        else
                        {
                            p1.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_in[j] * scalefactor));
                            p2.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_in[j + 1] * scalefactor));
                        }
                       // if (p2.X > p1.X)
                            g.DrawLine(redPen, p1, p2);
                    }
                }

                for (j = 0; j < maxPoints - 1; j++)
                {
                    if ((t_in[j] >= minX) && (t_in[j] <= maxX))
                    {
                        p1.X = Convert.ToInt32(t_in[j] * pGraph.Width / (double)maxTime);
                        p2.X = Convert.ToInt32(t_in[j + 1] * pGraph.Width / (double)maxTime);
                        if (drawCeroline)
                        {
                            p1.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_out[j] * scalefactor));
                            p2.Y = (pGraph.Height / 2) - Convert.ToInt32(Math.Round(y_out[j + 1] * scalefactor));
                        }
                        else
                        {
                            p1.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_out[j] * scalefactor));
                            p2.Y = (pGraph.Height) - Convert.ToInt32(Math.Round(y_out[j + 1] * scalefactor));
                        }
                       // if (p2.X > p1.X)
                            g.DrawLine(bluePen, p1, p2);
                    }
                }
            }
            g.Dispose();
        }


        private void button1_Click(object sender, EventArgs e)
        {
            int i, j;
          
            try
            {
                fs = Convert.ToDouble(tbSampleF.Text);
                fc = Convert.ToDouble(tbCutoffF.Text);
                f = Convert.ToDouble(tbSign.Text);
                fg = Convert.ToDouble(tbGap.Text);
                if (fc > fs)
                {
                    MessageBox.Show("Cut off frequency must be smaller then sample frequency!");
                    fc = fs;
                    tbCutoffF.Text = Math.Round(fc, 1).ToString();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            TButterworth butter = new TButterworth(order, fc, fs, fg);

            butter.CalcButterworth(order);
            butter.BandFilterTransformation();
            butter.TransformToZPlane();
            za = butter.a_z;
            zb = butter.b_z;

            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            for (i = 0; i < za.Length; i++)
            {
                y_out[i] = 0;
                for (j = 0; j <= i; j++)
                {
                    y_out[i] = y_out[i] + y_in[i - j] * zb[j] * (i/ za.Length);
                }
                for (j = 1; j <= i; j++)
                {
                    y_out[i] = y_out[i] - y_out[i - j] * za[j] * (i / za.Length);
                }
            }

            for (i = za.Length + 1; i < datapoints; i++)
            {
                y_out[i] = 0;
                for (j = 0; j < zb.Length; j++)
                {
                    y_out[i] = y_out[i] + y_in[i - j] * zb[j];
                }
                for (j = 1; j < za.Length; j++)
                {
                    y_out[i] = y_out[i] - y_out[i - j] * za[j];
                }
            }
            DrawGraph(datapoints, 0, t_in[datapoints - 1], true);
        }

        private void pGraph_Paint(object sender, PaintEventArgs e)
        {
           DrawGraph(datapoints, 0, t_in[datapoints - 1], false);
        }  
    }
}
