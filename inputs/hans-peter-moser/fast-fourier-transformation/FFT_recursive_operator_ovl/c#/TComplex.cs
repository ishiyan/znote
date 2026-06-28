using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WindowsFormsApplication1
{
    public struct TComplex
    {
        public double real;
        public double imag;

        // operator overloads for complex numbers
        public static TComplex operator +(TComplex a, TComplex b)
        {
            TComplex res;
            res.real = a.real + b.real;
            res.imag = a.imag + b.imag;
            return (res);
        }

        public static TComplex operator -(TComplex a, TComplex b)
        {
            TComplex res;
            res.real = a.real - b.real;
            res.imag = a.imag - b.imag;
            return (res);
        }

        public static TComplex operator *(TComplex a, TComplex b)
        {
            TComplex res;
            res.real = a.real * b.real - a.imag * b.imag;
            res.imag = a.real * b.imag + a.imag * b.real;
            return (res);
        }

        public static TComplex operator /(TComplex a, TComplex b)
        {
            TComplex res;
            double l = b.imag * b.imag + b.real * b.real;
            if (l > 0.0)
            {
                res.real = (a.real * b.real + a.imag * b.imag) / l;
                res.imag = (-a.real * b.imag + a.imag * b.real) / l;
            }
            else
            {
                res.real = 1E300;
                res.imag = 0;
            }
            return (res);
        }
    }
}
