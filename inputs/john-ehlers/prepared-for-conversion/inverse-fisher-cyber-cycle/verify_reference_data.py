"""Verify every exported reference array against the streaming Python master.

This script belongs to the self-contained research folder. It uses only the
standard library and parses fixture literals without executing foreign code.
It checks all five languages' names, comments, dimensions, finite decimals,
NaN masks, and unchanged shared OHLC input sections. Run it after generation.
Actual Go/Rust/Zig/TypeScript compiler/runtime checks complement this parser.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re


DIRECTORY = Path(__file__).resolve().parent
SLUG = DIRECTORY.name
SPEC = importlib.util.spec_from_file_location('reference_master', DIRECTORY/(SLUG+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


def _decode_literal(text, language):
    # Convert only the generator's restricted list-literal grammar. Foreign
    # functions/types are removed before this step, never evaluated as code.
    if language == 'go':
        text = text.replace('math.NaN()', 'None').replace('{', '[').replace('}', ']')
    elif language == 'rs':
        text = text.replace('vec![', '[').replace('f64::NAN', 'None')
    elif language == 'zig':
        text = text.replace('.{', '[').replace('}', ']')
        text = re.sub(r'\bnan\b', 'None', text)
    else:
        text = re.sub(r'\bNaN\b', 'None', text)
    return ast.literal_eval(text)


def _fixture_arrays(language):
    filename = {'py': 'test_testdata.py', 'go': 'testdata_test.go',
                'ts': 'testdata.ts', 'rs': 'testdata.rs', 'zig': 'testdata.zig'}[language]
    full_text = (DIRECTORY/filename).read_text(encoding='utf-8')
    comment = '#' if language == 'py' else '//'
    begin = f'{comment} BEGIN GENERATED {SLUG.upper()} EXPECTED DATA'
    end = f'{comment} END GENERATED {SLUG.upper()} EXPECTED DATA'
    assert full_text.count(begin) == full_text.count(end) == 1, filename
    section = full_text.split(begin, 1)[1].split(end, 1)[0]
    patterns = {
        'py': r'(?m)^# ([^\n]*)\n# ([^\n]*)\n(EXPECTED_\w+) = (\[.*?^\])',
        'go': r'(?m)^// ([^\n]*)\n// ([^\n]*)\nvar (expected\w+) = (?:\[\]){1,2}float64(\{.*?^\})',
        'ts': r'(?m)^// ([^\n]*)\n// ([^\n]*)\nexport const (expected\w+): number(?:\[\]){1,2} = (\[.*?^\]);',
        'rs': r'(?m)^// ([^\n]*)\n// ([^\n]*)\npub fn (expected_\w+)\(\) -> Vec<.*?> \{\n    (vec!\[.*?^    \])\n\}',
        'zig': r'(?m)^// ([^\n]*)\n// ([^\n]*)\npub fn (expected\w+)\(\) \[252\](?:\[\d+\])?f64 \{\n    return (\.\{.*?^    \});\n\}',
    }
    matches = re.findall(patterns[language], section, re.DOTALL)
    arrays = {}
    for description, parameters, name, literal in matches:
        assert name not in arrays, (filename, name)
        arrays[name] = (description, parameters, _decode_literal(literal, language))
    return arrays


def _same(left, right):
    # NaNs from the Python master become None in restricted literal decoding.
    if isinstance(left, list):
        return (isinstance(right, list) and len(left) == len(right)
                and all(_same(a, b) for a, b in zip(left, right)))
    if right is None:
        return left is None or math.isnan(left)
    return left == right


def verify():
    assert MASTER.REFERENCE_CASES_CONFIRMED
    inputs = MASTER._load_arrays(DIRECTORY/'test_testdata.py')
    translated = {language: _fixture_arrays(language) for language in ('py', 'go', 'ts', 'rs', 'zig')}
    names = {language: set() for language in translated}
    total_values = 0
    for case in MASTER.REFERENCE_CASES:
        raw = MASTER._run_reference(case, inputs)
        indicator = MASTER.MASTER_CLASS(**{k: v for k,v in case.items() if k != 'what_it_tests'})
        for component, values in raw.items():
            suffix = MASTER._case_suffix(case)+('_'+component if component else '')
            python_name = 'EXPECTED_'+suffix
            expected = translated['py'][python_name][2]
            # Compare exported decimals to exactly the 15-significant-digit
            # rounding of raw master outputs, not just a broad tolerance.
            rounded = [[None if math.isnan(v) else float(format(v, '.15g')) for v in row]
                       for row in values] if isinstance(values[0], list) else [
                           None if math.isnan(v) else float(format(v, '.15g')) for v in values]
            assert _same(rounded, expected), (python_name, 'incorrect master values')
            assert len(expected) == 252
            if isinstance(values[0], list):
                assert all(len(row) == indicator.max_period-indicator.min_period+1 for row in expected)
                total_values += sum(len(row) for row in expected)
            else:
                total_values += len(expected)
            for language, arrays in translated.items():
                name = python_name if language == 'py' else (
                    'expected_'+suffix.lower() if language == 'rs' else 'expected'+suffix)
                names[language].add(name)
                description, parameters, actual = arrays[name]
                assert description == case['what_it_tests'], (language, name, 'description')
                assert parameters == MASTER._parameter_comment(case), (language, name, 'parameters')
                assert _same(expected, actual), (language, name, 'translated value mismatch')
    for language, arrays in translated.items():
        assert set(arrays) == names[language], (language, 'missing or extra arrays')

    # Preserve every shared OHLC input even in close-only indicators. Strip
    # only known package and NaN import additions, then compare input sections.
    parent = DIRECTORY.parent
    for filename in ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig'):
        text = (DIRECTORY/filename).read_text(encoding='utf-8').split('BEGIN GENERATED', 1)[0]
        # Ignore the trailing marker comment fragment and formatting. Numbers
        # below occur only in the unchanged original OHLC literal sections.
        source_inputs = re.findall(r'-?\d+\.\d+(?:[eE][+-]?\d+)?', text)
        if (parent/filename).exists():
            original_inputs = re.findall(r'-?\d+\.\d+(?:[eE][+-]?\d+)?', (parent/filename).read_text())
            assert source_inputs == original_inputs, (filename, 'input changed')
        assert len(source_inputs) == 4*252, (filename, 'OHLC input count')
    return len(names['py']), total_values


if __name__ == '__main__':
    count, values = verify()
    print(f'{SLUG}: verified {count} arrays, {values} values per language, all five languages agree.')
