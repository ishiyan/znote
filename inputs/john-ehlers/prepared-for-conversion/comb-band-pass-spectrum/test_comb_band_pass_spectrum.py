"""Behavior and independent book-listing transcription checks, standard library only.

Run python3 -m unittest discover -s THIS_FOLDER -p test_comb_band_pass_spectrum.py.
The oracle uses full-length time series and one-based EL arrays, unlike the
bounded streaming buffers. It never invokes the master's numerical helpers.
"""
import importlib.util
import math
from pathlib import Path
import unittest

DIRECTORY = Path(__file__).resolve().parent
SLUG = DIRECTORY.name
SPEC = importlib.util.spec_from_file_location('book_heatmap_master', DIRECTORY/(SLUG+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_arrays(DIRECTORY/'test_testdata.py')['INPUT_CLOSE']
IS_CORR = SLUG == 'roofed-autocorrelation-heatmap'
IS_COMB = SLUG == 'comb-band-pass-spectrum'


class ListingOracle:
    """Separate direct translation of source listings with zero EL prehistory.

    Source indices are one-based for the comb matrix, zero-based historical
    lookup for variable series. Full histories make the shift/recurrence
    comparison meaningful. Emulates the supplied constants at full precision.
    """
    def __init__(self, params):
        self.p = params
        self.prices, self.hp, self.filt = [], [], []
        self.max_power = self.dominant = 0.0
        self.identified = False
        if IS_CORR:
            self.corr = [0.0]*(params.max_lag+1)
        else:
            self.periods = range(params.min_period, params.max_period+1)
            self.bp = {period: [0.0]*(params.max_period+1) for period in self.periods}

    @staticmethod
    def previous(series, lag):
        return series[-1-lag] if len(series) > lag else 0.0

    def update(self, price):
        p = self.p
        # These coefficients and equations are copied from the book rather
        # than fetched from _Roof or another numerical implementation.
        theta = math.sqrt(2.0)*math.pi/p.highpass_period
        alpha = (math.cos(theta)+math.sin(theta)-1.0)/math.cos(theta)
        h = ((1.0-alpha/2.0)*(1.0-alpha/2.0)
             *(price-2.0*self.previous(self.prices,0)+self.previous(self.prices,1))
             +2.0*(1.0-alpha)*self.previous(self.hp,0)
             -(1.0-alpha)*(1.0-alpha)*self.previous(self.hp,1))
        a1 = math.exp(-math.sqrt(2.0)*math.pi/p.smoothing_period)
        c2 = 2.0*a1*math.cos(math.sqrt(2.0)*math.pi/p.smoothing_period)
        c3 = -a1*a1
        c1 = 1.0-c2-c3
        f = (c1*(h+self.previous(self.hp,0))/2.0
             +c2*self.previous(self.filt,0)+c3*self.previous(self.filt,1))
        self.prices.append(price)
        self.hp.append(h)
        self.filt.append(f)
        if IS_CORR:
            for lag in range(p.max_lag+1):
                m = p.averaging_length if p.averaging_length else lag
                sx = sy = sxx = sxy = syy = 0.0
                for count in range(m):
                    x = self.previous(self.filt,count)
                    y = self.previous(self.filt,lag+count)
                    sx += x
                    sy += y
                    sxx += x*x
                    sxy += x*y
                    syy += y*y
                denominator = (m*sxx-sx*sx)*(m*syy-sy*sy)
                if denominator > 0:
                    self.corr[lag] = (m*sxy-sx*sy)/math.sqrt(denominator)
                self.corr[lag] = .5*(self.corr[lag]+1)
            return self.corr[p.min_lag:p.max_lag+1], None, h, f
        powers = {}
        for period in self.periods:
            comp = period if p.spectral_dilation_compensation else 1.0
            if IS_COMB:
                row = self.bp[period]
                # Exactly source matrix indices M=max DownTo 2, current=1.
                for m in range(p.max_period,1,-1):
                    row[m] = row[m-1]
                if len(self.prices) > 12:
                    beta = math.cos(2.0*math.pi/period)
                    gamma = 1.0/math.cos(2.0*math.pi*p.bandwidth/period)
                    pole = gamma-math.sqrt(gamma*gamma-1.0)
                    row[1] = (.5*(1.0-pole)*(f-self.previous(self.filt,2))
                              +beta*(1.0+pole)*row[2]-pole*row[3])
                powers[period] = 0.0
                for m in range(1,period+1):
                    powers[period] += (row[m]/comp)*(row[m]/comp)
            else:
                cosine = sine = 0.0
                for n in range(p.window_length):
                    value = self.previous(self.filt,n)
                    cosine += value*math.cos(2.0*math.pi*n/period)/comp
                    sine += value*math.sin(2.0*math.pi*n/period)/comp
                powers[period] = cosine*cosine+sine*sine
        self.max_power = .995*self.max_power
        for period in self.periods:
            if powers[period] > self.max_power:
                self.max_power = powers[period]
        for period in self.periods:
            powers[period] = powers[period]/self.max_power if self.max_power else 0.0
        sp = spx = 0.0
        for period in self.periods:
            if powers[period] >= .5:
                spx += period*powers[period]
                sp += powers[period]
        if sp:
            self.dominant = spx/sp
            self.identified = True
        values = [powers[period]**3 if p.enhance_resolution else powers[period]
                  for period in self.periods]
        return values, self.dominant if self.identified else math.nan, h, f


class MasterTests(unittest.TestCase):
    def same_number(self, actual, expected):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertTrue(math.isclose(actual,expected,rel_tol=2e-11,abs_tol=2e-11),
                            f'{actual} versus {expected}')

    def test_all_confirmed_cases_against_source_transcription(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                params = {k:v for k,v in case.items() if k != 'what_it_tests'}
                indicator = MASTER.MASTER_CLASS(**params)
                oracle = ListingOracle(indicator.parameters)
                for i, price in enumerate(INPUTS):
                    result = indicator.update(price)
                    values, dominant, h, f = oracle.update(price)
                    self.same_number(indicator.state.high_pass,h)
                    self.same_number(indicator.state.filtered,f)
                    heatmap = result if IS_CORR else result.heatmap
                    self.assertEqual(heatmap.is_empty(),i < indicator.warmup_bars)
                    if heatmap.is_empty():
                        self.assertTrue(math.isnan(heatmap.value_min))
                        self.assertTrue(math.isnan(heatmap.value_max))
                        if not IS_CORR:
                            self.assertTrue(math.isnan(result.dominant_cycle))
                        continue
                    self.assertEqual(len(heatmap.values),len(values))
                    for actual, expected in zip(heatmap.values,values):
                        self.same_number(actual,expected)
                    self.same_number(heatmap.value_min,min(values))
                    self.same_number(heatmap.value_max,max(values))
                    if not IS_CORR:
                        self.same_number(result.dominant_cycle,dominant)

    def test_missing_infinity_and_overflow_preserve_state(self):
        indicator = MASTER.MASTER_CLASS()
        control = MASTER.MASTER_CLASS()
        for price in INPUTS[:120]:
            indicator.update(price)
            control.update(price)
        state, last, count = indicator.state, indicator.output, indicator.samples_seen
        result = indicator.update(math.nan,'missing')
        self.assertTrue((result if IS_CORR else result.heatmap).is_empty())
        self.assertEqual(result.time if IS_CORR else result.heatmap.time,'missing')
        for value in (math.inf,-math.inf,True,1e308):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual(indicator.state,state)
            self.assertIs(indicator.output,last)
            self.assertEqual(indicator.samples_seen,count)
        actual, expected = indicator.update(INPUTS[120]),control.update(INPUTS[120])
        self.assertEqual(actual,expected)

    def test_owned_snapshot_and_reset_replay(self):
        indicator = MASTER.MASTER_CLASS()
        outputs = [indicator.update(price) for price in INPUTS]
        last = outputs[-1] if IS_CORR else outputs[-1].heatmap
        snapshot = last.values.copy()
        indicator.update(101.0)
        self.assertEqual(last.values,snapshot)
        # Changing a returned list cannot alter internal state.
        last.values[0] = -999.0
        control = MASTER.MASTER_CLASS()
        for price in INPUTS+[101.0]:
            control.update(price)
        self.assertEqual(indicator.update(102.0),control.update(102.0))
        indicator.reset()
        replay = [indicator.update(price) for price in INPUTS]
        original = MASTER.MASTER_CLASS()
        reference = [original.update(price) for price in INPUTS]
        for a,b in zip(replay,reference):
            ma,mb = (a,b) if IS_CORR else (a.heatmap,b.heatmap)
            self.assertEqual(ma.values,mb.values)
            if not ma.is_empty():
                self.assertEqual(a,b)

    def test_zero_input_and_published_degenerate_branch(self):
        indicator = MASTER.MASTER_CLASS()
        for i in range(indicator.warmup_bars+4):
            result = indicator.update(0.0)
        heatmap = result if IS_CORR else result.heatmap
        self.assertTrue(indicator.is_primed)
        if IS_CORR:
            self.assertTrue(all(v == 1.0 for v in heatmap.values))
            short = MASTER.MASTER_CLASS(min_lag=0,max_lag=3,averaging_length=1)
            for n in range(1,9):
                short.update(float(n))
                self.assertEqual(short.state.correlations,(1.0-2.0**(-n),)*4)
        else:
            self.assertEqual(heatmap.values,[0.0]*len(heatmap.values))
            self.assertTrue(math.isnan(result.dominant_cycle))
            self.assertEqual(indicator.state.normalization_maximum,0.0)

    def test_single_bin_and_record_boundary(self):
        case = MASTER.REFERENCE_CASES[-1]
        indicator = MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
        outputs = [indicator.update(price) for price in INPUTS]
        if not IS_CORR:
            boundary_index = 6 if not IS_COMB else 11
            boundary_case = MASTER.REFERENCE_CASES[boundary_index]
            boundary = MASTER.MASTER_CLASS(**{k:v for k,v in boundary_case.items() if k != 'what_it_tests'})
            results = [boundary.update(price) for price in INPUTS]
            self.assertEqual(boundary.warmup_bars,251)
            self.assertTrue(all(r.heatmap.is_empty() for r in results[:-1]))
            self.assertFalse(results[-1].heatmap.is_empty())
            single = MASTER.MASTER_CLASS(min_period=20,max_period=20)
            result = None
            for price in INPUTS:
                result = single.update(price)
                if not math.isnan(result.dominant_cycle):
                    self.same_number(result.dominant_cycle,20.0)
        else:
            self.assertEqual(indicator.warmup_bars,2)
            self.assertEqual(len(outputs[-1].values),1)
            self.same_number(outputs[-1].values[0],1.0)

    def test_invalid_parameters(self):
        cases = [{'highpass_period':4},{'smoothing_period':1},{'max_period':True}]
        if IS_CORR:
            cases[-1] = {'max_lag':True}
            cases.extend([{'min_lag':-1},{'max_lag':2},{'averaging_length':-1}])
        else:
            cases.extend([{'min_period':2},{'max_period':9},
                          {'spectral_dilation_compensation':1},{'enhance_resolution':'yes'}])
            cases.extend([{'bandwidth':0},{'bandwidth':2.5}] if IS_COMB else [{'window_length':1}])
        for kwargs in cases:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                MASTER.MASTER_CLASS(**kwargs)

    def test_source_gate_or_lag_zero_or_fourier_compensation(self):
        if IS_CORR:
            indicator = MASTER.MASTER_CLASS(min_lag=0,max_lag=0,averaging_length=0)
            self.assertEqual(indicator.update(100.0).values,[0.5])
            self.assertEqual(indicator.update(100.0).values,[0.75])
        elif IS_COMB:
            indicator = MASTER.MASTER_CLASS()
            for price in INPUTS[:12]:
                indicator.update(price)
                self.assertTrue(all(v == 0.0 for row in indicator.band_pass_history for v in row))
            indicator.update(INPUTS[12])
            self.assertTrue(any(row[0] != 0.0 for row in indicator.band_pass_history))
        else:
            compensated = MASTER.MASTER_CLASS()
            plain = MASTER.MASTER_CLASS(spectral_dilation_compensation=False)
            for price in INPUTS:
                compensated.update(price)
                plain.update(price)
            for i,period in enumerate(range(10,49)):
                self.same_number(compensated.state.raw_power[i],plain.state.raw_power[i]/(period*period))

    def test_display_enhancement_never_changes_centroid(self):
        if IS_CORR:
            # Axis selection does not retune the independent roof or change
            # any internal correlations, only the width of the public output.
            full = MASTER.MASTER_CLASS()
            compact = MASTER.MASTER_CLASS(min_lag=10,max_lag=48)
            for price in INPUTS:
                full.update(price)
                compact.update(price)
            self.assertEqual(full.state,compact.state)
            self.assertEqual(full.output.values[7:],compact.output.values)
        else:
            plain = MASTER.MASTER_CLASS()
            enhanced = MASTER.MASTER_CLASS(enhance_resolution=True)
            for price in INPUTS:
                a,b = plain.update(price),enhanced.update(price)
                self.assertEqual(plain.state,enhanced.state)
                self.same_number(a.dominant_cycle,b.dominant_cycle)
                if not a.heatmap.is_empty():
                    for x,y in zip(a.heatmap.values,b.heatmap.values):
                        self.same_number(y,x*x*x)

    def test_sine_wave_known_correlation_or_selected_period(self):
        if IS_CORR:
            indicator = MASTER.MASTER_CLASS(min_lag=0,max_lag=40,averaging_length=20)
            for i in range(1000):
                result = indicator.update(math.sin(2.0*math.pi*i/20.0))
            # Full-cycle Pearson of any roofed settled sinusoid is cosine lag.
            for lag,actual in enumerate(result.values):
                self.same_number(actual,.5*(1.0+math.cos(2.0*math.pi*lag/20.0)))
        else:
            kwargs = {} if IS_COMB else {'window_length':120}
            indicator = MASTER.MASTER_CLASS(**kwargs)
            for i in range(1000):
                result = indicator.update(math.sin(2.0*math.pi*i/20.0))
            peak = max(range(len(result.heatmap.values)),key=result.heatmap.values.__getitem__)+10
            self.assertTrue(abs(peak-20) <= (2 if IS_COMB else 1),peak)
            self.assertTrue(17 < result.dominant_cycle < 23,result.dominant_cycle)


if __name__ == '__main__':
    unittest.main()
