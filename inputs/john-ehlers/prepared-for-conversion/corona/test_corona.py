"""Research checks with independent source and physical/synthetic properties.

Run: python3 -m unittest discover -s inputs/john-ehlers/prepared-for-conversion/corona
The tests do not require framework imports or any third-party package.
"""
from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
PREPARED = HERE.parent


def load(name,path):
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module
        spec.loader.exec_module(module)
    return sys.modules[name]


core=load('corona_reference_core', HERE/'corona.py')
generator=load('corona_reference_generator',HERE/'generate_reference.py')
classes={name:generator.load_master(PREPARED/name) for name in generator.INDICATORS}
inputs=generator.read_inputs(PREPARED/'test_testdata.py')


class TestCoronaReference(unittest.TestCase):
    def test_shared_estimator_against_independent_later_source(self):
        # Extract only the pre-existing investigation reconstruction function;
        # it uses separate dictionaries, half-period indices, and state shifts.
        # Do not execute the copied wrappers or rewrite investigation files.
        tree=ast.parse((HERE/'investigate_copied.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='source_estimator')
        namespace={'math':math}
        exec(compile(ast.Module(body=[function],type_ignores=[]),'source_reconstruction','exec'),namespace)
        for prices in (inputs['INPUT_CLOSE'],[(h+l)/2 for h,l in zip(inputs['INPUT_HIGH'],inputs['INPUT_LOW'])]):
            expected=namespace['source_estimator'](prices)
            engine=core.Corona()
            for price,(dc,median,power) in zip(prices,expected):
                actual=engine.update(price)
                self.assertAlmostEqual(actual.dominant_cycle,dc,delta=5e-11)
                self.assertAlmostEqual(actual.dominant_cycle_median,median,delta=5e-11)
                self.assertAlmostEqual(actual.normalization_power,power,delta=5e-11)

    def test_source_startup_and_empty_selection_holds(self):
        engine=core.Corona()
        snapshots=[engine.update(price) for price in inputs['INPUT_CLOSE']]
        self.assertTrue(all(not s.primed and s.maximum_power==0 for s in snapshots[:12]))
        self.assertTrue(snapshots[12].primed)
        holds=0
        for old,new in zip(snapshots,snapshots[1:]):
            if new.selected_bins==0:
                holds+=1
                self.assertEqual(new.dominant_cycle,old.dominant_cycle)
                self.assertFalse(new.has_cycle_estimate)
        self.assertGreater(holds,0)
        self.assertEqual(snapshots[-1].dominant_cycle,11.5)

    def test_shared_and_standalone_consumers_match(self):
        engine=core.Corona()
        standalone=[cls() for cls in classes.values()]
        shared=[cls() for cls in classes.values()]
        for i,price in enumerate(inputs['INPUT_CLOSE']):
            snapshot=engine.update(price)
            for a,b in zip(standalone,shared):
                kw={'high':inputs['INPUT_HIGH'][i],'low':inputs['INPUT_LOW'][i]} if a.__class__.__name__=='CoronaSignalToNoiseRatio' else {}
                out_a=a.update(price,**kw)
                out_b=b.update_from_snapshot(snapshot,**kw)
                self.assertTrue(generator.same_values(tuple(out_a),tuple(out_b)))
        self.assertEqual(engine.sample_count,252)
        with self.assertRaises(ValueError):
            shared[0].update_from_snapshot(snapshot)

    def test_nan_skips_and_snapshot_owns_arrays(self):
        for name,cls in classes.items():
            a,b=cls(),cls()
            for i,price in enumerate(inputs['INPUT_CLOSE'][:50]):
                kw={'bar_range':2.0} if name=='corona-signal-to-noise-ratio' else {}
                if i==25:
                    missing=a.update(math.nan,**kw)
                    self.assertTrue(missing.heatmap.is_empty())
                    self.assertEqual(a.sample_count,25)
                x,y=a.update(price,**kw),b.update(price,**kw)
                self.assertTrue(generator.same_values(tuple(x),tuple(y)))
            x.heatmap.values[0]=-999.0
            x=a.update(102.0,**kw)
            y=b.update(102.0,**kw)
            self.assertTrue(generator.same_values(tuple(x),tuple(y)))

    def test_reject_bad_parameters_and_nonfinite_before_engine_mutation(self):
        for config in ({'min_period':2},{'min_period':True},{'min_period':6.0},
                       {'max_period':6},{'high_pass_cutoff':4},
                       {'decibels_threshold':math.nan},{'decibels_threshold':20},
                       {'max_raster_value':math.inf}):
            with self.assertRaises(ValueError):core.Corona(**config)
        engine=core.Corona()
        for price in inputs['INPUT_CLOSE'][:30]:engine.update(price)
        before=engine.last_snapshot
        for value in (math.inf,-math.inf,1e308):
            with self.assertRaises(ValueError):engine.update(value)
            self.assertIs(engine.last_snapshot,before)
            self.assertEqual(engine.sample_count,30)
        engine.reset()
        self.assertEqual(engine.sample_count,0)
        self.assertIsNone(engine.last_snapshot)

    def test_full_cycle_trend_cancels_sinusoid_and_preserves_linear_displacement(self):
        cls=classes['corona-trend-vigor']
        consumer=cls()
        engine=core.Corona()
        # Fix the measured period at20 to isolate the article's physical
        # statement: subtracting one whole cycle eliminates its oscillation.
        for i in range(120):
            price=100+0.5*i+3*math.sin(core.TWO_PI*i/20)
            snapshot=engine.update(price)._replace(dominant_cycle=20.0,dominant_cycle_median=20.0)
            output=consumer.update_from_snapshot(snapshot)
            if i<20:
                self.assertTrue(output.heatmap.is_empty())
            else:
                self.assertEqual(output.lookback,20.0)
                self.assertAlmostEqual(output.trend_displacement,10.0,delta=1e-12)
        self.assertTrue(consumer.is_primed())
        with self.assertRaises(ValueError):cls(lookback_offset=0.0)

    def test_phase_lead_uses_current_bandpass_and_full_precision_constant(self):
        bandpass=core.AdaptiveBandPass()
        previous_bp=0.0
        for i in range(100):
            cycle=bandpass.update(100+math.sin(core.TWO_PI*i/20),20)
            if i>=2:
                self.assertAlmostEqual(cycle.quadrature,(cycle.band_pass-previous_bp)/(core.TWO_PI/20),delta=1e-14)
                self.assertAlmostEqual(cycle.lead60,0.5*cycle.band_pass+math.sqrt(3)/2*cycle.quadrature,delta=1e-14)
            previous_bp=cycle.band_pass

    def test_constant_and_zero_prices_have_explicit_diagnostics(self):
        for name,cls in classes.items():
            for price in (0.0,100.0):
                instance=cls()
                for _ in range(100):
                    result=instance.update(price,bar_range=2.0) if name=='corona-signal-to-noise-ratio' else instance.update(price)
                self.assertFalse(result.heatmap.is_empty())
                self.assertEqual(result.has_cycle_estimate,0.0)
                if name=='corona-swing-position':
                    self.assertEqual(result.normalized_position,0.5)
                    self.assertEqual(result.swing_position,0.0)
                    self.assertTrue(all(v==20.0 for v in result.heatmap.values))
                if name=='corona-signal-to-noise-ratio':
                    if price>0:
                        self.assertEqual(result.physical_decibels,-math.inf)
                    else:
                        self.assertTrue(math.isnan(result.physical_decibels))
                    self.assertEqual(result.signal_to_noise_ratio,1.0)

    def test_snr_physical_amplitude_ratio_and_source_signal_gain(self):
        cls=classes['corona-signal-to-noise-ratio']
        consumer=cls()
        engine=core.Corona()
        for _ in range(350):
            # Constant measured amplitude2 => source signal steady state4;
            # constant bar height2 => smoothed noise steady state2.
            snapshot=engine.update(100.0)._replace(maximum_power=4.0)
            output=consumer.update_from_snapshot(snapshot,bar_range=2.0)
        self.assertAlmostEqual(output.signal,4.0,delta=1e-12)
        self.assertAlmostEqual(output.noise,2.0,delta=1e-12)
        self.assertAlmostEqual(output.physical_decibels,20*math.log10(2),delta=1e-12)
        self.assertAlmostEqual(output.signal_to_noise_ratio,1+output.physical_decibels+3.5,delta=1e-12)
        zero_noise=cls()
        no_signal=cls()
        # Use a fresh sequence for exact accepted-sample ordering.
        engine=core.Corona()
        for _ in range(50):
            snapshot=engine.update(100.0)
            zero=zero_noise.update_from_snapshot(snapshot._replace(maximum_power=4.0),bar_range=0.0)
            none=no_signal.update_from_snapshot(snapshot,bar_range=0.0)
        self.assertEqual(zero.physical_decibels,math.inf)
        self.assertEqual(zero.signal_to_noise_ratio,11.0)
        self.assertTrue(math.isnan(none.physical_decibels))
        self.assertEqual(none.signal_to_noise_ratio,1.0)

    def test_snr_range_validation_is_atomic_and_equivalent_interfaces(self):
        cls=classes['corona-signal-to-noise-ratio']
        instance=cls()
        for kwargs in ({},{'high':99.,'low':101.},{'bar_range':-1.},
                       {'high':math.inf,'low':100.},{'high':101.,'low':99.,'bar_range':2.}):
            with self.assertRaises(ValueError):instance.update(100.0,**kwargs)
            self.assertEqual(instance.sample_count,0)
            self.assertEqual(instance.corona.sample_count,0)
        self.assertTrue(instance.update(100.,high=math.nan,low=99.).heatmap.is_empty())
        self.assertEqual(instance.corona.sample_count,0)
        a,b=cls(),cls()
        for i,price in enumerate(inputs['INPUT_CLOSE']):
            out_a=a.update(price,high=inputs['INPUT_HIGH'][i],low=inputs['INPUT_LOW'][i])
            out_b=b.update(price,bar_range=inputs['INPUT_HIGH'][i]-inputs['INPUT_LOW'][i])
            self.assertTrue(generator.same_values(tuple(out_a),tuple(out_b)))

    def test_raster_source_geometry_marker_endpoint_and_rounding(self):
        raster=core.Raster(50,-5,5,20)
        raster.update(1.0,0.1,'swing')
        column=raster.column(None)
        self.assertEqual(column.parameter_first,-4.8)
        self.assertEqual(column.parameter_last,5.0)
        self.assertEqual(column.parameter_resolution,0.2)
        self.assertEqual(column.values[-1],0.0)
        self.assertGreater(column.values[0],0.0)
        raster=core.Raster(50,-5,5,20)
        raster.values=[8.0]*50
        raster.update(0.01,0.1,'swing')  # 50*.01=.5; half-up marker1.
        self.assertEqual(raster.values[0],4.0)


if __name__=='__main__':
    unittest.main()
