
using System;
using System.Linq;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

/*             Digital high and low pass Shelving filter              */
/*                          www.mosismath.com                         */

namespace WindowsFormsApplication1
{

    public partial class MainWin : Form
    {
        public int N = 3;  // filter order N
        public const int datapoints = 500; // number of datapoints for the interpolation
        double f = 90.0;              // signal frequency 
        public double fs = 10000.0;   // sampling frequency
        public double fc = 300.0;     // cut off frequency
        double G = 1.3;               // amplification

        double[] t_in = new double[datapoints];
        double[] y_in = new double[datapoints];
        double[] y_out = new double[datapoints];

        public double[] a;
        public double[] b;

        class TShelving
        {
            int order;
            public double[] a_z;
            public double[] b_z;
            public double[] a_s;
            public double[] b_s;
            double wc = 1.0;

            public TShelving(int iOrder, double dWc)
            {
                order = iOrder;
                wc = dWc;
                a_z = new double[order + 1];
                b_z = new double[1];
            }


            public void CalcShelving(double amp, bool bHighPass)
            {
                int i = 1;
     
               
                a_s = new double[1];
                b_s = new double[1];
                double[] poly = new double[3];
                double gl = Math.Pow(amp, 1.0 / order);
                double tempD;
                
                if (order % 2 == 0) // order is even
                {
                    a_s = new double[1];
                    b_s = new double[1];
                    b_s[0] = 1.0;
                    a_s[0] = 1.0;
                    for (i = 1; i < order; i += 2)
                    {
                        poly[0] = 1.0;
                        poly[1] = 2.0 * Math.Cos(Math.PI * i / 2.0 / order) * gl;
                        poly[2] = gl * gl;
                        b_s = Poly.Mult(b_s, poly);

                        poly[0] = 1.0;
                        poly[1] = 2.0 * Math.Cos(Math.PI * i / 2.0 / order);
                        poly[2] = 1.0;
                        a_s = Poly.Mult(a_s, poly);
                    }
                }
                else // order is odd
                {
                    a_s = new double[2];
                    b_s = new double[2];
                    b_s[0] = 1.0;
                    b_s[1] = gl;
                    a_s[0] = 1.0;
                    a_s[1] = 1.0;
                    for (i = 2; i < order; i += 2)
                    {
                        poly[0] = 1.0;
                        poly[1] = 2.0 * Math.Cos(Math.PI * i / 2.0 / order) * gl;
                        poly[2] = gl * gl;
                        b_s = Poly.Mult(b_s, poly);

                        poly[0] = 1.0;
                        poly[1] = 2.0 * Math.Cos(Math.PI * i / 2.0 / order);
                        poly[2] = 1.0;
                        a_s = Poly.Mult(a_s, poly);
                    }
                }

                if(!bHighPass)
                {
                    for(i=0; i < a_s.Length/2; i++)
                    {
                        tempD = a_s[i];
                        a_s[i] = a_s[a_s.Length - 1 - i];
                        a_s[a_s.Length - 1 - i] = tempD;
                    }

                    for (i = 0; i < b_s.Length / 2; i++)
                    {
                        tempD = b_s[i];
                        b_s[i] = b_s[b_s.Length - 1 - i];
                        b_s[a_s.Length - 1 - i] = tempD;
                    }
                }
            }


            public void TransformToZPlane()
            {
                int i, j;
                List<double[]> aa = new List<double[]>();
                List<double[]> bb = new List<double[]>();
                double[] tempA = { 1.0, 1.0 };
                tempA[0] = 1;
                tempA[1] = 1;

                for (i = 0; i < a_s.Length; i++)
                {
                    aa.Add(new double[] { 1.0, -1.0 });
                    bb.Add(new double[] { 1.0, -1.0 });
                }

                for (i = 0; i < a_s.Length; i++)
                {
                    double[] tempEl = aa.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, a_s.Length - 1 - i));
                    tempEl = Poly.Mult(tempEl, a_s[i] * Math.Pow(2.0 / wc, a_s.Length - 1 - i));
                    aa.RemoveAt(i);
                    aa.Insert(i, tempEl);
                }

                for (i = 0; i < b_s.Length; i++)
                {
                    double[] tempEl = bb.ElementAt(i);
                    tempEl = Poly.Mult(Poly.Power(tempA, i), Poly.Power(tempEl, b_s.Length - 1 - i));
                    tempEl = Poly.Mult(tempEl, b_s[i] * Math.Pow(2.0 / wc, b_s.Length - 1 - i));
                    bb.RemoveAt(i);
                    bb.Insert(i, tempEl);
                }

                a_z = new double[aa.Count];
                for (i = 0; i < a_z.Length; i++)
                {
                    a_z[i] = 0;
                    for (j = 0; j < aa.Count; j++)
                    {
                        a_z[i] = a_z[i] + aa.ElementAt(j)[i];
                    }
                }

                b_z = new double[bb.Count];
                for (i = 0; i < b_z.Length; i++)
                {
                    b_z[i] = 0;
                    for (j = 0; j < bb.Count; j++)
                    {
                        b_z[i] = b_z[i] + bb.ElementAt(j)[i];
                    }
                }

                for (i = 0; i < b_z.Length; i++)
                {
                    b_z[i] = b_z[i] / a_z[0];
                }
                for (i = a_z.Length - 1; i >= 0; i--)
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
                        if (G > 1.0)
                            scalefactor = pGraph.Height / maxVal / 2.2 / G;
                        else
                            scalefactor = pGraph.Height / maxVal / 2.4;
                    else
                    {
                        if (G > 1.0)
                            scalefactor = pGraph.Height / Math.Abs(minVal) / 2.2 / G;
                        else
                            scalefactor = pGraph.Height / Math.Abs(minVal) / 2.4;
                    }
                }
                else
                    scalefactor = 5.0;
                drawCeroline = true;
            }
            else
            {
                scalefactor = pGraph.Height / (maxVal) / 2.0;
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
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            t = 2.0 * Math.PI * fc / fs;
            TShelving shelv = new TShelving(N, t);
            shelv.CalcShelving(G, cbHighPass.Checked == true);
            shelv.TransformToZPlane();
            
            a = shelv.a_z;
            b = shelv.b_z;
            // create a signal
            for (i = 0; i < datapoints; i++)
            {
                t_in[i] = i / fs;
                y_in[i] = 20.0 * Math.Sin(2.0 * Math.PI * t_in[i] * f);
            }
            // as long as there are not enough values to fill the polynomials
            for (i = 0; i < a.Length; i++)
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
            // now there are enough values for the complete filter
            for (i = a.Length; i < datapoints; i++)
            {
                y_out[i] = 0;
                for (j = 0; j < a.Length; j++)
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
