"""Deterministic five-language fixtures for the confirmed64 Corona cases.

Run this script for the full family, or a leaf master with
--generate-reference-data for its16 cases. Standard library only. Python
arrays are written/read/verified FIRST; other language arrays are translated
from those parsed Python literals. Existing input prefixes remain intact.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

PREPARED = Path(__file__).resolve().parent.parent
MARKER = 'BEGIN GENERATED CORONA REFERENCE DATA'
FILES = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
RANGES = ((6, 30), (6, 20), (10, 30), (10, 48))
INDICATORS = {
    'corona-spectrum': 'CoronaSpectrum',
    'corona-swing-position': 'CoronaSwingPosition',
    'corona-trend-vigor': 'CoronaTrendVigor',
    'corona-signal-to-noise-ratio': 'CoronaSignalToNoiseRatio',
}


def literal(node):
    """Parse numeric list expressions without executing an enormous data module."""
    if isinstance(node, (ast.List, ast.Tuple)):
        return [literal(item) for item in node.elts]
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -literal(node.operand)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'math':
        if node.attr == 'nan':
            return math.nan
        if node.attr == 'inf':
            return math.inf
    raise ValueError(f'unsupported fixture expression: {ast.dump(node)}')


def read_arrays(path, prefix):
    arrays = {}
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.startswith(prefix):
                if name in arrays:
                    raise ValueError(f'duplicate {name}')
                arrays[name] = literal(node.value)
    return arrays


def read_inputs(path):
    data = read_arrays(path, 'INPUT_')
    for name in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW', 'INPUT_OPEN'):
        if name not in data or len(data[name]) != 252:
            raise ValueError(f'{path}: {name} must contain252 prices')
    return data


def cases(folder):
    """Deterministic order: HP, period range, then selector/raster variant."""
    result = []
    for hp in (30, 48):
        for minimum, maximum in RANGES:
            for variant in ((6.0, 3.0) if folder == 'corona-spectrum' else (50, 25)):
                params = dict(high_pass_cutoff=hp, min_period=minimum, max_period=maximum)
                suffix = f'H{hp}_PMIN{minimum}_PMAX{maximum}'
                if folder == 'corona-spectrum':
                    params['decibels_threshold'] = variant
                    suffix += f'_DB{int(variant)}'
                    specific = 'Original centroid selection.' if variant == 6 else 'Tighter centroid selection and centroid holds.'
                else:
                    params['raster_length'] = variant
                    suffix += f'_R{variant}'
                    specific = 'Original raster density.' if variant == 50 else 'Coarser raster with consistent source coordinates.'
                range_test = {
                    (6,30): 'Original Corona period range and half-bar spectral channels.',
                    (6,20): 'Reduced upper bound and faster-cycle selection.',
                    (10,30): 'Suppression of short-cycle candidates.',
                    (10,48): 'Extended cycle search beyond the original30-bar range.',
                }[(minimum, maximum)]
                purpose = range_test + ' ' + ('Article detrending. ' if hp == 30 else 'Changed detrending independent of bank bounds. ') + specific
                defaults = 'max_raster_value=20, period_step=0.5, median_window=5, first_bank_sample=13'
                if folder == 'corona-swing-position':
                    defaults += ', display_min=-5, display_max=5, lead_window=51, position_window=21, lead_degrees=60'
                elif folder == 'corona-trend-vigor':
                    defaults += ', display_min=-10, display_max=10, lookback_offset=0'
                elif folder == 'corona-signal-to-noise-ratio':
                    defaults += ', display_min=1, display_max=11, input_ranges=INPUT_HIGH-INPUT_LOW'
                parameter_line = ', '.join(f'{key}={value:g}' for key,value in params.items()) + ', ' + defaults
                result.append(dict(parameters=params, suffix=suffix, purpose=purpose, parameter_line=parameter_line))
    assert len(result) == 16
    return result


def load_master(folder):
    name = folder.name.replace('-', '_') + '_master'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, folder / (folder.name + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return getattr(sys.modules[name], INDICATORS[folder.name])


def calculate(folder, cls, inputs):
    records, manifest_cases = [], []
    for case in cases(folder.name):
        indicator = cls(**case['parameters'])
        outputs = []
        for index, price in enumerate(inputs['INPUT_CLOSE']):
            if folder.name == 'corona-signal-to-noise-ratio':
                outputs.append(indicator.update(price, high=inputs['INPUT_HIGH'][index], low=inputs['INPUT_LOW'][index]))
            else:
                outputs.append(indicator.update(price))
        cells = (len(indicator.corona.periods) if folder.name == 'corona-spectrum' else indicator._raster.length)
        fields = {}
        for field in outputs[0]._fields:
            if field == 'heatmap':
                fields['HEATMAP'] = [list(output.heatmap.values) or [math.nan] * cells for output in outputs]
                fields['HEATMAP_MIN'] = [output.heatmap.value_min for output in outputs]
                fields['HEATMAP_MAX'] = [output.heatmap.value_max for output in outputs]
            else:
                fields[field.upper()] = [getattr(output, field) for output in outputs]
        for field, values in fields.items():
            name = 'EXPECTED_' + case['suffix'] + '_' + field
            records.append(dict(name=name, values=values,
                                purpose=case['purpose'] + f' Output: {field.lower()}.',
                                parameter_line=case['parameter_line']))
        last_heatmap = outputs[-1].heatmap
        manifest_cases.append(dict(**case, cells=cells,
            first_available_sample=next((i+1 for i,out in enumerate(outputs) if out.heatmap.values), None),
            parameter_first=last_heatmap.parameter_first, parameter_last=last_heatmap.parameter_last,
            parameter_resolution=last_heatmap.parameter_resolution,
            outputs=list(fields)))
    return records, manifest_cases


def number(value, language):
    if math.isnan(value):
        return dict(python='math.nan', go='math.NaN()', ts='NaN', rust='f64::NAN', zig='nan')[language]
    if math.isinf(value):
        positive = value > 0
        return dict(python='math.inf' if positive else '-math.inf',
                    go='math.Inf(1)' if positive else 'math.Inf(-1)',
                    ts='Infinity' if positive else '-Infinity',
                    rust='f64::INFINITY' if positive else 'f64::NEG_INFINITY',
                    zig='math.inf(f64)' if positive else '-math.inf(f64)')[language]
    token = format(value, '.15g')
    # Rust/Zig literals in explicitly f64 arrays must also represent0/1 as
    # floating values. Uniform spelling simplifies cross-language verification.
    if '.' not in token and 'e' not in token:
        token += '.0'
    return token


def body(values, language, indent):
    matrix = isinstance(values[0], (list, tuple))
    if matrix:
        result = []
        for row in values:
            tokens = ', '.join(number(value, language) for value in row)
            begin,end = ('{','}') if language == 'go' else ('vec![',']') if language == 'rust' else ('.{','}') if language == 'zig' else ('[',']')
            result.append(indent + begin + tokens + end + ',\n')
        return ''.join(result)
    result = []
    for start in range(0,len(values),6):
        result.append(indent + ', '.join(number(value,language) for value in values[start:start+6]) + ',\n')
    return ''.join(result)


def declaration(record, language):
    values = record['values']
    name = record['name']
    matrix = isinstance(values[0], (list, tuple))
    comments = ('# ' if language == 'python' else '// ')
    prefix = comments + record['purpose'] + '\n' + comments + record['parameter_line'] + '\n'
    suffix = name.removeprefix('EXPECTED_')
    if language == 'python':
        return prefix + name + ' = [\n' + body(values,language,'    ') + ']\n\n'
    if language == 'go':
        kind = '[][]float64' if matrix else '[]float64'
        return prefix + f'var expected{suffix} = {kind}' + '{\n' + body(values,language,'\t') + '}\n\n'
    if language == 'ts':
        kind = 'number[][]' if matrix else 'number[]'
        return prefix + f'export const expected{suffix}: {kind} = [\n' + body(values,language,'    ') + '];\n\n'
    if language == 'rust':
        kind = 'Vec<Vec<f64>>' if matrix else 'Vec<f64>'
        return prefix + f'pub fn expected_{suffix.lower()}() -> {kind}' + ' {\n    vec![\n' + body(values,language,'        ') + '    ]\n}\n\n'
    kind = f'[252][{len(values[0])}]f64' if matrix else '[252]f64'
    return prefix + f'pub fn expected{suffix}() {kind}' + ' {\n    return .{\n' + body(values,language,'        ') + '    };\n}\n\n'


def input_prefix(folder, filename):
    """Remove only this generator's section, preserving original input data."""
    source = (folder/filename).read_text()
    lines = source.splitlines(keepends=True)
    for i,line in enumerate(lines):
        if MARKER in line:
            source = ''.join(lines[:i])
            break
    if filename == 'testdata_test.go':
        source = re.sub(r'\bpackage\s+\w+', 'package ' + folder.name.replace('-','').replace('_',''), source, count=1)
        if 'import "math"' not in source:
            source = re.sub(r'(package\s+\w+\n)', '\\1\nimport "math"\n', source, count=1)
    return source.rstrip() + '\n\n'


def parsed_expected(path):
    arrays = read_arrays(path, 'EXPECTED_')
    if not arrays:
        raise ValueError('Python reference file contains no expected arrays')
    return arrays


def same_values(actual, expected):
    if isinstance(expected, (tuple, list)):
        return isinstance(actual,(tuple,list)) and len(actual)==len(expected) and all(same_values(a,b) for a,b in zip(actual,expected))
    if not isinstance(expected,(int,float)):
        return actual == expected
    return (math.isnan(actual) and math.isnan(expected)) or actual == expected or math.isclose(actual,expected,rel_tol=5e-14,abs_tol=5e-14)


def generate_folder(folder, cls=None):
    folder = folder.resolve()
    inputs = read_inputs(folder/'test_testdata.py')
    original_inputs = read_inputs(PREPARED/'test_testdata.py')
    if inputs != original_inputs:
        raise ValueError('copied inputs differ from prepared-for-conversion originals')
    records, manifest_cases = calculate(folder, cls or load_master(folder), inputs)
    prefix = input_prefix(folder,'test_testdata.py')
    (folder/'test_testdata.py').write_text(prefix + '# ' + MARKER + '\n\n' + ''.join(declaration(record,'python') for record in records))
    # Parse what was actually written, then verify the rounded arrays against
    # full-precision calculations. The other four files use these exact data.
    arrays = parsed_expected(folder/'test_testdata.py')
    if list(arrays) != [record['name'] for record in records]:
        raise ValueError('Python expected array declarations differ')
    for record in records:
        if not same_values(arrays[record['name']],record['values']):
            raise ValueError(f'Python reference mismatch: {record["name"]}')
        record['values'] = arrays[record['name']]

    for filename, language in (('testdata_test.go','go'),('testdata.ts','ts'),('testdata.rs','rust'),('testdata.zig','zig')):
        text = input_prefix(folder,filename) + '// ' + MARKER + '\n\n'
        # Rust's original input functions remain within their existing cfg(test)
        # module. Expected functions form a separate module appended afterward.
        if language == 'rust':
            text += '#[cfg(test)]\n#[allow(non_snake_case)]\npub mod expected_data {\n'
        text += ''.join(declaration(record,language) for record in records)
        if language == 'rust':
            text += '}\n'
        (folder/filename).write_text(text)

    manifest = dict(indicator=folder.name, confirmed_cases=16, input_count=252,
        formatting='15 significant decimal digits, binary64 calculations',
        tolerance=dict(relative=5e-12,absolute=5e-12),
        cases=manifest_cases, array_count=len(records),
        files={filename:hashlib.sha256((folder/filename).read_bytes()).hexdigest() for filename in FILES})
    (folder/'reference_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{folder.name}: verified16 cases, {len(records)} arrays per language,252 rows per array.')
    return manifest


if __name__ == '__main__':
    for name in INDICATORS:
        generate_folder(PREPARED/name)
