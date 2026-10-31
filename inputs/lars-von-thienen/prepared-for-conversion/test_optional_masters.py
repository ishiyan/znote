"""Independent mathematical, calendar and CLI checks for the seven additions."""
import importlib.util
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from itertools import combinations

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('optional_test_core', ROOT/'cycle_core.py')
c = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = c
spec.loader.exec_module(c)


def coherent(n=240):
    return [100+4*math.sin(2*math.pi*i/12+0.4)+2*math.sin(2*math.pi*i/30-0.7)
            for i in range(n)]


def independent_correlation(a, b):
    am, bm = sum(a)/len(a), sum(b)/len(b)
    numerator = sum((x-am)*(y-bm) for x,y in zip(a,b))
    denominator = math.sqrt(sum((x-am)**2 for x in a)*sum((y-bm)**2 for y in b))
    return numerator/denominator


def handcrafted(year, n=252, amplitude=2.0, phase=0.3):
    return dict(schema='lvt-annual-cycle-model', version=1, year=year,
                sample_count=n, phase_convention='sine radians at ordinal zero',
                components=[dict(period=21.0, amplitude=amplitude, phase=phase)])


class ScannerTests(unittest.TestCase):
    def test_spectrum_matches_direct_dft(self):
        data = coherent(120)
        config = c.ScanConfig(120, 5, 45, 0, 49, 0)
        result = c.scan_cycles(data, config)
        for p, observed in zip(range(5,46), result.spectrum.values):
            real = sum(value*math.cos(2*math.pi*i/p) for i,value in enumerate(data))
            imaginary = -sum(value*math.sin(2*math.pi*i/p) for i,value in enumerate(data))
            self.assertAlmostEqual(observed, 2*math.sqrt(real**2+imaginary**2)/len(data), places=10)

    def test_strength_dominates_amplitude(self):
        data = [4*math.sin(2*math.pi*i/10)+9*math.sin(2*math.pi*i/40) for i in range(200)]
        config = c.ScanConfig(200, 8, 45, 0, 49, 0, 3)
        result = c.scan_cycles(data, config)
        self.assertEqual(result.cycles[0].period, 10)
        self.assertAlmostEqual(result.cycles[0].strength, 0.4, places=12)
        self.assertGreater(max(result.spectrum.values), result.cycles[0].amplitude)

    def test_threshold_zero_energy_and_insufficient_evidence(self):
        rejected = c.scan_cycles(coherent(), c.ScanConfig(240,5,45,0,100))
        self.assertEqual(rejected.accepted_count, 0)
        self.assertTrue(all(math.isnan(wave.period) for wave in rejected.cycles))
        self.assertTrue(all(math.isfinite(value) for value in rejected.spectrum.values))
        zero = c.scan_cycles([0.0]*30, c.ScanConfig(30,5,20))
        self.assertEqual(zero.accepted_count, 0)
        self.assertTrue(math.isnan(zero.genuine_percent[-1]))

    def test_latest_raw_segments_are_the_validation_input(self):
        data = [i*0.5+math.sin(2*math.pi*i/10)*(1+i/100) for i in range(93)]
        result = c.scan_cycles(data, c.ScanConfig(93,10,10,1600))
        # Independent harmonic-vector score on the most recent 5 whole cycles.
        latest = data[-50:]
        vectors = [(sum(latest[10*j+k]*math.sin(2*math.pi*(k+1)/10) for k in range(10)),
                    sum(latest[10*j+k]*math.cos(2*math.pi*(k+1)/10) for k in range(10)))
                   for j in range(5)]
        a, b = sum(x for x,y in vectors)/5, sum(y for x,y in vectors)/5
        energy = sum(x*x+y*y for x,y in vectors)/5
        expected = 100*(1-math.exp(-5*(a*a+b*b)/energy))
        self.assertAlmostEqual(result.genuine_percent[0], expected, places=10)

    def test_recent_phase_and_endpoint_units(self):
        data = [3*math.sin(2*math.pi*i/10+0.3) for i in range(100)]
        result = c.scan_cycles(data, c.ScanConfig(100,10,10,0,49,2,1))
        cycle = result.cycles[0]
        expected_phase = (2*math.pi*99/10+0.3) % (2*math.pi)
        self.assertAlmostEqual(cycle.phase, expected_phase, places=11)
        self.assertEqual(cycle.fit_samples, 20)
        self.assertAlmostEqual(cycle.value, data[-1], places=11)
        self.assertAlmostEqual(cycle.slope, 3*2*math.pi/10*math.cos(expected_phase), places=11)
        self.assertAlmostEqual(c.modeled_value(cycle,cycle.eta_top), 3, places=11)
        self.assertAlmostEqual(c.modeled_value(cycle,cycle.eta_bottom), -3, places=11)

    def test_peak_distance_suppresses_after_strength_ranking(self):
        data = [4*math.sin(2*math.pi*i/10)+9*math.sin(2*math.pi*i/40) for i in range(200)]
        result = c.scan_cycles(data, c.ScanConfig(200,8,45,0,49,0,3,40))
        self.assertEqual(result.accepted_count, 1)
        self.assertEqual(result.cycles[0].period, 10)

    def test_score_extrema_periodicity_and_combined_range(self):
        for phase, expected in [(0,0),(math.pi/2,100),(math.pi,0),(3*math.pi/2,-100)]:
            self.assertAlmostEqual(c.phase_state(phase), expected, places=12)
            self.assertAlmostEqual(c.phase_state(phase+2*math.pi), expected, places=12)
        oscillator = c.PhasingOscillator(120,5,15,16,45,0,49,0)
        for value in coherent(140):
            output = oscillator.update(value-100)
        self.assertTrue(-200 <= output.value <= 200)
        self.assertEqual(output.value, output.short_score+output.long_score)
        with self.assertRaises(ValueError):
            c.PhasingOscillator(short_max=30,long_min=30)

    def test_even_odd_centering_and_causal_highlighter(self):
        prices = [i*i+0.2*i for i in range(100)]
        self.assertAlmostEqual(c.centered_mean(prices,20,5), sum(prices[18:23])/5)
        expected = (sum(prices[18:22])/4+sum(prices[19:23])/4)/2
        self.assertAlmostEqual(c.centered_mean(prices,20,4), expected)
        self.assertTrue(math.isnan(c.centered_mean(prices,0,4)))
        for p in (7,8):
            data = [100+2*math.sin(2*math.pi*i/p) for i in range(100)]
            indicator = c.DynamicCycleExplorer(50,p,p,0,0,0,1)
            for index,price in enumerate(data):
                result = indicator.update(price)
                if index < 49:
                    self.assertTrue(math.isnan(result.highlighter))
                else:
                    center = index-p//2
                    short = max(2,math.floor(p/2+0.5))
                    expected = c.centered_mean(data[:index+1],center,short)-c.centered_mean(data[:index+1],center,p)
                    self.assertEqual(result.highlighter_index, center)
                    self.assertAlmostEqual(result.highlighter, expected)


class AnnualTests(unittest.TestCase):
    def test_exhaustive_subset_matches_independent_enumeration(self):
        rng = random.Random(881)
        waves = [[rng.uniform(-2,2) for _ in range(25)] for _ in range(5)]
        target = [waves[1][i]+waves[4][i]+rng.uniform(-0.01,0.01) for i in range(25)]
        subset, score, count = c.choose_subset(target,waves,[5,7,11,13,17],3)
        scores = []
        for size in range(1,4):
            for selected in combinations(range(5),size):
                total = [sum(waves[j][i] for j in selected) for i in range(25)]
                scores.append((independent_correlation(target,total), selected))
        self.assertEqual(subset, max(scores)[1])
        self.assertEqual(count, 25)
        self.assertAlmostEqual(score,max(scores)[0], places=13)

    def test_exact_two_wave_annual_clone_and_reader(self):
        # Exact coherent amplitude recovery assumes no DC leakage into nearby
        # non-bin candidates; raw preprocessing intentionally does not demean.
        model = c.fit_annual_values([value-100 for value in coherent()],2020,5,45,0,49,10,7)
        self.assertEqual([wave['period'] for wave in model['components']], [12,30])
        self.assertAlmostEqual(model['correlation'],1,places=12)
        reader = c.AnnualWaveReader(model)
        for price in coherent():
            self.assertAlmostEqual(reader.update(),price-100,places=10)
        reader.reset()
        self.assertAlmostEqual(reader.update(),coherent()[0]-100,places=10)

    def test_completed_year_calendar_and_no_lookahead(self):
        dates = c.synthetic_dates(2020,240)
        rows = list(zip(dates,coherent()))
        params = dict(min_period=5,max_period=45,smoothing=0)
        with self.assertRaises(ValueError):
            c.decode_annual(rows,2020,date(2020,12,31),dates,**params)
        with self.assertRaises(ValueError):
            c.decode_annual(rows,2020,date(2021,1,1),**params)
        with self.assertRaises(ValueError):
            c.decode_annual(rows[:100]+rows[101:],2020,date(2021,1,1),dates,**params)
        first = c.decode_annual(rows,2020,date(2021,1,1),dates,**params)
        second = c.decode_annual(rows+[(date(2021,1,4),999999)],2020,date(2021,1,1),dates,**params)
        self.assertEqual(first, second)
        with self.assertRaises(ValueError):
            c.decode_annual(rows[::-1],2020,date(2021,1,1),dates,**params)
        with self.assertRaises(ValueError):
            c.decode_annual(rows[:1]+rows,2020,date(2021,1,1),dates,**params)

    def test_model_schema_and_bounded_fitting(self):
        for changes in [dict(version=2),dict(sample_count=0),
                        dict(phase_convention='cosine'),dict(components=[])]:
            model = dict(handcrafted(2000),**changes)
            with self.assertRaises(ValueError):
                c.validate_annual_model(model)
        for params in [dict(candidate_pool=17),dict(max_components=8)]:
            with self.assertRaises(ValueError):
                c.fit_annual_values(coherent(),2020,**params)
        with self.assertRaises(ValueError):
            c.fit_annual_values([0.0]*100,2020)


class SuperpositionTests(unittest.TestCase):
    def test_source_years_ordinals_and_arithmetic_average(self):
        models = [handcrafted(2021-lag,amplitude=1+j,phase=0.2*j) for j,lag in enumerate(c.METONIC_LAGS)]
        values, model = c.superposition_values(models,2021,252,'none','strict')
        for i,value in enumerate(values):
            expected = sum((1+j)*math.sin(2*math.pi*i/21+0.2*j) for j in range(6))/6
            self.assertAlmostEqual(value,expected,places=13)
        self.assertEqual(model['source_years'], [2013,2010,2002,1994,1991,1983])
        self.assertEqual([2008-lag for lag in c.METONIC_LAGS], [2000,1997,1989,1981,1978,1970])
        with self.assertRaises(ValueError):
            c.superposition_values(models[:-1],2021,252)
        with self.assertRaises(ValueError):
            c.superposition_values(models+[models[0]],2021,252)

    def test_source_normalization_extension_and_manual_inversion(self):
        models = [handcrafted(2021-lag,250,amplitude=j+1,phase=0.1*j) for j,lag in enumerate(c.METONIC_LAGS)]
        values, _ = c.superposition_values(models,2021,252,'rms','extend')
        inverted, _ = c.superposition_values(models,2021,252,'rms','extend',True)
        self.assertEqual(values,[-value for value in inverted])
        shorter, _ = c.superposition_values(models,2021,100,'rms','extend')
        self.assertEqual(values[:100],shorter)
        for i in (0,249,251):
            source = []
            for model in models:
                component = model['components'][0]
                base = [component['amplitude']*math.sin(2*math.pi*k/21+component['phase']) for k in range(250)]
                mean = sum(base)/250
                rms = math.sqrt(sum((v-mean)**2 for v in base)/250)
                source.append((component['amplitude']*math.sin(2*math.pi*i/21+component['phase'])-mean)/rms)
            self.assertAlmostEqual(values[i],sum(source)/6,places=13)
        with self.assertRaises(ValueError):
            c.superposition_values(models,2021,252,'rms','strict')
        reader = c.SuperpositionWaveReader(models,2021,2,'none','extend')
        reader.update()
        reader.update()
        with self.assertRaises(StopIteration):
            reader.update()


class CLITests(unittest.TestCase):
    def command(self, folder, *arguments):
        result = subprocess.run([sys.executable,'-B',str(folder/(folder.name+'.py')),*map(str,arguments)],
                                text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        return result.stdout

    def test_standalone_cli_export_and_frozen_model_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix='lvt-cli-test-') as temporary:
            work = Path(temporary)
            dates = c.synthetic_dates(2020,240)
            prices = work/'prices.csv'
            calendar = work/'calendar.csv'
            prices.write_text('date,close\n'+'\n'.join(f'{day.isoformat()},{value!r}' for day,value in zip(dates,coherent()))+'\n')
            calendar.write_text('date\n'+'\n'.join(day.isoformat() for day in dates)+'\n')
            # Copy the annual directory away from its parent and siblings.
            annual = work/'annual-cycle-pattern-decoder'
            shutil.copytree(ROOT/annual.name,annual)
            model, wave = work/'annual.json', work/'annual.csv'
            self.command(annual,'fit','--input',prices,'--year',2020,'--as-of','2021-01-01',
                         '--calendar',calendar,'--smoothing',0,'--max-period',45,
                         '--model-out',model,'--wave-out',wave)
            replay = work/'replayed.csv'
            self.command(annual,'replay','--model',model,'--wave-out',replay)
            self.assertEqual(wave.read_bytes(),replay.read_bytes())
            report = work/'scan.json'
            series = work/'series.csv'
            for slug in ('complete-cycle-scanner','dominant-market-vibration',
                         'dynamic-cycle-explorer','cycle-phase-score','phasing-oscillator'):
                output = self.command(ROOT/slug,'analyze','--input',prices,'--smoothing',0,
                                      '--max-period',45,'--json-out',report,'--series-out',series,'--horizon',3)
                self.assertEqual(json.loads(output)['schema'],'lvt-cycle-scan')
                projection = json.loads(output)['projection']
                self.assertEqual(len(projection),3)
                if slug=='phasing-oscillator':
                    for point in projection:
                        if point['value'] is not None:
                            self.assertAlmostEqual(point['value'],point['short_score']+point['long_score'])
                            self.assertTrue(-200 <= point['value'] <= 200)
                elif slug=='cycle-phase-score':
                    for point in projection:
                        if point['value'] is not None:
                            self.assertTrue(-100 <= point['value'] <= 100)
                self.assertEqual(len(series.read_text().splitlines()),241)
                # Also cover unprimed rolling output and JSON null handling.
                self.command(ROOT/slug,'analyze','--input',prices,'--rolling','--window',300,
                             '--json-out',report,'--series-out',series)
                self.assertIsNone(json.loads(report.read_text())['output']['value'] if slug!='complete-cycle-scanner'
                                  else json.loads(report.read_text())['output']['accepted_count'])
            self.command(ROOT/'cycle-phase-score','phase','--radians',math.pi/2)
            paths = []
            for j,lag in enumerate(c.METONIC_LAGS):
                p = work/f'model{j}.json'
                c.save_json(p,handcrafted(2021-lag,240))
                paths.append(p)
            target = work/'target.csv'
            target.write_text('date\n'+'\n'.join(day.isoformat() for day in c.synthetic_dates(2021,240))+'\n')
            superposition = ROOT/'harmonic-energy-superposition-wave'
            saved = work/'superposition.json'
            self.command(superposition,'build','--models',*paths,'--target-year',2021,'--calendar',target,
                         '--model-out',saved,'--wave-out',wave)
            self.command(superposition,'replay','--model',saved,'--wave-out',replay)
            self.assertEqual(wave.read_bytes(),replay.read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
