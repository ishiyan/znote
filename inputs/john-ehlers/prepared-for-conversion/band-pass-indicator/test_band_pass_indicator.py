"""Independent full-history listing oracle and meaningful streaming checks."""
import importlib.util
import math
from pathlib import Path
import unittest

DIRECTORY=Path(__file__).resolve().parent
SLUG=DIRECTORY.name
SPEC=importlib.util.spec_from_file_location('scalar_master',DIRECTORY/(SLUG+'.py'))
MASTER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUT_CLOSE=MASTER._load_arrays(DIRECTORY/'test_testdata.py')['INPUT_CLOSE']


class ListingOracle:
    """Unbounded full-variable history, coefficients recomputed each bar.

    Unlike the master, missing historical values are resolved at read time.
    Full-precision constants and documented public startup are intentional.
    """
    def __init__(self, parameters):
        self.p=parameters
        self.prices=[]; self.high1=[]; self.high2=[]; self.out=[]
        self.bp=[]; self.peak=[]; self.signal=[]; self.trigger=[]
        self.dim=[]; self.hurst=[]

    @staticmethod
    def at(series, lag=0):
        return series[-1-lag] if len(series)>lag else 0.0

    @staticmethod
    def alpha(angle):
        return (math.cos(angle)+math.sin(angle)-1.0)/math.cos(angle)

    def update(self, price):
        p=self.p
        if SLUG=='decycler':
            alpha=self.alpha(2.0*math.pi/p.cutoff)
            value=(alpha/2.0)*(price+self.at(self.prices))+(1.0-alpha)*self.at(self.out)
            # Independently calculate the cancellation definition too.
            high=(1.0-alpha/2.0)*(price-self.at(self.prices))+(1.0-alpha)*self.at(self.high1)
            self.high1.append(high)
            result=dict(value=value,cancellation=price-high)
        elif SLUG=='decycler-oscillator':
            difference=price-2.0*self.at(self.prices)+self.at(self.prices,1)
            highs=[]
            for period,series in ((p.highpass_period1,self.high1),(p.highpass_period2,self.high2)):
                alpha=self.alpha(math.sqrt(2.0)*math.pi/period)
                hp=(1.0-alpha/2.0)**2*difference+2.0*(1.0-alpha)*self.at(series)-(1.0-alpha)**2*self.at(series,1)
                highs.append(hp)
            self.high1.append(highs[0]); self.high2.append(highs[1])
            value=highs[1]-highs[0]
            result=dict(value=value,high_pass1=highs[0],high_pass2=highs[1])
        elif SLUG=='band-pass-indicator':
            alpha2=self.alpha(.25*p.bandwidth*2.0*math.pi/p.period)
            hp=(1.0+alpha2/2.0)*(price-self.at(self.prices))+(1.0-alpha2)*self.at(self.high1)
            beta=math.cos(2.0*math.pi/p.period)
            gamma=1.0/math.cos(2.0*math.pi*p.bandwidth/p.period)
            alpha=gamma-math.sqrt(gamma*gamma-1.0)
            bp=.5*(1.0-alpha)*(hp-self.at(self.high1,1))+beta*(1.0+alpha)*self.at(self.bp)-alpha*self.at(self.bp,1)
            if len(self.prices)<2: bp=0.0
            peak=.991*self.at(self.peak)
            if abs(bp)>peak:peak=abs(bp)
            signal=bp/peak if peak else self.at(self.signal)
            alpha2=self.alpha(1.5*p.bandwidth*2.0*math.pi/p.period)
            trigger=(1.0+alpha2/2.0)*(signal-self.at(self.signal))+(1.0-alpha2)*self.at(self.trigger)
            self.high1.append(hp);self.bp.append(bp);self.peak.append(peak)
            self.signal.append(signal);self.trigger.append(trigger)
            result=dict(high_pass=hp,band_pass=bp,peak=peak,signal=signal,trigger=trigger)
            self.prices.append(price)
            return result
        else:
            self.prices.append(price)
            half=p.length//2
            # Build full current windows from independent chronological history.
            all_values=[self.at(self.prices,j) for j in range(p.length)]
            n3=(max(all_values)-min(all_values))/p.length
            current=all_values[:half];older=all_values[half:]
            n1=(max(current)-min(current))/half
            n2=(max(older)-min(older))/half
            dimension=self.at(self.dim)
            updated=n1>0 and n2>0 and n3>0
            if updated:
                dimension=.5*((math.log(n1+n2)-math.log(n3))/math.log(2.0)+self.at(self.dim))
            hurst=2.0-dimension
            a=math.exp(-math.sqrt(2.0)*math.pi/p.smoothing_period)
            c2=2.0*a*math.cos(math.sqrt(2.0)*math.pi/p.smoothing_period)
            c3=-a*a;c1=1.0-c2-c3
            value=c1*(hurst+self.at(self.hurst))/2.0+c2*self.at(self.out)+c3*self.at(self.out,1)
            self.dim.append(dimension);self.hurst.append(hurst);self.out.append(value)
            return dict(n1=n1,n2=n2,n3=n3,dimension=dimension,hurst=hurst,value=value,dimension_updated=updated)
        self.prices.append(price);self.out.append(value)
        return result


class MasterTests(unittest.TestCase):
    def same(self, actual, expected):
        if math.isnan(expected):self.assertTrue(math.isnan(actual))
        else:self.assertTrue(math.isclose(actual,expected,rel_tol=1e-11,abs_tol=1e-11),f'{actual} vs {expected}')

    def test_all_reference_cases_against_listing(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                obj=MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k!='what_it_tests'})
                oracle=ListingOracle(obj.parameters)
                for i,price in enumerate(INPUT_CLOSE):
                    output=obj.update(price);expected=oracle.update(price)
                    self.assertEqual(obj.is_primed,i>=obj.warmup_bars)
                    for field in obj.state._fields:
                        if field=='previous_close':self.assertEqual(obj.state.previous_close,price)
                        elif field=='dimension_updated':self.assertEqual(obj.state.dimension_updated,expected[field])
                        else:self.same(getattr(obj.state,field),expected[field])
                    if SLUG=='decycler':self.same(obj.state.value,expected['cancellation'])
                    if isinstance(output,float):self.same(output,expected['value'] if obj.is_primed else math.nan)
                    else:
                        for field in output._fields:self.same(getattr(output,field),expected[field] if obj.is_primed else math.nan)

    def test_nan_invalid_and_overflow_are_transactional(self):
        obj=MASTER.MASTER_CLASS();control=MASTER.MASTER_CLASS()
        for value in INPUT_CLOSE[:180]:obj.update(value);control.update(value)
        state,count,last=obj.state,obj.samples_seen,obj.output
        missing=obj.update(math.nan)
        self.assertTrue(math.isnan(missing) if isinstance(missing,float) else all(math.isnan(v) for v in missing))
        self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
        for bad in (math.inf,-math.inf,True,None,'not a price'):
            with self.assertRaises(ValueError):obj.update(bad)
            self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
        self.assertEqual(obj.update(INPUT_CLOSE[180]),control.update(INPUT_CLOSE[180]))
        # Force arithmetic failure while preserving valid pre-call state.
        # Two same-sign maxima overflow the decycler's paired-price sum;
        # two opposite-sign maxima overflow the other source differences/ranges.
        large=8e307 if SLUG=='decycler-oscillator' else 1e308
        obj.update(large)
        state,count,last=obj.state,obj.samples_seen,obj.output
        bad=1e308 if SLUG=='decycler' else -1e308
        with self.assertRaises(ValueError):obj.update(bad)
        self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
        # Recovery after the rejected arithmetic step matches a stream that
        # accepted the same huge sample and never received the rejected one.
        control2=MASTER.MASTER_CLASS()
        for value in INPUT_CLOSE[:181]:control2.update(value)
        control2.update(large)
        self.assertEqual(obj.update(INPUT_CLOSE[181]),control2.update(INPUT_CLOSE[181]))

    def test_reset_and_immutable_snapshots(self):
        obj=MASTER.MASTER_CLASS();fresh=MASTER.MASTER_CLASS()
        for close in INPUT_CLOSE:obj.update(close)
        snapshot=obj.state
        obj.update(102.0)
        with self.assertRaises(AttributeError):setattr(obj.parameters,obj.parameters._fields[0],10)
        self.assertNotEqual(obj.state,snapshot)
        obj.reset()
        self.assertEqual(obj.samples_seen,0);self.assertFalse(obj.is_primed)
        for close in INPUT_CLOSE:
            a,b=obj.update(close),fresh.update(close)
            if obj.is_primed:self.assertEqual(a,b)
        self.assertEqual(obj.state,fresh.state)

    def test_zero_stream_source_initialization(self):
        obj=MASTER.MASTER_CLASS()
        for _ in range(800):output=obj.update(0.0)
        if SLUG=='hurst-coefficient':
            self.assertEqual(obj.state.dimension,0.0)
            self.assertEqual(obj.state.hurst,2.0)
            self.same(output,2.0)  # Source holds dimension zero, no .5 fallback.
        elif SLUG=='band-pass-indicator':self.assertEqual(output,MASTER.BandPassOutput(0.0,0.0))
        else:self.assertEqual(output,0.0)

    def test_exact_history_boundary(self):
        obj=MASTER.MASTER_CLASS()
        for _ in range(obj.warmup_bars):
            out=obj.update(100.0)
            self.assertTrue(math.isnan(out) if isinstance(out,float) else all(math.isnan(v) for v in out))
        out=obj.update(101.0)
        self.assertTrue(math.isfinite(out) if isinstance(out,float) else all(math.isfinite(v) for v in out))
        if SLUG=='hurst-coefficient':
            long=MASTER.MASTER_CLASS(length=252)
            for close in INPUT_CLOSE:self.assertTrue(math.isnan(long.update(close)))
            self.assertTrue(math.isfinite(long.update(108.0)))

    def test_analytic_or_source_specific_behavior(self):
        if SLUG=='decycler':
            obj=MASTER.MASTER_CLASS(cutoff=30.0)
            angle=2.0*math.pi/30.0
            alpha=(math.cos(angle)+math.sin(angle)-1.0)/math.cos(angle)
            pole=1.0-alpha
            for i in range(100):
                obj.update(1.0 if i==0 else 0.0)
                expected=alpha/2.0 if i==0 else (alpha/2.0)*(1.0+pole)*pole**(i-1)
                self.same(obj.state.value,expected)
            for _ in range(1000):out=obj.update(120.0)
            self.same(out,120.0)
        elif SLUG=='decycler-oscillator':
            equal=MASTER.MASTER_CLASS(highpass_period1=30,highpass_period2=30)
            normal=MASTER.MASTER_CLASS();reverse=MASTER.MASTER_CLASS(highpass_period1=60,highpass_period2=30)
            for price in INPUT_CLOSE:
                equal.update(price);normal.update(price);reverse.update(price)
                self.assertEqual(equal.state.value,0.0)
                self.assertEqual(normal.state.value,-reverse.state.value)
        elif SLUG=='band-pass-indicator':
            obj=MASTER.MASTER_CLASS()
            previous=0.0
            max_difference=0.0
            angle=1.5*.3*2.0*math.pi/20.0
            alpha=(math.cos(angle)+math.sin(angle)-1.0)/math.cos(angle)
            previous_trigger=0.0
            for i,price in enumerate(INPUT_CLOSE):
                obj.update(price);state=obj.state
                if i<2:self.assertEqual(state.band_pass,0.0)
                self.assertLessEqual(abs(state.signal),1.0)
                self.same(state.trigger,(1.0+alpha/2.0)*(state.signal-previous)+(1.0-alpha)*previous_trigger)
                max_difference=max(max_difference,abs(state.trigger-.9*previous))
                previous,previous_trigger=state.signal,state.trigger
            self.assertGreater(max_difference,.2)
        else:
            # Length=2 half windows each contain one sample, so the guard is
            # always false, even when the full window has a nonzero range.
            obj=MASTER.MASTER_CLASS(length=2)
            for price in INPUT_CLOSE:obj.update(price)
            self.assertEqual(obj.state.dimension,0.0);self.assertEqual(obj.state.hurst,2.0)
            # Gaps between constant halves invalidate N1/N2; do not update D.
            obj=MASTER.MASTER_CLASS(length=4)
            for price in (0,1,2,3):obj.update(price)
            dim=obj.state.dimension
            for price in (10,10,10,10):
                previous=obj.state.dimension;obj.update(price)
                if not obj.state.dimension_updated:self.assertEqual(obj.state.dimension,previous)
            self.assertFalse(obj.state.dimension_updated)
            self.assertNotEqual(dim,0.0)

    def test_scale_behavior(self):
        obj=MASTER.MASTER_CLASS();scaled=MASTER.MASTER_CLASS()
        for price in INPUT_CLOSE:
            obj.update(price);scaled.update(price*8.0)
            if SLUG=='band-pass-indicator':
                self.same(obj.state.signal,scaled.state.signal)
                self.same(obj.state.trigger,scaled.state.trigger)
            elif SLUG=='hurst-coefficient':self.same(obj.state.value,scaled.state.value)
            else:self.same(8.0*obj.state.value,scaled.state.value)

    def test_invalid_parameters(self):
        if SLUG=='decycler':cases=[dict(cutoff=4),dict(cutoff=True),dict(cutoff=math.inf),dict(cutoff=1e300)]
        elif SLUG=='decycler-oscillator':cases=[dict(highpass_period1=4),dict(highpass_period2=math.nan),dict(highpass_period1=True),dict(highpass_period2=1e300)]
        elif SLUG=='band-pass-indicator':cases=[dict(period=5),dict(bandwidth=0),dict(bandwidth=-1),dict(period=6,bandwidth=1),dict(bandwidth=True),dict(bandwidth=1e-300)]
        else:cases=[dict(length=1),dict(length=3),dict(length=30.0),dict(length=True),dict(smoothing_period=1),dict(smoothing_period=math.nan),dict(smoothing_period=1e300)]
        for params in cases:
            with self.subTest(params=params),self.assertRaises(ValueError):MASTER.MASTER_CLASS(**params)


if __name__=='__main__':unittest.main()
