"""harmonic-energy-superposition-wave: standalone research prototype master and local CLI.
Read description.md for source equations and declared reconstruction choices.
The complete portable numerical implementation is in this folder's cycle_core.py.
"""
import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path

# Load ONLY the colocated core, even when loaded from another working directory.
# Unique module names allow all standalone masters to coexist in test runners.
_spec = importlib.util.spec_from_file_location("lvt_core_harmonic_energy_superposition_wave", Path(__file__).with_name('cycle_core.py'))
_core = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _core
_spec.loader.exec_module(_core)
for _name, _value in vars(_core).items():
    if not _name.startswith('__'):
        globals()[_name] = _value

INDICATOR_SLUG = 'harmonic-energy-superposition-wave'
DELIVERY_KIND = 'model-cli'
MASTER_CLASS = SuperpositionWaveReader
PARAMETER_SHORTCUTS = [('normalization_mode', 'N'), ('calendar_mode', 'C'), ('invert', 'I')]
REFERENCE_CASES = ({'params': {'calendar_mode': 0, 'invert': False, 'normalization_mode': 0},
  'what_it_tests': 'Six SYNTHETIC rotated/scaled INPUT_CLOSE years; raw ordinal average.'},
 {'params': {'calendar_mode': 0, 'invert': False, 'normalization_mode': 1},
  'what_it_tests': 'Source-year mean/RMS normalization with equal-length calendars.'},
 {'params': {'calendar_mode': 0, 'invert': True, 'normalization_mode': 1},
  'what_it_tests': 'Manual inversion negates the normalized six-wave average.'},
 {'params': {'calendar_mode': 1, 'invert': False, 'normalization_mode': 1},
  'what_it_tests': '250-source/252-target ordinal extension and source-only normalization.'})
OUTPUT_FIELDS = ('wave',)


def flatten_output(indicator, output):
    return {"wave":output}
# ---------------------------------------------------------------------------
# Fixture tooling: numerical classes above are the independent porting master.
# No sibling module, third-party package, market API, or network is required.
# ---------------------------------------------------------------------------
import argparse
import ast
import re
from pathlib import Path


def _load_arrays(path):
    """Parse literal fixture arrays without executing arbitrary fixture code."""
    result = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.List):
            continue
        target = node.targets[0]
        if not isinstance(target,ast.Name):
            continue
        values = []
        for item in node.value.elts:
            if isinstance(item,ast.Attribute) and isinstance(item.value,ast.Name) and item.value.id=='math' and item.attr=='nan':
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(item)))
        result[target.id] = values
    return result


def _token(value):
    # Tuple periods are encoded in their supplied order, e.g. P20_40.
    if isinstance(value,(tuple,list)):
        return '_'.join(_token(item) for item in value)
    if type(value) is bool:
        return '1' if value else '0'
    return format(float(value),'g').replace('.','_').replace('-','m').replace('+','')


def _suffix(parameters):
    return '_'.join(shortcut+_token(parameters[name]) for name,shortcut in PARAMETER_SHORTCUTS)


def _literal(value,nan_token):
    # Binary64 calculations are rounded ONCE: serialization, 15 significant digits.
    if math.isnan(value):
        return nan_token
    if not math.isfinite(value):
        raise ValueError("fixture output must be finite or NaN")
    text = format(value,'.15g')
    if '.' not in text and 'e' not in text.lower():
        text += '.0'  # Rust/Zig require explicit floating-point literal types.
    return text


def _rows(values,nan_token,indent):
    literals = [_literal(value,nan_token) for value in values]
    return '\n'.join(indent+', '.join(literals[i:i+6])+',' for i in range(0,len(literals),6))


def _replace_section(path,body,comment,rust=False):
    # Idempotent generated blocks preserve every copied INPUT array.
    begin = comment+' BEGIN GENERATED '+INDICATOR_SLUG.upper()+' EXPECTED DATA'
    end = comment+' END GENERATED '+INDICATOR_SLUG.upper()+' EXPECTED DATA'
    original = path.read_text(encoding='utf-8')
    block = begin+'\n\n'+body.rstrip()+'\n\n'+end
    if begin in original:
        start = original.index(begin)
        stop = original.index(end,start)+len(end)
        result = original[:start]+block+original[stop:]
    elif rust:
        # The root Rust fixtures already contain a cfg(test) module. Keep all
        # generated functions INSIDE it, rather than adding inaccessible peers.
        stop = original.rfind('}')
        result = original[:stop].rstrip()+'\n\n'+block+'\n'+original[stop:]
    else:
        result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result,encoding='utf-8')



def reference_outputs(input_close, directory):
    arrays = _load_arrays(directory/'test_testdata.py')
    if len(input_close)!=252 or list(input_close)!=arrays['INPUT_CLOSE']:
        raise ValueError('expected exact embedded 252 INPUT_CLOSE values')
    outputs = []
    for case in REFERENCE_CASES:
        parameters = case['params']
        if INDICATOR_SLUG == 'annual-cycle-pattern-decoder':
            model = fixture_annual(input_close, **parameters)
            wave = [annual_wave(model,i) for i in range(252)]
            columns = {'wave':wave, 'correlation':[model['correlation']]*252,
                       'component_count':[float(len(model['components']))]*252}
        else:
            models = fixture_historical_models(input_close)
            # Length mismatch is deliberate ONLY in extension reference case.
            if parameters['calendar_mode']==1:
                for model in models:
                    model['sample_count']=250
                    model['dates']=model['dates'][:250]
                    model['end_date']=model['dates'][-1]
                    model['fixture_note']+='; truncated normalization interval to 250'
            wave, model = superposition_values(models,2021,252,
                           'rms' if parameters['normalization_mode'] else 'none',
                           'extend' if parameters['calendar_mode'] else 'strict',
                           parameters['invert'])
            columns = {'wave':wave}
        for field,values in columns.items():
            outputs.append((_suffix(parameters)+'_'+field.upper(),
                            case['what_it_tests']+' Output: '+field+'.',
                            ', '.join(f'{name}={parameters[name]!r}' for name,_ in PARAMETER_SHORTCUTS),
                            values))
    return outputs


def generate_reference_data(input_close,directory):
    outputs = reference_outputs(input_close,directory)
    python_sections = []
    for suffix,explanation,parameters,values in outputs:
        python_sections.append(f'# {explanation}\n# {parameters}\nEXPECTED_{suffix} = [\n'
                               +_rows(values,'math.nan','    ')+'\n]')
    _replace_section(directory/'test_testdata.py','\n\n'.join(python_sections),'#')
    # Read BACK the saved Python decimal literals. All other languages copy
    # these exact saved numbers, not separately computed/re-rounded results.
    saved = _load_arrays(directory/'test_testdata.py')
    if {name for name in saved if name.startswith('EXPECTED_')} != {'EXPECTED_'+row[0] for row in outputs}:
        raise ValueError("saved Python array set differs from the reference")
    sections = {name:[] for name in ('testdata_test.go','testdata.ts','testdata.rs','testdata.zig')}
    for suffix,explanation,parameters,raw in outputs:
        values = saved['EXPECTED_'+suffix]
        if len(values)!=252:
            raise ValueError("saved Python output has wrong length")
        for calculated,stored in zip(raw,values):
            if math.isnan(calculated) and math.isnan(stored):
                continue
            if stored!=float(_literal(calculated,'math.nan')):
                raise ValueError("Python serialization lost the defined precision")
        comments = f'// {explanation}\n// {parameters}\n'
        sections['testdata_test.go'].append(comments+'var expected'+suffix+' = []float64{\n'+_rows(values,'math.NaN()','\t')+'\n}')
        sections['testdata.ts'].append(comments+'export const expected'+suffix+': number[] = [\n'+_rows(values,'NaN','    ')+'\n];')
        sections['testdata.rs'].append(comments+'pub fn expected_'+suffix.lower()+'() -> Vec<f64> {\n    vec![\n'+_rows(values,'f64::NAN','        ')+'\n    ]\n}')
        sections['testdata.zig'].append(comments+'pub fn expected'+suffix+'() [252]f64 {\n    return .{\n'+_rows(values,'nan','        ')+'\n    };\n}')
    go_path = directory/'testdata_test.go'
    go_text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-','').replace('_','')
    go_text = re.sub(r'(?m)^package\s+\w+', 'package '+package,go_text)
    if 'import "math"' not in go_text:
        go_text = go_text.replace('package '+package,'package '+package+'\n\nimport "math"',1)
    if 'math.NaN()' not in '\n'.join(sections['testdata_test.go']) and 'var _ = math.NaN' not in go_text:
        # Go rejects an unused import when every fixture is immediately finite.
        # Retain the requested math import without inserting fabricated NaNs.
        go_text = go_text.replace('import "math"','import "math"\n\nvar _ = math.NaN',1)
    go_path.write_text(go_text,encoding='utf-8')
    zig_path = directory/'testdata.zig'
    zig_text = zig_path.read_text(encoding='utf-8')
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n'+zig_text
    if 'const nan = math.nan(f64);' not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);',1)
    zig_path.write_text(zig_text,encoding='utf-8')
    for filename,parts in sections.items():
        _replace_section(directory/filename,'\n\n'.join(parts),'//',rust=filename.endswith('.rs'))
    return len(outputs)



if __name__ == '__main__':
    # Exact requested 252 input closes, embedded for portable regeneration.
    INPUT_CLOSE = [91.5, 94.815, 94.375, 95.095, 93.78, 94.625, 92.53, 92.75, 90.315, 92.47, 96.125, 97.25, 98.5, 89.875, 91.0, 92.815, 89.155, 89.345, 91.625, 89.875, 88.375, 87.625, 84.78, 83.0, 83.5, 81.375, 84.44, 89.25, 86.375, 86.25, 85.25, 87.125, 85.815, 88.97, 88.47, 86.875, 86.815, 84.875, 84.19, 83.875, 83.375, 85.5, 89.19, 89.44, 91.095, 90.75, 91.44, 89.0, 91.0, 90.5, 89.03, 88.815, 84.28, 83.5, 82.69, 84.75, 85.655, 86.19, 88.94, 89.28, 88.625, 88.5, 91.97, 91.5, 93.25, 93.5, 93.155, 91.72, 90.0, 89.69, 88.875, 85.19, 83.375, 84.875, 85.94, 97.25, 99.875, 104.94, 106.0, 102.5, 102.405, 104.595, 106.125, 106.0, 106.065, 104.625, 108.625, 109.315, 110.5, 112.75, 123.0, 119.625, 118.75, 119.25, 117.94, 116.44, 115.19, 111.875, 110.595, 118.125, 116.0, 116.0, 112.0, 113.75, 112.94, 116.0, 120.5, 116.62, 117.0, 115.25, 114.31, 115.5, 115.87, 120.69, 120.19, 120.75, 124.75, 123.37, 122.94, 122.56, 123.12, 122.56, 124.62, 129.25, 131.0, 132.25, 131.0, 132.81, 134.0, 137.38, 137.81, 137.88, 137.25, 136.31, 136.25, 134.63, 128.25, 129.0, 123.87, 124.81, 123.0, 126.25, 128.38, 125.37, 125.69, 122.25, 119.37, 118.5, 123.19, 123.5, 122.19, 119.31, 123.31, 121.12, 123.37, 127.37, 128.5, 123.87, 122.94, 121.75, 124.44, 122.0, 122.37, 122.94, 124.0, 123.19, 124.56, 127.25, 125.87, 128.86, 132.0, 130.75, 134.75, 135.0, 132.38, 133.31, 131.94, 130.0, 125.37, 130.13, 127.12, 125.19, 122.0, 125.0, 123.0, 123.5, 120.06, 121.0, 117.75, 119.87, 122.0, 119.19, 116.37, 113.5, 114.25, 110.0, 105.06, 107.0, 107.87, 107.0, 107.12, 107.0, 91.0, 93.94, 93.87, 95.5, 93.0, 94.94, 98.25, 96.75, 94.81, 94.37, 91.56, 90.25, 93.94, 93.62, 97.0, 95.0, 95.87, 94.06, 94.62, 93.75, 98.0, 103.94, 107.87, 106.06, 104.5, 105.0, 104.19, 103.06, 103.42, 105.27, 111.87, 116.0, 116.62, 118.28, 113.37, 109.0, 109.7, 109.25, 107.0, 109.19, 110.0, 109.2, 110.12, 108.0, 108.62, 109.75, 109.81, 109.0, 108.75, 107.87]
    directory = Path(__file__).resolve().parent
    parser = make_cli_parser(INDICATOR_SLUG)
    args = parser.parse_args()
    try:
        if args.generate_reference_data:
            count = generate_reference_data(INPUT_CLOSE,directory)
            print(f'{INDICATOR_SLUG}: {len(REFERENCE_CASES)} cases; {count} arrays/language')
        elif args.command:
            run_cli(INDICATOR_SLUG,args,MASTER_CLASS,flatten_output)
        else:
            # No-argument demo computes every reference configuration.
            for suffix,explanation,parameters,values in reference_outputs(INPUT_CLOSE,directory):
                if suffix.endswith(('_WAVE','_VALUE','_PERIOD','_ACCEPTED_COUNT')):
                    print(parameters, suffix, 'last=', values[-1])
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as error:
        parser.exit(2, f'{INDICATOR_SLUG}: {error}'+chr(10))
