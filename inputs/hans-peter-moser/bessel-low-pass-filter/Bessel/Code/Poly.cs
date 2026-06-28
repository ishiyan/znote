
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
