"""Independent source transcription and streaming/algorithmic checks."""
import importlib.util
import math
from pathlib import Path
import unittest

DIRECTORY=Path(__file__).resolve().parent
SLUG=DIRECTORY.name
SPEC=importlib.util.spec_from_file_location('listing_master',DIRECTORY/(SLUG+'.py'))
MASTER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MASTER)
INPUTS=MASTER._load_arrays(DIRECTORY/'test_testdata.py')['INPUT_CLOSE']


class ListingOracle:
    """Full histories and coefficients calculated again each bar.

    This oracle uses historical lookup rather than bounded master buffers.
    It transcribes each source listing with the documented precision/seeds.
    """
    def __init__(self,p):
        self.p=p
        self.x=[];self.hp=[];self.f=[];self.ratio=[];self.denom=[];self.out=[]
        self.corr=[0.0]*(p.max_lag-p.min_lag+1) if SLUG=='autocorrelation-reversals' else []

    @staticmethod
    def at(series,lag=0):
        return series[-1-lag] if len(series)>lag else 0.0

    def update(self,price):
        p=self.p
        if SLUG=='even-better-sinewave':
            angle=2.0*math.pi/p.duration
            pole=(1.0-math.sin(angle))/math.cos(angle)
            high=.5*(1.0+pole)*(price-self.at(self.x))+pole*self.at(self.hp)
        else:
            period=48.0 if SLUG=='autocorrelation-reversals' and p.source=='book' else p.highpass_period
            angle=math.sqrt(2.0)*math.pi/period
            alpha=(math.cos(angle)+math.sin(angle)-1.0)/math.cos(angle)
            high=((1.0-alpha/2.0)*(1.0-alpha/2.0)*(price-2.0*self.at(self.x)+self.at(self.x,1))
                  +2.0*(1.0-alpha)*self.at(self.hp)-(1.0-alpha)*(1.0-alpha)*self.at(self.hp,1))
        a=math.exp(-math.sqrt(2.0)*math.pi/p.smoothing_period)
        c2=2.0*a*math.cos(math.sqrt(2.0)*math.pi/p.smoothing_period)
        c3=-a*a;c1=1.0-c2-c3
        filtered=c1*(high+self.at(self.hp))/2.0+c2*self.at(self.f)+c3*self.at(self.f,1)
        self.x.append(price);self.hp.append(high);self.f.append(filtered)
        if SLUG=='modified-relative-strength-index':
            up=down=0.0
            for count in range(p.length):
                newer=self.at(self.f,count);older=self.at(self.f,count+1)
                if newer>older:up+=newer-older
                if newer<older:down+=older-newer
            denominator=up+down
            ratio=up/denominator if denominator else self.at(self.ratio)
            updated=denominator!=0 and self.at(self.denom)!=0
            value=self.at(self.out)
            if updated:value=c1*(ratio+self.at(self.ratio))/2.0+c2*self.at(self.out)+c3*self.at(self.out,1)
            self.ratio.append(ratio);self.denom.append(denominator);self.out.append(value)
            return dict(high_pass=high,filtered=filtered,closes_up=up,closes_down=down,
                        denominator=denominator,raw_ratio=ratio,value=value,smoothing_updated=updated)
        if SLUG=='autocorrelation-reversals':
            previous=self.corr.copy()
            for index,lag in enumerate(range(p.min_lag,p.max_lag+1)):
                m=p.averaging_length if p.averaging_length else lag
                sx=sy=sxx=sxy=syy=0.0
                for count in range(m):
                    x=self.at(self.f,count);y=self.at(self.f,lag+count)
                    sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;syy+=y*y
                denominator=(m*sxx-sx*sx)*(m*syy-sy*sy)
                if denominator>0:self.corr[index]=(m*sxy-sx*sy)/math.sqrt(denominator)
                self.corr[index]=.5*(self.corr[index]+1.0)
            changes=sum(1 for a,b in zip(self.corr,previous) if (a>.5 and b<.5) or (a<.5 and b>.5))
            return dict(high_pass=high,filtered=filtered,correlations=tuple(self.corr),
                        previous_correlations=tuple(previous),sign_changes=changes,
                        reversal=1.0 if changes>p.sign_change_threshold else 0.0)
        wave=(filtered+self.at(self.f,1)+self.at(self.f,2))/3.0
        power=(filtered*filtered+self.at(self.f,1)**2+self.at(self.f,2)**2)/3.0
        value=wave/math.sqrt(power) if power else self.at(self.out)
        self.out.append(value)
        return dict(high_pass=high,filtered=filtered,mean_wave=wave,mean_power=power,value=value)


class MasterTests(unittest.TestCase):
    def same(self,actual,expected):
        if isinstance(expected,tuple):
            self.assertEqual(len(actual),len(expected))
            for a,b in zip(actual,expected):self.same(a,b)
        elif math.isnan(expected):self.assertTrue(math.isnan(actual))
        else:self.assertTrue(math.isclose(actual,expected,rel_tol=2e-10,abs_tol=2e-10),f'{actual} vs {expected}')

    def test_all_12_reference_cases_against_listing(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                obj=MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k!='what_it_tests'})
                oracle=ListingOracle(obj.parameters)
                for i,price in enumerate(INPUTS):
                    out=obj.update(price);expected=oracle.update(price)
                    self.assertEqual(obj.is_primed,i>=obj.warmup_bars)
                    for field in obj.state._fields:
                        if field in ('smoothing_updated','reversal','sign_changes'):
                            self.assertEqual(getattr(obj.state,field),expected[field])
                        else:self.same(getattr(obj.state,field),expected[field])
                    if isinstance(out,float):self.same(out,expected['value'] if obj.is_primed else math.nan)
                    else:
                        for field in out._fields:self.same(getattr(out,field),expected[field] if obj.is_primed else math.nan)

    def test_skipped_and_invalid_input_do_not_advance(self):
        obj=MASTER.MASTER_CLASS();control=MASTER.MASTER_CLASS()
        for price in INPUTS[:120]:obj.update(price);control.update(price)
        state,count,last=obj.state,obj.samples_seen,obj.output
        result=obj.update(math.nan)
        self.assertTrue(math.isnan(result) if isinstance(result,float) else all(math.isnan(v) for v in result))
        self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
        invalid=(math.inf,-math.inf,True,None,'bad')
        if SLUG!='modified-relative-strength-index':invalid+= (1e308,)
        for value in invalid:
            with self.assertRaises(ValueError):obj.update(value)
            self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
        self.assertEqual(obj.update(INPUTS[120]),control.update(INPUTS[120]))
        if SLUG=='modified-relative-strength-index':
            # A large but finite price is not automatically invalid. Accept
            # it, then force actual overflow of the second raw difference.
            obj.update(8e307);control.update(8e307)
            state,count,last=obj.state,obj.samples_seen,obj.output
            with self.assertRaises(ValueError):obj.update(-1.7e308)
            self.assertEqual(obj.state,state);self.assertEqual(obj.samples_seen,count);self.assertIs(obj.output,last)
            self.assertEqual(obj.update(INPUTS[121]),control.update(INPUTS[121]))

    def test_reset_and_immutable_configuration_and_state(self):
        obj=MASTER.MASTER_CLASS()
        for price in INPUTS:obj.update(price)
        snapshot=obj.state
        with self.assertRaises(AttributeError):setattr(obj.parameters,obj.parameters._fields[0],1)
        obj.update(88.0)
        self.assertNotEqual(obj.state,snapshot)
        obj.reset();fresh=MASTER.MASTER_CLASS()
        for price in INPUTS:
            a,b=obj.update(price),fresh.update(price)
            if obj.is_primed:self.assertEqual(a,b)
        self.assertEqual(obj.state,fresh.state)

    def test_zero_stream_and_exact_source_seeds(self):
        obj=MASTER.MASTER_CLASS()
        if SLUG=='autocorrelation-reversals':
            for n in range(1,21):
                obj.update(0.0)
                for value in obj.state.correlations:self.assertEqual(value,1.0-2.0**(-n))
                self.assertEqual(obj.state.sign_changes,0)
        else:
            for _ in range(100):obj.update(0.0)
            self.assertEqual(obj.state.value,0.0)
            if SLUG=='modified-relative-strength-index':self.assertFalse(obj.state.smoothing_updated)
            else:self.assertEqual(obj.state.mean_power,0.0)

    def test_public_input_history_boundaries(self):
        obj=MASTER.MASTER_CLASS()
        for _ in range(obj.warmup_bars):
            out=obj.update(100.0)
            self.assertTrue(math.isnan(out) if isinstance(out,float) else all(math.isnan(v) for v in out))
        out=obj.update(101.0)
        self.assertTrue(math.isfinite(out) if isinstance(out,float) else all(math.isfinite(v) for v in out))
        if SLUG=='modified-relative-strength-index':
            final=MASTER.MASTER_CLASS(length=250);none=MASTER.MASTER_CLASS(length=251)
            for index,price in enumerate(INPUTS):
                a,b=final.update(price),none.update(price)
                self.assertTrue(math.isnan(b))
                self.assertEqual(math.isnan(a),index<251)
        elif SLUG=='autocorrelation-reversals':
            final=MASTER.MASTER_CLASS(averaging_length=203)
            self.assertEqual(final.warmup_bars,251)
            for price in INPUTS[:-1]:self.assertTrue(all(math.isnan(v) for v in final.update(price)))
            self.assertTrue(all(math.isfinite(v) for v in final.update(INPUTS[-1])))
        else:self.assertEqual(obj.warmup_bars,4)

    def test_listing_specific_guards_and_math(self):
        if SLUG=='modified-relative-strength-index':
            obj=MASTER.MASTER_CLASS(length=1)
            obj.update(0.0);obj.update(1.0)
            self.assertEqual(obj.state.raw_ratio,1.0)
            self.assertEqual(obj.state.value,0.0)
            self.assertFalse(obj.state.smoothing_updated)
            obj.update(2.0);self.assertTrue(obj.state.smoothing_updated)
            # Force a exactly flat roof output using zero histories; verify
            # held output still shifts its two accepted-bar feedback values.
            obj._roof.reset();obj._history=[0.0,0.0]
            obj._denom=1.0;obj._ratio=.6;obj._y1=.4;obj._y2=.3
            obj.update(0.0)
            self.assertEqual(obj._y1,.4);self.assertEqual(obj._y2,.4)
            self.assertEqual(obj.state.raw_ratio,.6);self.assertFalse(obj.state.smoothing_updated)
        elif SLUG=='autocorrelation-reversals':
            # Exactly .5 touches are not counted; both strict crossing signs
            # are counted, and values staying on a side are not counted.
            now=(.6,.4,.5,.6,.4,.5,.9,.1)
            old=(.4,.6,.4,.5,.5,.6,.6,.4)
            self.assertEqual(MASTER._strict_sign_changes(now,old),2)
            obj=MASTER.MASTER_CLASS(averaging_length=1)
            for n,price in enumerate(INPUTS,1):
                obj.update(price)
                expected=1.0-2.0**(-n)
                self.assertTrue(all(value==expected for value in obj.state.correlations))
                self.assertEqual(obj.state.sign_changes,0)
        else:
            obj=MASTER.MASTER_CLASS()
            obj.update(91.5)
            self.same(obj.state.value,1.0/math.sqrt(3.0))
            self.assertGreater(obj.state.mean_power,0.0)
            for price in INPUTS[1:]:
                obj.update(price)
                self.assertLessEqual(abs(obj.state.value),1.0+1e-14)
                self.same(obj.state.value,obj.state.mean_wave/math.sqrt(obj.state.mean_power))
            # Equal three amplitudes normalize to the sign, not sqrt(2).
            self.same((2.0+2.0+2.0)/3.0/math.sqrt((4.0+4.0+4.0)/3.0),1.0)
            self.same((2.0-2.0+0.0)/3.0/math.sqrt((4.0+4.0+0.0)/3.0),0.0)

    def test_source_mode_or_transfer_or_output_smoothing(self):
        if SLUG=='autocorrelation-reversals':
            original=MASTER.MASTER_CLASS();unused=MASTER.MASTER_CLASS(highpass_period=80)
            configured=MASTER.MASTER_CLASS(highpass_period=80,source='configured-highpass')
            differences=0
            for price in INPUTS:
                original.update(price);unused.update(price);configured.update(price)
                self.assertEqual(original.state,unused.state)
                differences+=original.state.reversal!=configured.state.reversal
            self.assertGreater(differences,0)
            self.assertEqual(unused.effective_highpass_period,48.0)
            self.assertEqual(configured.effective_highpass_period,80.0)
        elif SLUG=='modified-relative-strength-index':
            obj=MASTER.MASTER_CLASS(length=5)
            extremes=[]
            for price in INPUTS:
                obj.update(price)
                self.assertTrue(0.0<=obj.state.raw_ratio<=1.0)
                extremes.append(obj.state.value)
            # Final source SuperSmoother is intentionally unclipped.
            self.assertTrue(min(extremes)<0.0 or max(extremes)>1.0)
        else:
            obj=MASTER.MASTER_CLASS(duration=40)
            angle=2.0*math.pi/40.0
            q=(1.0-math.sin(angle))/math.cos(angle)
            gain=.5*(1.0+q)
            for i in range(100):
                obj.update(1.0 if i==0 else 0.0)
                expected=gain if i==0 else -gain*(1.0-q)*q**(i-1)
                self.same(obj.state.high_pass,expected)

    def test_scale_behavior(self):
        normal=MASTER.MASTER_CLASS();scaled=MASTER.MASTER_CLASS()
        for price in INPUTS:
            normal.update(price);scaled.update(8.0*price)
            if SLUG=='autocorrelation-reversals':
                self.same(normal.state.correlations,scaled.state.correlations)
                self.assertEqual(normal.state.sign_changes,scaled.state.sign_changes)
            else:self.same(normal.state.value,scaled.state.value)

    def test_additional_boundary_behavior(self):
        if SLUG=='modified-relative-strength-index':
            fast=MASTER.MASTER_CLASS(length=1,highpass_period=5,smoothing_period=2)
            oracle=ListingOracle(fast.parameters)
            for price in INPUTS:
                fast.update(price);expected=oracle.update(price)
                self.same(fast.state.value,expected['value'])
                self.assertTrue(math.isfinite(fast.state.value))
            return
        if SLUG=='even-better-sinewave':
            fast=MASTER.MASTER_CLASS(duration=5,smoothing_period=2)
            oracle=ListingOracle(fast.parameters)
            for price in INPUTS:
                fast.update(price);expected=oracle.update(price)
                self.same(fast.state.value,expected['value'])
                self.assertLessEqual(abs(fast.state.value),1.0+1e-14)
            return
        # Decisions are checked around each observed count, including equality.
        objects={threshold:MASTER.MASTER_CLASS(sign_change_threshold=threshold)
                 for threshold in (0,23,24,25,46)}
        seen=set()
        for price in INPUTS:
            for threshold,obj in objects.items():
                obj.update(price);count=obj.state.sign_changes
                seen.add(count)
                self.assertEqual(obj.state.reversal,float(count>threshold))
        self.assertTrue(any(c==24 for c in seen))
        single=MASTER.MASTER_CLASS(min_lag=3,max_lag=3,sign_change_threshold=0)
        for price in INPUTS:single.update(price)
        self.assertEqual(len(single.state.correlations),1)

    def test_invalid_parameters(self):
        if SLUG=='modified-relative-strength-index':
            cases=[dict(length=0),dict(length=True),dict(length=10.0),dict(highpass_period=4),dict(smoothing_period=1),dict(smoothing_period=1e300)]
        elif SLUG=='autocorrelation-reversals':
            cases=[dict(min_lag=2),dict(max_lag=2),dict(averaging_length=-1),dict(averaging_length=2.0),dict(sign_change_threshold=-1),dict(source='corrected'),dict(highpass_period=True),dict(smoothing_period=math.nan)]
        else:
            cases=[dict(duration=4),dict(duration=True),dict(duration=math.inf),dict(duration=1e300),dict(smoothing_period=1),dict(smoothing_period=math.nan),dict(smoothing_period=1e300)]
        for values in cases:
            with self.subTest(values=values),self.assertRaises(ValueError):MASTER.MASTER_CLASS(**values)


if __name__=='__main__':unittest.main()
