"""Independent full-history transcriptions of Chapter 11, plus streaming checks."""
import importlib.util
import math
from pathlib import Path
import unittest

DIRECTORY=Path(__file__).resolve().parent
SLUG=DIRECTORY.name
SPEC=importlib.util.spec_from_file_location('adaptive_master',DIRECTORY/(SLUG+'.py'))
MASTER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS=MASTER._load_arrays(DIRECTORY/'test_testdata.py')['INPUT_CLOSE']
KIND='rsi'

class ListingOracle:
    """Full record of variable histories, separate from the bounded master."""
    def __init__(self,p):
        self.p=p
        self.x=[]; self.hp=[]; self.f=[]; self.mean=[]
        self.corr=[0.0]*(p.max_period+1)
        self.powers={period:0.0 for period in range(p.min_period,p.max_period+1)}
        self.max_power=0.0; self.dc=float(p.min_period)
        self.ratios=[]; self.denoms=[]; self.outputs=[]
        self.bp=[]; self.peaks=[]; self.signals=[]; self.lead_peaks=[]; self.lead_signals=[]
        self.c2=math.nan; self.c3=math.nan; self.c1=math.nan

    @staticmethod
    def at(series,lag=0,seed=0.0):
        return series[-1-lag] if len(series)>lag else seed

    def update(self,price):
        p=self.p
        theta=math.sqrt(2.0)*math.pi/p.highpass_period
        alpha=(math.cos(theta)+math.sin(theta)-1.0)/math.cos(theta)
        hp=((1.0-alpha/2.0)*(1.0-alpha/2.0)*(price-2.0*self.at(self.x)+self.at(self.x,1))
            +2.0*(1.0-alpha)*self.at(self.hp)-(1.0-alpha)*(1.0-alpha)*self.at(self.hp,1))
        a=math.exp(-math.sqrt(2.0)*math.pi/p.smoothing_period)
        c2=2.0*a*math.cos(math.sqrt(2.0)*math.pi/p.smoothing_period)
        c3=-a*a; c1=1.0-c2-c3
        self.c1,self.c2,self.c3=c1,c2,c3
        f=c1*(hp+self.at(self.hp))/2.0+c2*self.at(self.f)+c3*self.at(self.f,1)
        self.x.append(price); self.hp.append(hp); self.f.append(f)
        for lag in range(p.max_period+1):
            m=p.averaging_length if p.averaging_length else lag
            sx=sy=sxx=sxy=syy=0.0
            for count in range(m):
                x=self.at(self.f,count); y=self.at(self.f,lag+count)
                sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;syy+=y*y
            denominator=(m*sxx-sx*sx)*(m*syy-sy*sy)
            if denominator>0.0:
                self.corr[lag]=(m*sxy-sx*sy)/math.sqrt(denominator)
        for period in self.powers:
            cosine=sine=0.0
            for n in range(3,p.max_period+1):
                cosine+=self.corr[n]*math.cos(2.0*math.pi*n/period)
                sine+=self.corr[n]*math.sin(2.0*math.pi*n/period)
            sq=cosine*cosine+sine*sine
            self.powers[period]=.2*sq*sq+.8*self.powers[period]
        decay=.991 if KIND in ('rsi','cci') else .995
        self.max_power=decay*self.max_power
        for period in self.powers:
            if self.powers[period]>self.max_power:
                self.max_power=self.powers[period]
        norm={period:value/self.max_power if self.max_power else 0.0 for period,value in self.powers.items()}
        sp=spx=0.0
        for period in self.powers:
            if norm[period]>=.5:
                spx+=period*norm[period];sp+=norm[period]
        if sp: self.dc=spx/sp
        self.dc=min(float(p.max_period),max(float(p.min_period),self.dc))
        length=math.trunc(self.dc/2.0-1.0)+1 if KIND=='rsi' else math.floor(self.dc-1.0)+1
        mean=rms=denom=0.0
        if KIND=='rsi':
            up=down=0.0
            for count in range(length):
                newer=self.at(self.f,count); older=self.at(self.f,count+1)
                if newer>older:up+=newer-older
                if newer<older:down+=older-newer
            denom=up+down
            ratio=up/denom if denom else self.at(self.ratios)
            out=self.at(self.outputs)
            if denom and self.at(self.denoms):
                out=c1*(ratio+self.at(self.ratios))/2.0+c2*self.at(self.outputs)+c3*self.at(self.outputs,1)
        elif KIND=='stoch':
            highest=lowest=f
            for count in range(length):
                v=self.at(self.f,count)
                if v>highest:highest=v
                if v<lowest:lowest=v
            denom=highest-lowest
            ratio=(f-lowest)/denom if denom else self.at(self.ratios)
            out=c1*(ratio+self.at(self.ratios))/2.0+c2*self.at(self.outputs)+c3*self.at(self.outputs,1)
        elif KIND=='cci':
            for count in range(length):mean+=self.at(self.f,count)
            mean/=self.dc
            self.mean.append(mean)
            energy=0.0
            for count in range(length):
                residual=self.at(self.f,count)-self.at(self.mean,count)
                energy+=residual*residual
            rms=math.sqrt(energy/self.dc);denom=.015*rms
            ratio=(f-mean)/denom if denom else self.at(self.ratios)
            out=c1*(ratio+self.at(self.ratios))/2.0+c2*self.at(self.outputs)+c3*self.at(self.outputs,1)
        else:
            tuned=.9*self.dc
            beta=math.cos(2.0*math.pi/tuned)
            gamma=1.0/math.cos(2.0*math.pi*p.bandwidth/tuned)
            alpha=gamma-math.sqrt(gamma*gamma-1.0)
            bp=.5*(1.0-alpha)*(f-self.at(self.f,2))+beta*(1.0+alpha)*self.at(self.bp)-alpha*self.at(self.bp,1)
            if len(self.x) in (1,2):bp=0.0
            peak=.991*self.at(self.peaks)
            if abs(bp)>peak:peak=abs(bp)
            signal=bp/peak if peak else self.at(self.signals)
            trigger=.9*self.at(self.signals)
            lead=1.3*(signal+self.at(self.signals)-self.at(self.signals,1)-self.at(self.signals,2))/4.0
            lead_peak=.93*self.at(self.lead_peaks)
            if abs(lead)>lead_peak:lead_peak=abs(lead)
            lead_signal=.7*lead/lead_peak if lead_peak else self.at(self.lead_signals)
            self.bp.append(bp);self.peaks.append(peak);self.signals.append(signal)
            self.lead_peaks.append(lead_peak);self.lead_signals.append(lead_signal)
            return dict(signal=signal,trigger=trigger,dominant_cycle=self.dc,tuned_period=tuned,
                        high=hp,filtered=f,band_pass=bp,peak=peak,lead=lead,lead_peak=lead_peak,lead_signal=lead_signal)
        self.ratios.append(ratio);self.denoms.append(denom);self.outputs.append(out)
        return dict(value=out,dominant_cycle=self.dc,lookback_length=float(length),
                    high=hp,filtered=f,raw_ratio=ratio,denominator=denom,mean=mean,rms=rms)


class MasterTests(unittest.TestCase):
    def same(self,a,b):
        if math.isnan(b): self.assertTrue(math.isnan(a))
        else:self.assertTrue(math.isclose(a,b,rel_tol=5e-10,abs_tol=5e-10),f'{a} vs {b}')

    def test_all_cases_against_independent_listing(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                indicator=MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k!='what_it_tests'})
                oracle=ListingOracle(indicator.parameters)
                for i,price in enumerate(INPUTS):
                    output=indicator.update(price);expected=oracle.update(price)
                    state=indicator.state
                    self.same(state.cycle.high_pass,expected['high'])
                    self.same(state.cycle.filtered,expected['filtered'])
                    self.same(state.cycle.dominant_cycle,expected['dominant_cycle'])
                    for a,b in zip(state.cycle.correlations,oracle.corr):self.same(a,b)
                    for a,b in zip(state.cycle.smoothed_power,oracle.powers.values()):self.same(a,b)
                    for field in (('band_pass','peak','signal','trigger','lead','lead_peak','lead_signal') if KIND=='bp'
                                  else ('raw_ratio','value','denominator','mean','rms')):
                        self.same(getattr(state,field),expected[field])
                    self.assertEqual(indicator.is_primed,i>=indicator.warmup_bars)
                    for field in output._fields:
                        self.same(getattr(output,field),expected[field] if indicator.is_primed else math.nan)

    def test_missing_invalid_and_overflow_do_not_advance(self):
        master=MASTER.MASTER_CLASS();control=MASTER.MASTER_CLASS()
        for price in INPUTS[:150]: master.update(price);control.update(price)
        state,count,last=master.state,master.samples_seen,master.output
        self.assertTrue(all(math.isnan(v) for v in master.update(math.nan)))
        for value in (math.inf,-math.inf,True,1e308):
            with self.assertRaises(ValueError):master.update(value)
            self.assertEqual(master.state,state);self.assertEqual(master.samples_seen,count)
            self.assertIs(master.output,last)
        self.assertEqual(master.update(INPUTS[150]),control.update(INPUTS[150]))

    def test_reset_and_immutable_snapshots(self):
        master=MASTER.MASTER_CLASS()
        for price in INPUTS:master.update(price)
        state=master.state; snapshot=state.cycle.correlations
        master.update(100.0)
        self.assertEqual(state.cycle.correlations,snapshot)
        with self.assertRaises(AttributeError):master.parameters.min_period=12
        master.reset();control=MASTER.MASTER_CLASS()
        for price in INPUTS:
            a,b=master.update(price),control.update(price)
            if master.is_primed:self.assertEqual(a,b)
            else:self.assertTrue(all(math.isnan(v) for v in a))
        self.assertEqual(master.state,control.state)

    def test_zero_input_fallback_and_defined_extensions(self):
        master=MASTER.MASTER_CLASS()
        for _ in range(master.warmup_bars+100):output=master.update(0.0)
        self.assertTrue(master.is_primed)
        self.assertFalse(master.state.cycle.has_cycle)
        self.assertEqual(output.dominant_cycle,10.0)
        if KIND=='bp':
            self.assertEqual(output.signal,0.0);self.assertEqual(output.trigger,0.0)
        elif KIND=='stoch':self.assertEqual(output.value,0.0)
        else:self.assertEqual(output.value,0.0)

    def test_record_boundary(self):
        case=MASTER.REFERENCE_CASES[10]
        master=MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k!='what_it_tests'})
        self.assertEqual(master.warmup_bars,251)
        for price in INPUTS[:-1]:self.assertTrue(all(math.isnan(v) for v in master.update(price)))
        self.assertTrue(all(math.isfinite(v) for v in master.update(INPUTS[-1])))

    def test_single_period_and_loop_boundaries(self):
        master=MASTER.MASTER_CLASS(min_period=20,max_period=20)
        for price in INPUTS:output=master.update(price)
        self.assertEqual(output.dominant_cycle,20.0)
        if KIND=='bp':self.assertEqual(output.tuned_period,18.0)
        else:self.assertEqual(output.lookback_length,10.0 if KIND=='rsi' else 20.0)
        for dc in (10.0,10.1,10.9999999999,11.0,47.99,48.0):
            self.assertEqual(MASTER._inclusive_cycle_length(dc),math.floor(dc))

    def test_source_specific_history_or_trigger(self):
        master=MASTER.MASTER_CLASS()
        if KIND=='bp':
            previous=0.0
            for i,price in enumerate(INPUTS):
                master.update(price)
                self.assertEqual(master.state.trigger,.9*previous)
                if i<2:self.assertEqual(master.state.band_pass,0.0)
                previous=master.state.signal
            self.assertNotEqual(master.state.lead_signal,master.state.trigger)
        elif KIND=='cci':
            self.assertEqual(master.warmup_bars,94)
            for price in INPUTS:master.update(price)
            history=master._cycle.history;dc=master.state.cycle.dominant_cycle
            expected_mean=sum(history[:master.state.lookback_length])/dc
            self.same(master.state.mean,expected_mean)
            wrong=math.sqrt(sum((v-master.state.mean)**2 for v in history[:master.state.lookback_length])/dc)
            self.assertGreater(abs(master.state.rms-wrong),1e-4)
        elif KIND=='rsi':
            # The guarded output holds when previous denominator is zero.
            master.update(0.0);master.update(1.0)
            self.assertEqual(master.state.value,0.0)
            master.update(2.0)
            self.assertNotEqual(master.state.value,0.0)
        else:
            master.update(0.0)
            self.assertEqual(master.state.raw_ratio,0.0)
            self.assertEqual(master.state.value,0.0)
            # On the first nonflat observation, previous Stoc is the zero
            # source seed, not an inserted neutral .5.
            fresh=MASTER.MASTER_CLASS()
            fresh.update(91.5)
            self.assertEqual(fresh.state.raw_ratio,1.0)
            self.same(fresh.state.value,fresh._cycle.roof.ss1/2.0)

    def test_invalid_parameters(self):
        cases=[dict(min_period=5),dict(max_period=9),dict(averaging_length=1),
               dict(averaging_length=-1),dict(smoothing_period=1),dict(highpass_period=4),
               dict(min_period=True),dict(smoothing_period=math.nan)]
        if KIND=='bp':cases.extend([dict(bandwidth=0),dict(bandwidth=2.25)])
        for kwargs in cases:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):MASTER.MASTER_CLASS(**kwargs)

    def test_dynamic_period_and_window_changes(self):
        master=MASTER.MASTER_CLASS()
        periods=[];lengths=[]
        for price in INPUTS:
            output=master.update(price)
            if master.is_primed:
                self.assertTrue(10<=output.dominant_cycle<=48)
                periods.append(output.dominant_cycle)
                if KIND!='bp':lengths.append(output.lookback_length)
        self.assertTrue(any(abs(v-round(v))>1e-6 for v in periods))
        if KIND!='bp':self.assertGreater(len(set(lengths)),3)


if __name__=='__main__':unittest.main()
