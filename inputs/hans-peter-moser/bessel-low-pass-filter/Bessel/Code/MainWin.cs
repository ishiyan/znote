
using System;
using System.Linq;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

/*                          Digital Bessel filter                           */
/*                           www.mosismath.com                              */


namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {
        public int order = 4;
        public const int datapoints = 500; // number of datapoints for the interpolation

        double f = 20.0;
        double fs = 10000.0;
        double fc = 300.0;

        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];

        public double[] a;
        public double[] b;

        class TBessel
        {
            private int order;
            public double[] a_z;
            public double[] b_z;
            private double tc = 1.0;
            private double[] a_s = new double[2];

            public TBessel(int iOrder, double dTc)
            {
                double[] correctT = { 1.0, 0.7344, 0.56958, 0.47306, 0.41196, 0.36991, 0.33878, 0.3145 };
                
                order = iOrder;

                if ((order > 0) && (order <= 8))
                {
                    double c = correctT[(order - 1)];
                    tc = dTc * c;
                }
                else
                    throw new Exception("Order too high"); 
                a_z = new double[order + 1];
                b_z = new double[1];
            }

            private double Fact(double value)
            {
                int i;
                double res = 1;
                if (value != 0)
                {
                    for (i = (int)(Math.Round(value)); i > 0; i--)
                    {
                        res = res * value;
                        value--;
                    }
                }
                return res;
            }

            public void CalcBesselPolynom(int n)
            {
                int i;
                
                a_s = new double[n+1];
                for(i = 0; i <= n; i++)
                {
                    a_s[n - i] = Fact(2 * n - i) / Math.Pow(2.0, n - i) / Fact(n - i) / Fact(i);
                }
                for (i = 0; i <= n ; i++)
                {
                    a_s[i] = a_s[i] / a_s[n];
                }
            }

            public void TransformToZPlane()
            {
                int i, j;
                double[] tempA = new double[2];
                List<double[]> aa = new List<double[]>();
                for (i = 0; i <= order; i++)
                {
                    aa.Add(new double[] { 1, -1 });
                }
                tempA[0] = 1;
                tempA[1] = 1;
                b_z = Poly.Power(tempA, order);
                for (i = 0; i <= order; i++)
                {
                    double[] tempEl = aa.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, order - i));
                    tempEl = Poly.Mult(tempEl, a_s[i] * Math.Pow(2.0 / tc, order - i));
                    aa.RemoveAt(i);
                    aa.Insert(i, tempEl);
                }
                for (i = 0; i <= order; i++)
                {
                    a_z[i] = 0;
                    for (j = 0; j <= aa.Count-1; j++)
                        a_z[i] = a_z[i] + aa.ElementAt(j)[i];
                }
                for (i = 0; i < b_z.Length; i++)
                {
                    b_z[i] = b_z[i] / a_z[0];
                }
                for (i = order; i >= 0; i--)
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
                        if (p2.X > p1.X)
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
                        if (p2.X > p1.X)
                            g.DrawLine(bluePen, p1, p2);
                    }
                }
            }
            g.Dispose();
        }


        private void button1_Click(object sender, EventArgs e)
        {
            int i, j;
            double t;
            
            try
            {
                fs = Convert.ToDouble(tbSampleF.Text);
                fc = Convert.ToDouble(tbCutoffF.Text);
                f = Convert.ToDouble(tbSign.Text);
                if (fc > fs)
                {
                    MessageBox.Show("Cut off frequency must be smaller then sample frequency!");
                    fc = fs;
                    tbCutoffF.Text = Math.Round(fc, 1).ToString();
                }
            }
            catch(Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            t = 2.0 * Math.PI * fc / fs;
            TBessel bessel = new TBessel(order, t);

            bessel.CalcBesselPolynom(order);
            bessel.TransformToZPlane();

            a = bessel.a_z;
            b = bessel.b_z;

            // create a sample signal
            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }

            // the first n elements are different 
            for (i = 0; i < order; i++)
            {
                y_out[i] = 0;
                for (j = 0; j <= i; j++)
                {
                    y_out[i] = y_out[i] + y_in[i-j] * b[j];
                }
                for (j = 1; j <= i; j++)
                {
                    y_out[i] = y_out[i] - y_out[i-j] * a[j];
                }
            }

            // calculate filtered data
            for (i = a.Length; i < datapoints; i++)
            {
                y_out[i] = 0;
                for (j = 0; j < b.Length; j++)
                {
                    y_out[i] = y_out[i] + y_in[i - j] * b[j];
                }
                for (j = 1; j < a.Length; j++)
                {
                    y_out[i] = y_out[i] - y_out[i - j] * a[j];
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
