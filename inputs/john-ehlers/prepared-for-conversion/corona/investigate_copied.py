"""Read-only numerical audit of severed copied Corona classes.

Only unavailable relative imports are removed. Entity/metadata helpers are
stubbed; all estimator and wrapper calculation bodies execute unchanged.
This is an investigation harness, not a proposed reference implementation.
"""
from __future__ import annotations

import ast
import datetime
import enum
import json
import math
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[4]
COPIED = ROOT / 'external/zpano/py/indicators/john_ehlers'
PREPARED = ROOT / 'inputs/john-ehlers/prepared-for-conversion'


class Component(enum.Enum):
    MEDIAN = 1


def load(path, namespace=None, replacements=()):
    namespace = {} if namespace is None else dict(namespace)
    source = path.read_text()
    for old, new in replacements:
        assert old in source, old
        source = source.replace(old, new)
    tree = ast.parse(source, filename=str(path))
    tree.body = [n for n in tree.body
                 if not (isinstance(n, ast.ImportFrom) and n.level)]
    tree.body.insert(0, ast.ImportFrom(module='__future__',
                                     names=[ast.alias(name='annotations')], level=0))
    namespace.setdefault('__name__', 'corona_audit')
    module = types.ModuleType(namespace['__name__'])
    module.__dict__.update(namespace)
    sys.modules[namespace['__name__']] = module
    exec(compile(ast.fix_missing_locations(tree), str(path), 'exec'), module.__dict__)
    namespace = module.__dict__
    return namespace


base = dict(BarComponent=Component, DEFAULT_QUOTE_COMPONENT=None,
            DEFAULT_TRADE_COMPONENT=None,
            bar_component_value=lambda c: lambda b: (b.high+b.low)/2,
            quote_component_value=lambda c: lambda q: 0,
            trade_component_value=lambda c: lambda t: 0,
            component_triple_mnemonic=lambda *args: ', hl/2')
base.update(load(ROOT / 'external/zpano/py/indicators/core/outputs/heatmap.py'))
base.update(load(COPIED / 'corona/params.py'))
base.update(load(COPIED / 'corona/corona.py', base))
data = load(PREPARED / 'test_testdata.py')
close, highs, lows = data['INPUT_CLOSE'], data['INPUT_HIGH'], data['INPUT_LOW']
median = [(h+l)/2 for h,l in zip(highs,lows)]
names = dict(corona_spectrum='CoronaSpectrum',
             corona_swing_position='CoronaSwingPosition',
             corona_trend_vigor='CoronaTrendVigor',
             corona_signal_to_noise_ratio='CoronaSignalToNoiseRatio')
namespaces = {}
report = {'scope': 'Calculations unchanged; framework imports stubbed.',
          'fixture_input': {}, 'snapshot_checks': {}, 'edge_cases': {},
          'controlled_changes': {}, 'spectrum_source_startup_comparison': {}}


def run(cls, params, prices, bars=None):
    instance = cls(params)
    outputs = []
    for i,price in enumerate(prices):
        time = datetime.datetime(2021,4,1) + datetime.timedelta(minutes=i)
        if cls.__name__ == 'CoronaSignalToNoiseRatio':
            low,high = (price,price) if bars is None else bars[i]
            outputs.append(instance.update(price,low,high,time))
        else:
            outputs.append(instance.update(price,time))
    return instance, outputs


for folder, class_name in names.items():
    ns = load(COPIED / folder / 'params.py', base)
    ns = load(COPIED / folder / (folder+'.py'), ns)
    fixtures = load(COPIED / folder / 'test_testdata.py')
    ns.update(fixtures)
    namespaces[folder] = ns
    inp = fixtures['_test_input']()
    report['fixture_input'][folder] = {
        'count':len(inp), 'max_difference_from_close':max(abs(a-b) for a,b in zip(inp,close)),
        'max_difference_from_high_low_median':max(abs(a-b) for a,b in zip(inp,median))}
    testns = load(COPIED / folder / ('test_'+folder+'.py'), ns)
    suite = unittest.TestSuite()
    for name,obj in testns.items():
        if isinstance(obj,type) and issubclass(obj,unittest.TestCase):
            for method in unittest.defaultTestLoader.getTestCaseNames(obj):
                if 'snapshots' in method or 'primes' in method or 'nan_input' in method:
                    suite.addTest(obj(method))
    result = unittest.TestResult()
    suite.run(result)
    report['snapshot_checks'][folder] = {
        'tests_run':result.testsRun,
        'failures':[(str(test),detail.splitlines()[-1]) for test,detail in result.failures],
        'errors':[(str(test),detail.splitlines()[-1]) for test,detail in result.errors]}

    edge = {}
    for label, prices, bars in [
        ('constant_positive', [100.0]*100, [(99.0,101.0)]*100),
        ('zero', [0.0]*100, [(0.0,0.0)]*100),
        ('close_with_actual_bar_ranges', close, list(zip(lows,highs))),
        ('close_with_zero_ranges', close, None),
        ('infinite_sample', close[:30]+[math.inf]+close[31:],list(zip(lows,highs)))]:
        try:
            instance,out = run(ns[class_name],ns['Params'](),prices,bars)
            last=out[-1]
            edge[label]={'last_scalar':list(last[1:]),'last_heatmap_min':last[0].value_min,
                         'last_heatmap_max':last[0].value_max,
                         'nonfinite_post_warmup_scalar_count':sum(
                             not math.isfinite(v) for x in out[11:] for v in x[1:])}
        except Exception as exc:
            edge[label]={'exception':type(exc).__name__+': '+str(exc)}
    report['edge_cases'][folder]=edge


def controlled(folder,replacements,label):
    ns=namespaces[folder]
    changed=load(COPIED/folder/(folder+'.py'),ns,replacements)
    inp=ns['_test_input']()
    bars=[(v-v*(.005+.03*(1+math.sin(i*.37))),v+v*(.005+.03*(1+math.sin(i*.37))))
          for i,v in enumerate(inp)]
    a,original=run(ns[names[folder]],ns['Params'](),inp,bars)
    b,modified=run(changed[names[folder]],ns['Params'](),inp,bars)
    delta=[abs(x[1]-y[1]) for x,y in zip(original[11:],modified[11:])]
    report['controlled_changes'][label]={
        'input':'copied 252 high-low median prices',
        'max_post_warmup_scalar_difference':max(delta),
        'count_difference_over_1e-10':sum(d>1e-10 for d in delta),
        'original_final_scalar':original[-1][1],
        'modified_final_scalar':modified[-1][1]}


controlled('corona_swing_position',[
    ('_LEAD60_COEF_BP * self._band_pass_previous2 +', '_LEAD60_COEF_BP * band_pass +')],
    'swing_current_bandpass_in_lead_only')
controlled('corona_swing_position',[
    ('_LEAD60_COEF_Q = 0.866','_LEAD60_COEF_Q = math.sqrt(3.0) / 2.0')],
    'swing_full_precision_phase_constant_only')
controlled('corona_swing_position',[
    ('_MAX_LEAD_LIST_COUNT = 50','_MAX_LEAD_LIST_COUNT = 51'),
    ('_MAX_POSITION_LIST_COUNT = 20','_MAX_POSITION_LIST_COUNT = 21')],
    'swing_inclusive_source_windows_only')
controlled('corona_trend_vigor',[
    ('len(self._sample_buffer) - lookback]', 'len(self._sample_buffer) - 1 - lookback]')],
    'trend_fix_extra_ring_buffer_off_by_one_only')

def controlled_estimator(replacements, label):
    modified_ns=load(COPIED/'corona/corona.py',base,replacements)
    original=base['Corona']()
    modified=modified_ns['Corona']()
    differences=[]
    no_selection_count=0
    for i,price in enumerate(median):
        original.update(price);modified.update(price)
        if i>=11:
            differences.append(abs(original.dominant_cycle-modified.dominant_cycle))
            no_selection_count+=not any(f.decibels<=6 for f in original.filter_bank)
    report['controlled_changes'][label]={
        'input':'copied 252 high-low median prices',
        'max_post_warmup_dc_difference':max(differences),
        'count_difference_over_1e-10':sum(d>1e-10 for d in differences),
        'copied_bars_with_no_qualifying_bins':no_selection_count,
        'original_final_dc':original.dominant_cycle,
        'modified_final_dc':modified.dominant_cycle}


controlled_estimator([
    ('self.dominant_cycle = 0.0\n        for index',
     '# Hold the previous centroid when no bins qualify.\n        for index')],
    'estimator_hold_previous_cycle_only')

# Invalid high/low input is accepted by the copied SNR wrapper. Capture its
# eventual contamination with a mixed missing-data sequence.
ns=namespaces['corona_signal_to_noise_ratio']
for label,bars in [('one_nan_high',list(zip(lows,highs))),
                   ('reversed_ranges',list(zip(highs,lows)))]:
    if label=='one_nan_high':bars[30]=(lows[30],math.nan)
    try:
        instance,out=run(ns[names['corona_signal_to_noise_ratio']],ns['Params'](),close,bars)
        report['edge_cases']['corona_signal_to_noise_ratio'][label]={
            'last_scalar':out[-1][1],
            'signal':instance._signal_previous,'noise':instance._noise_previous}
    except Exception as exc:
        report['edge_cases']['corona_signal_to_noise_ratio'][label]={'exception':repr(exc)}

# Reconstruct only the bank/startup of the readable 2012 EasyLanguage listing,
# at full pi precision. This is not an assertion about unavailable 2008 ELD.
def source_estimator(prices):
    alpha=(1-math.sin(2*math.pi/30))/math.cos(2*math.pi/30)
    hp=[0.0]*6
    bank=[dict(i=0.,i1=0.,i2=0.,q=0.,q1=0.,q2=0.,r=0.,r1=0.,r2=0.,
               im=0.,im1=0.,im2=0.,power=0.,db=0.) for _ in range(49)]
    prev=prices[0];smoothprev=0.;dc=0.;dc_history=[0.]*5
    outputs=[]
    for bar,price in enumerate(prices,1):
        hpcur=.5*(1+alpha)*(price-prev)+alpha*hp[-1]
        hp=hp[1:]+[hpcur]
        smooth=sum(x*y for x,y in zip(hp,[1,2,3,3,2,1]))/12
        if bar<7:smooth=price-prev
        if bar==1:smooth=0.
        delta=max(.1,.5-.015*bar)
        if bar>12:
            for index,f in enumerate(bank):
                n=index+12
                beta=math.cos(4*math.pi/n)
                gamma=1/math.cos(8*math.pi*delta/n)
                a=gamma-math.sqrt(gamma*gamma-1)
                f['i']=smooth
                f['q']=n/(4*math.pi)*(smooth-smoothprev)
                f['r']=.5*(1-a)*(f['i']-f['i2'])+beta*(1+a)*f['r1']-a*f['r2']
                f['im']=.5*(1-a)*(f['q']-f['q2'])+beta*(1+a)*f['im1']-a*f['im2']
                f['power']=f['r']**2+f['im']**2
        for f in bank:
            for prefix in ('i','q','r','im'):
                f[prefix+'2']=f[prefix+'1'];f[prefix+'1']=f[prefix]
        # In this 2012 listing, max power has a .01 fallback only at zero.
        maxpower=max(bank[0]['power'] or .01, max(f['power'] for f in bank))
        numerator=denominator=0.
        for index,f in enumerate(bank):
            old=f['db']
            raw=old
            if f['power']/maxpower>0:
                raw=10*math.log10((1-.99*f['power']/maxpower)/.01)
            f['db']=min(20.,.33*raw+.67*old)
            if f['db']<=6:
                numerator+=(index+12)*(20-f['db']);denominator+=20-f['db']
        if denominator:dc=.5*numerator/denominator
        dc_history=dc_history[1:]+[dc]
        dcm=max(6.,sorted(dc_history)[2])
        outputs.append((dc,dcm,maxpower))
        prev=price;smoothprev=smooth
    return outputs


for label, prices in [('close',close),('median',median)]:
    copied=base['Corona']()
    actual=[]
    for price in prices:
        copied.update(price)
        actual.append((copied.dominant_cycle,copied.dominant_cycle_median,
                       copied.maximal_amplitude_squared))
    src=source_estimator(prices)
    report['spectrum_source_startup_comparison'][label]={
        'source':'2012 local Corona Chart Swing Position.eqi; full pi',
        'max_dc_difference_from_index_12':max(abs(a[0]-b[0]) for a,b in zip(actual[12:],src[12:])),
        'max_dcm_difference_from_index_12':max(abs(a[1]-b[1]) for a,b in zip(actual[12:],src[12:])),
        'snapshots':[{'index':i,'copied':actual[i],'source':src[i]} for i in [11,12,50,100,150,200,251]]}

report['parameter_boundaries']={}
for period in (2,3,4,6):
    try:
        corona=base['Corona'](base['CoronaParams'](minimal_period=period))
        for i in range(150):corona.update(100+math.sin(2*math.pi*i/20))
        report['parameter_boundaries'][str(period)]={
            'max_amplitude_squared':corona.maximal_amplitude_squared,
            'dc':corona.dominant_cycle}
    except Exception as exc:
        report['parameter_boundaries'][str(period)]={'exception':repr(exc)}

# Rounded-marker direction is valid for finite normalized values. In particular,
# rounding alone does not produce negative fractional-power arguments.
negative_count=0
for k in range(10001):
    position=k/10000
    marker=round(50*position)
    for index in range(50):
        if index==marker:continue
        argument=20*position-.4*index
        if index>marker:argument=-argument
        negative_count+=argument<0
report['raster_direction_check']={'grid_values':10001,'negative_arguments':negative_count}

def json_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        return 'NaN' if math.isnan(value) else ('Infinity' if value > 0 else '-Infinity')
    if isinstance(value, dict):
        return {key: json_finite(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_finite(item) for item in value]
    return value


path = pathlib.Path(__file__).with_name('investigation_results.json')
path.write_text(json.dumps(json_finite(report), indent=2, allow_nan=False)+'\n')
print(f'Wrote {path}')
print('Copied wrapper checks: 12 run; '
      f"{sum(len(v['failures'])+len(v['errors']) for v in report['snapshot_checks'].values())} failed.")
