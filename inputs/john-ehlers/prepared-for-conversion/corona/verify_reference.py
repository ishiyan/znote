"""Read-only verification of every exported scalar/cell across five languages.

This checks actual serialized literals, shapes, output coverage, comments,
warm-up NaNs, input preservation, and hashes, then regenerates the expected
numbers in memory with the streaming masters. No fixture file is rewritten.
Compiler checks are supplementary and described in validation.md.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('corona_reference_generator',HERE/'generate_reference.py')
generator=sys.modules.get(spec.name)
if generator is None:
    generator=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=generator
    spec.loader.exec_module(generator)


def flatten(values):
    for value in values:
        if isinstance(value,(list,tuple)):
            yield from flatten(value)
        else:
            yield value


def language_name(python_name,language):
    suffix=python_name.removeprefix('EXPECTED_')
    return 'expected_'+suffix.lower() if language=='rust' else 'expected'+suffix


def blocks(text,language):
    patterns={
        'go':r'var (expected\w+) = (\[\]\[\]float64|\[\]float64)\{\n(.*?)\n\}',
        'ts':r'export const (expected\w+): (number\[\]\[\]|number\[\]) = \[\n(.*?)\n\];',
        'rust':r'pub fn (expected_\w+)\(\) -> (Vec<Vec<f64>>|Vec<f64>) \{\n    vec!\[\n(.*?)\n    \]\n\}',
        'zig':r'pub fn (expected\w+)\(\) (\[252\](?:\[\d+\])?f64) \{\n    return \.\{\n(.*?)\n    \};\n\}',
    }
    found={}
    for match in re.finditer(patterns[language],text,re.S):
        name,kind,body=match.groups()
        if name in found:
            raise AssertionError(f'duplicate declaration: {name}')
        found[name]=(kind,body)
    return found


def numeric_tokens(body,language):
    for old,new in {
        'math.NaN()':'NaN','math.Inf(1)':'Infinity','math.Inf(-1)':'-Infinity',
        'f64::NAN':'NaN','f64::NEG_INFINITY':'-Infinity','f64::INFINITY':'Infinity',
        'math.inf(f64)':'Infinity','nan':'NaN',
    }.items():
        body=body.replace(old,new)
    # Strip only container syntax; anything else left must be a floating token.
    body=body.replace('vec![','').replace('.{','')
    body=re.sub(r'[\[\]{}\s]','',body)
    return [float(token) for token in body.split(',') if token]


def verify():
    totals={'cases':0,'arrays_per_language':0,'values_per_language':0}
    originals=generator.read_inputs(generator.PREPARED/'test_testdata.py')
    for name in generator.INDICATORS:
        folder=generator.PREPARED/name
        manifest=json.loads((folder/'reference_manifest.json').read_text())
        assert manifest['confirmed_cases']==16
        assert generator.read_inputs(folder/'test_testdata.py')==originals
        records,cases=generator.calculate(folder,generator.load_master(folder),originals)
        python=generator.parsed_expected(folder/'test_testdata.py')
        assert len(python)==manifest['array_count']==len(records)
        assert list(python)==[record['name'] for record in records]
        for record in records:
            actual=python[record['name']]
            assert len(actual)==252
            assert generator.same_values(actual,record['values']),record['name']
            for value in flatten(actual):
                assert not math.isinf(value),'unexpected infinite reference data'
        # Check every unavailable heatmap row and mapped scalar correspond,
        # not merely the reported first available bar.
        for case in cases:
            prefix='EXPECTED_'+case['suffix']+'_'
            scalar={'corona-spectrum':'DOMINANT_CYCLE','corona-swing-position':'SWING_POSITION',
                    'corona-trend-vigor':'TREND_VIGOR','corona-signal-to-noise-ratio':'SIGNAL_TO_NOISE_RATIO'}[name]
            rows=python[prefix+'HEATMAP']
            for row,value in zip(rows,python[prefix+scalar]):
                assert len(row)==case['cells']
                assert all(math.isnan(cell) for cell in row)==math.isnan(value)
            assert next((i+1 for i,row in enumerate(rows) if not math.isnan(row[0])),None)==case['first_available_sample']
        for filename in generator.FILES:
            assert hashlib.sha256((folder/filename).read_bytes()).hexdigest()==manifest['files'][filename]
        pytext=(folder/'test_testdata.py').read_text()
        for filename,language in (('testdata_test.go','go'),('testdata.ts','ts'),('testdata.rs','rust'),('testdata.zig','zig')):
            text=(folder/filename).read_text()
            exported=blocks(text,language)
            assert len(exported)==len(python),(filename,len(exported),len(python))
            for record in records:
                output=language_name(record['name'],language)
                kind,body=exported[output]
                expected=python[record['name']]
                actual=numeric_tokens(body,language)
                flat=list(flatten(expected))
                assert len(actual)==len(flat),(filename,output)
                assert all((math.isnan(a) and math.isnan(b)) or a==b for a,b in zip(actual,flat)),(filename,output)
                assert ('// '+record['purpose']+'\n// '+record['parameter_line']+'\n') in text
                assert ('# '+record['purpose']+'\n# '+record['parameter_line']+'\n') in pytext
                matrix=isinstance(expected[0],(list,tuple))
                if matrix:
                    assert len(body.splitlines())==252
                    assert all(len(numeric_tokens(line,language))==len(expected[0]) for line in body.splitlines())
            original=(generator.PREPARED/filename).read_text()
            expected_prefix=original.rstrip()+'\n\n'
            actual_prefix=text.split('// '+generator.MARKER)[0]
            if language=='go':
                expected_prefix=re.sub(r'\bpackage\s+\w+','package '+name.replace('-',''),expected_prefix,count=1)
                expected_prefix=re.sub(r'(package\s+\w+\n)','\\1\nimport "math"\n',expected_prefix,count=1)
            assert actual_prefix==expected_prefix,filename+' input prefix changed'
        count=sum(len(list(flatten(values))) for values in python.values())
        totals['cases']+=16
        totals['arrays_per_language']+=len(python)
        totals['values_per_language']+=count
        print(f'{name}:16 cases, {len(python)} arrays, {count:,} cells verified in every language.')
    assert totals['cases']==64
    print(json.dumps(totals,sort_keys=True))
    return totals


if __name__=='__main__':
    verify()
