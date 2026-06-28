
using System;

namespace WindowsFormsApplication1
{
    public static class Poly
    {
        public static double[] Mult(double[] p1, double[] p2)
        {
            int i, j;
            double[] tempPoly = new double[p1.Length + p2.Length - 1];
            for (i = 0; i < p1.Length; i++)
            {
                for (j = 0; j < p2.Length; j++)
                {
                    tempPoly[j + i] = tempPoly[j + i] + p2[j] * p1[i];
                }
            }
            return tempPoly;
        }

        public static double[] Mult(double[] p1, double p2)
        {
            int i;
            for (i = 0; i < p1.Length; i++)
            {
                p1[i] = p1[i] * p2;
            }
            return p1;
        }

        public static double[] Divide(double[] a, double[] b, int order)
        {
            int i, j;
            double fact;
            double[] a2 = new double[order - 1];
            for (i = 0; i < order - 3; i++)
            {
                if (System.Math.Abs(b[0]) > 1E-30)
                {
                    fact = a[i];
                    for (j = 0; j < 2; j++)
                    {
                        a2[j + i] = a[j + i + 1] - b[j + 1] * fact;
                    }
                    for (j = 2; j < order - 1 - i; j++)
                    {
                        a2[j + i] = a[j + 1 + i];
                    }

                    for (j = i; j < order - 1; j++)
                        a[j + 1] = a2[j];
                }
            }
            return a;
        }


        public static double[] Power(double[] a, int power)
        {
            double[] a2 = { 1 };
            for (int i = 0; i < power; i++)
                a2 = Mult(a2, a);
            return a2;
        }


        public static void Copy(double[] source, ref double[] dest)
        {
            int i;
            Array.Resize(ref dest, source.Length);
            for (i = 0; i < dest.Length; i++)
            {
                dest[i] = source[i];
            }
        }
    }
}
