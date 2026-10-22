"""Independent full-history source transcription and causal streaming checks."""
import importlib.util
import math
from pathlib import Path
import unittest
from unittest import mock

DIRECTORY=Path(__file__).resolve().parent
SLUG=DIRECTORY.name
SPEC=importlib.util.spec_from_file_location('master',DIRECTORY/(SLUG+'.py'))
MASTER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS=MASTER._load_arrays(DIRECTORY/'test_testdata.py')['INPUT_CLOSE']
KIND='hilbert'

class ListingOracle:
    """Independent chronological histories; coefficients recalculated each bar."""
    def __init__(self,p):
        self.p=p
        self.x=[];self.hp=[];self.f=[];self.ip=[];self.real=[]
        self.difference=[];self.qp=[];self.q=[];self.imag=[]

    @staticmethod
    def at(series,lag=0):
        return series[-1-lag] if len(series)>lag else 0.0

    @staticmethod
    def coefficients(period):
        a=math.exp(-math.sqrt(2.0)*math.pi/period)
        c2=2.0*a*math.cos(math.sqrt(2.0)*math.pi/period)
        c3=-a*a
        return 1.0-c2-c3,c2,c3

    def update(self,price):
        p=self.p
        theta=math.sqrt(2.0)*math.pi/p.highpass_period
        alpha=(math.cos(theta)+math.sin(theta)-1.0)/math.cos(theta)
        h=((1.0-alpha/2.0)**2*(price-2.0*self.at(self.x)+self.at(self.x,1))
           +2.0*(1.0-alpha)*self.at(self.hp)-(1.0-alpha)**2*self.at(self.hp,1))
        c1,c2,c3=self.coefficients(p.smoothing_period)
        f=c1*(h+self.at(self.hp))/2.0+c2*self.at(self.f)+c3*self.at(self.f,1)
        ip=max(.991*self.at(self.ip),abs(f))
        real=f/ip if ip else self.at(self.real)
        difference=real-self.at(self.real)
        qp=max(.991*self.at(self.qp),abs(difference))
        q=difference/qp if qp else self.at(self.q)
        k1,k2,k3=self.coefficients(p.quadrature_period)
        imag=(k1*(q+self.at(self.q))/2.0+k2*self.at(self.imag)+k3*self.at(self.imag,1)
              if p.smooth_imaginary else q)
        self.x.append(price);self.hp.append(h);self.f.append(f);self.ip.append(ip)
        self.real.append(real);self.difference.append(difference);self.qp.append(qp)
        self.q.append(q);self.imag.append(imag)
        return dict(real=real,imaginary=imag,high_pass=h,filtered=f,in_phase_peak=ip,
                    raw_difference=difference,quadrature_peak=qp,normalized_quadrature=q)

class MasterTests(unittest.TestCase):
    def same(self,a,b):
        if math.isnan(b):self.assertTrue(math.isnan(a))
        else:self.assertTrue(math.isclose(a,b,rel_tol=5e-10,abs_tol=5e-10),f'{a} vs {b}')

    def test_every_confirmed_case_against_source_histories(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                indicator=MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k!='what_it_tests'})
                oracle=ListingOracle(indicator.parameters)
                previous_transform=0.0
                for i,price in enumerate(INPUTS):
                    expected=oracle.update(price)
                    output=indicator.update(price)
                    state=indicator.state
                    if KIND=='hilbert':
                        for field in state._fields:self.same(getattr(state,field),expected[field])
                    else:
                        base=expected['value']
                        self.same(state.base_value,base)
                        self.same(state.raw_ratio,expected['raw_ratio'])
                        self.same(state.denominator,expected['denominator'])
                        self.same(state.cycle.high_pass,expected['high'])
                        self.same(state.cycle.filtered,expected['filtered'])
                        for a,b in zip(state.cycle.correlations,oracle.corr):self.same(a,b)
                        for a,b in zip(state.cycle.smoothed_power,oracle.powers.values()):self.same(a,b)
                        translated=2.0*(base-.5)
                        self.same(state.translated_input,translated)
                        if KIND=='rsi':
                            amplified=min(.999,max(-.999,1.5*translated))
                            self.same(state.amplified_input,amplified)
                            expected['value']=.5*math.log((1.0+amplified)/(1.0-amplified))
                        else:
                            exponential=math.exp(6.0*translated)
                            expected['value']=(exponential-1.0)/(exponential+1.0)
                            expected['trigger']=.9*previous_transform
                            self.same(state.trigger,expected['trigger'])
                        self.same(state.value,expected['value'])
                        previous_transform=expected['value']
                    self.assertEqual(indicator.is_primed,i>=indicator.warmup_bars)
                    for field in output._fields:
                        self.same(getattr(output,field),expected[field] if indicator.is_primed else math.nan)

    def test_missing_invalid_input_preserves_every_state(self):
        m=MASTER.MASTER_CLASS();control=MASTER.MASTER_CLASS()
        for price in INPUTS[:150]:m.update(price);control.update(price)
        state,count,output=m.state,m.samples_seen,m.output
        self.assertTrue(all(math.isnan(v) for v in m.update(math.nan)))
        for value in (math.inf,-math.inf,True,'not a number',None,10**1000):
            with self.assertRaises(ValueError):m.update(value)
            self.assertEqual(m.state,state);self.assertEqual(m.samples_seen,count)
            self.assertIs(m.output,output)
        self.assertEqual(m.update(INPUTS[150]),control.update(INPUTS[150]))

    def test_arithmetic_overflow_preserves_every_state(self):
        m=MASTER.MASTER_CLASS()
        for price in INPUTS[:100]:m.update(price)
        if KIND=='hilbert':m.update(1e308)
        before,count,output=m.state,m.samples_seen,m.output
        with self.assertRaises(ValueError):m.update(-1e308)
        self.assertEqual(m.state,before);self.assertEqual(m.samples_seen,count)
        self.assertIs(m.output,output)

    def test_reset_and_immutable_snapshots(self):
        m=MASTER.MASTER_CLASS()
        for price in INPUTS:m.update(price)
        snapshot=m.state
        with self.assertRaises(AttributeError):m.parameters.smoothing_period=12
        with self.assertRaises(AttributeError):snapshot.value=123
        m.update(100.0)
        self.assertNotEqual(snapshot,m.state)
        m.reset();control=MASTER.MASTER_CLASS()
        for price in INPUTS:
            a,b=m.update(price),control.update(price)
            if m.is_primed:self.assertEqual(a,b)
            else:self.assertTrue(all(math.isnan(v) for v in a))
        self.assertEqual(m.state,control.state)

    def test_all_zero_input_defined_extensions(self):
        m=MASTER.MASTER_CLASS()
        for _ in range(m.warmup_bars+10):output=m.update(0.0)
        self.assertTrue(all(math.isfinite(v) for v in output))
        if KIND=='hilbert':
            self.assertEqual(output.real,0.0);self.assertEqual(output.imaginary,0.0)
        elif KIND=='rsi':
            self.same(output.value,-math.atanh(.999));self.assertEqual(m.state.base_value,0.0)
        else:
            self.same(output.value,-math.tanh(3.0));self.same(output.trigger,.9*output.value)
            self.assertEqual(m.state.raw_ratio,0.0);self.assertEqual(m.state.base_value,0.0)
        if KIND!='hilbert':
            self.assertFalse(m.state.cycle.has_cycle)
            self.assertEqual(output.dominant_cycle,float(m.min_period))

    def test_history_boundary_and_no_future_revisions(self):
        m=MASTER.MASTER_CLASS();outputs=[m.update(price) for price in INPUTS]
        for i,out in enumerate(outputs):self.assertEqual(all(math.isnan(v) for v in out),i<m.warmup_bars)
        before=repr(outputs)
        for i in range(20):m.update(100.+i)
        self.assertEqual(before,repr(outputs))
        if KIND!='hilbert':
            b=MASTER.MASTER_CLASS(averaging_length=204)
            history=[b.update(x) for x in INPUTS]
            self.assertTrue(all(math.isnan(v) for out in history[:-1] for v in out))
            self.assertTrue(all(math.isfinite(v) for v in history[-1]))
            b=MASTER.MASTER_CLASS(averaging_length=205)
            self.assertTrue(all(math.isnan(v) for x in INPUTS for v in b.update(x)))

    def test_invalid_parameters(self):
        trials=([dict(highpass_period=4),dict(smoothing_period=1),dict(quadrature_period=1),
                 dict(smooth_imaginary=1),dict(smoothing_period=True),dict(quadrature_period=1e308)]
                if KIND=='hilbert' else [dict(min_period=5),dict(max_period=9),dict(averaging_length=1),
                   dict(averaging_length=True),dict(highpass_period=4),dict(smoothing_period=1)])
        trials += [dict(highpass_period=math.inf),dict(smoothing_period=math.nan),dict(smoothing_period=None)]
        for kwargs in trials:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):MASTER.MASTER_CLASS(**kwargs)

    def test_full_precision_coefficients(self):
        m=MASTER.MASTER_CLASS();roof=m._roof if KIND=='hilbert' else m._cycle.roof
        hp=m.parameters.highpass_period
        angle=2.0*math.pi/(math.sqrt(2.0)*hp)
        alpha=(math.cos(angle)+math.sin(angle)-1.0)/math.cos(angle)
        self.assertEqual(roof.hp0,(1.0-alpha/2.0)**2)
        truncated=(math.cos(.707*2.0*math.pi/hp)+math.sin(.707*2.0*math.pi/hp)-1.0)/math.cos(.707*2.0*math.pi/hp)
        self.assertNotEqual(roof.hp0,(1.0-truncated/2.0)**2)

    def test_raw_and_smoothed_share_real_but_not_imaginary(self):
        a=MASTER.MASTER_CLASS();b=MASTER.MASTER_CLASS(smooth_imaginary=False)
        q_previous=imag_previous=imag_older=0.0
        for price in INPUTS:
            a.update(price);b.update(price)
            self.assertEqual(a.state.real,b.state.real)
            self.assertEqual(a.state.normalized_quadrature,b.state.imaginary)
            expected=(a._q1*(a.state.normalized_quadrature+q_previous)/2.0
                      +a._q2*imag_previous+a._q3*imag_older)
            self.assertEqual(a.state.imaginary,expected)
            q_previous=a.state.normalized_quadrature
            imag_older,imag_previous=imag_previous,a.state.imaginary
        self.assertNotEqual(a.output.imaginary,b.output.imaginary)

    def test_synthetic_chirp_and_constant_startup(self):
        m=MASTER.MASTER_CLASS();oracle=ListingOracle(m.parameters)
        phase=0.0
        for i in range(400):
            phase+=2.0*math.pi/(10.0+30.0*i/399.0)
            price=100.0+5.0*math.sin(phase)
            m.update(price);expected=oracle.update(price)
            self.same(m.state.real,expected['real']);self.same(m.state.imaginary,expected['imaginary'])
            self.assertLessEqual(abs(m.state.real),1.0)
            self.assertLessEqual(abs(m.state.normalized_quadrature),1.0)
        c=MASTER.MASTER_CLASS();c.update(100.0)
        self.assertNotEqual(c.state.filtered,0.0)

    def test_downstream_failure_is_atomic(self):
        m=MASTER.MASTER_CLASS()
        for price in INPUTS[:50]:m.update(price)
        before,count,output=m.state,m.samples_seen,m.output
        coefficient=m._q1;m._q1=math.inf
        with self.assertRaises(ValueError):m.update(INPUTS[50])
        m._q1=coefficient
        self.assertEqual(before,m.state);self.assertEqual(count,m.samples_seen);self.assertIs(output,m.output)


if __name__=='__main__':unittest.main()
