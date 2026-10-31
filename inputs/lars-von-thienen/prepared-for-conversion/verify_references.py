"""Verify saved reference fixtures in Python, Go, TypeScript, Rust, and Zig.

Use --native to additionally compile/load all fixtures with installed Go,
Rust, Zig, and Node (TypeScript stripping). Native probes use only stdlibs,
run from an isolated temporary directory, and do not download dependencies.
No generated indicator or input fixture is modified by this verifier.
"""

from pathlib import Path
import argparse
import ast
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Fixture checks are read-only and should not leave Python cache artifacts.
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent


def python_arrays(path):
    result={}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.List):
            name=node.targets[0].id
            result[name]=[math.nan if isinstance(item,ast.Attribute) else float(ast.literal_eval(item))
                          for item in node.value.elts]
    return result


def other_arrays(path):
    text=path.read_text()
    patterns={
        '.go':r'var\s+(\w+)\s*=\s*\[\]float64\s*\{([^}]+)\}',
        '.ts':r'export const\s+(\w+)\s*:\s*number\[\]\s*=\s*\[([^\]]+)\]',
        '.rs':r'pub fn\s+(\w+)\(\)\s*->\s*Vec<f64>\s*\{\s*vec!\[([^\]]+)\]',
        '.zig':r'pub fn\s+(\w+)\(\)\s*\[252\]f64\s*\{\s*return\s*\.\{([^}]+)\}',
    }
    result={}
    for name,body in re.findall(patterns[path.suffix],text):
        body=re.sub(r'//[^\n]*','',body)
        tokens=[token.strip() for token in body.split(',') if token.strip()]
        result[name]=[math.nan if token in ('math.NaN()','NaN','f64::NAN','nan') else float(token)
                      for token in tokens]
    return result


def identical(left,right):
    return len(left)==len(right) and all((math.isnan(a) and math.isnan(b)) or a==b
                                       for a,b in zip(left,right))


def load_master(folder):
    name='verify_'+folder.name.replace('-','_')
    spec=importlib.util.spec_from_file_location(name,folder/(folder.name+'.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def verify(folder):
    module=load_master(folder)
    if hasattr(module,'DELIVERY_KIND'):
        if (folder/'cycle_core.py').read_bytes() != (ROOT/'cycle_core.py').read_bytes():
            raise AssertionError(f'{folder.name}: standalone numerical core is out of sync')
    arrays=python_arrays(folder/'test_testdata.py')
    parent=python_arrays(ROOT/'test_testdata.py')
    for name,values in parent.items():
        if not identical(arrays[name],values):
            raise AssertionError(f'{folder.name}: changed input {name}')
    # Required check: compare saved 15-digit Python references to their master.
    rows=module.reference_outputs(parent['INPUT_CLOSE'],folder)
    expected={'EXPECTED_'+row[0] for row in rows}
    if {name for name in arrays if name.startswith('EXPECTED_')}!=expected:
        raise AssertionError(f'{folder.name}: missing or extra Python expected arrays')
    for suffix,explanation,parameters,raw in rows:
        saved=arrays['EXPECTED_'+suffix]
        rounded=[math.nan if math.isnan(value) else float(format(value,'.15g')) for value in raw]
        if len(saved)!=252 or not identical(saved,rounded):
            raise AssertionError(f'{folder.name}: saved Python mismatch {suffix}')
        comments=f'# {explanation}\n# {parameters}\nEXPECTED_{suffix}'
        if comments not in (folder/'test_testdata.py').read_text():
            raise AssertionError(f'{folder.name}: missing required two-line comments')
    input_names={
        'INPUT_CLOSE':('testInput','test_input'), 'INPUT_HIGH':('testHigh','test_high'),
        'INPUT_LOW':('testLow','test_low'), 'INPUT_OPEN':('testOpen','test_open'),
    }
    for filename in ('testdata_test.go','testdata.ts','testdata.rs','testdata.zig'):
        path=folder/filename
        translated=other_arrays(path)
        rust=filename.endswith('.rs')
        wanted={}
        for key,names in input_names.items():
            wanted[names[1] if rust else names[0]]=arrays[key]
        for key in expected:
            suffix=key[len('EXPECTED_'):]
            name='expected_'+suffix.lower() if rust else 'expected'+suffix
            wanted[name]=arrays[key]
        if set(translated)!=set(wanted):
            raise AssertionError(f'{folder.name}: {filename} arrays differ: {set(wanted)^set(translated)}')
        for name,values in wanted.items():
            if len(translated[name])!=252 or not identical(translated[name],values):
                raise AssertionError(f'{folder.name}: {filename} value mismatch {name}')
    return len(rows)


def run(command,environment=None):
    completed=subprocess.run(command,text=True,capture_output=True,env=environment)
    if completed.returncode:
        raise RuntimeError(' '.join(map(str,command))+'\n'+completed.stdout+completed.stderr)


def native_probe(folder,workspace):
    """Compile and invoke every exported array; value equality checked above."""
    for tool in ('go','rustc','zig','node'):
        if shutil.which(tool) is None:
            raise RuntimeError(f'--native requested but {tool} is unavailable')
    destination=workspace/folder.name
    destination.mkdir()
    for filename in ('testdata_test.go','testdata.ts','testdata.rs','testdata.zig'):
        shutil.copyfile(folder/filename,destination/filename)
    go_arrays=other_arrays(destination/'testdata_test.go')
    package=folder.name.replace('-','').replace('_','')
    checks='\n'.join(f'    if len({name}) != 252 {{ t.Fatal("{name}") }}' for name in go_arrays)
    go_probe=destination/'probe_test.go'
    go_probe.write_text('package '+package+'\nimport "testing"\nfunc TestFixtureLengths(t *testing.T) {\n'+checks+'\n}\n')
    environment=os.environ.copy()
    environment['GOCACHE']=str(workspace/'go-cache')
    environment['GOPATH']=str(workspace/'go-path')
    environment['GOTOOLCHAIN']='local'
    run(['go','test',str(destination/'testdata_test.go'),str(go_probe)],environment)
    rust_arrays=other_arrays(destination/'testdata.rs')
    rust_checks='\n'.join(f'    assert_eq!(fixture::testdata::{name}().len(),252);' for name in rust_arrays)
    rust_probe=destination/'probe.rs'
    rust_probe.write_text('#![allow(dead_code)]\n#[path="testdata.rs"] mod fixture;\n#[test] fn lengths() {\n'+rust_checks+'\n}\n')
    rust_executable=destination/'rust_probe'
    run(['rustc','--test',str(rust_probe),'-o',str(rust_executable)])
    run([str(rust_executable)])
    zig_arrays=other_arrays(destination/'testdata.zig')
    zig_checks='\n'.join(f'    try std.testing.expectEqual(@as(usize,252),fixture.{name}().len);' for name in zig_arrays)
    zig_probe=destination/'probe.zig'
    zig_probe.write_text('const std = @import("std");\nconst fixture = @import("testdata.zig");\ntest "fixture lengths" {\n'+zig_checks+'\n}\n')
    run(['zig','test',str(zig_probe),'--cache-dir',str(workspace/'zig-cache'),
         '--global-cache-dir',str(workspace/'zig-global-cache')])
    ts_arrays=other_arrays(destination/'testdata.ts')
    node_code='const fixture=await import('+repr((destination/'testdata.ts').as_uri())+');\n'
    node_code+='for (const [name,value] of Object.entries(fixture)) { if(value.length!==252) throw Error(name); }\n'
    node_code+=f'if(Object.keys(fixture).length!=={len(ts_arrays)}) throw Error("missing exports");\n'
    # Node v24 natively strips TypeScript annotation syntax, with no npm install.
    run(['node','--experimental-strip-types','--input-type=module','-e',node_code])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',action='store_true')
    args=parser.parse_args()
    folders=sorted(folder for folder in ROOT.iterdir()
                   if folder.is_dir() and (folder/(folder.name+'.py')).is_file())
    total=0
    with tempfile.TemporaryDirectory(prefix='lvt-reference-check-') as temporary:
        for folder in folders:
            count=verify(folder)
            total+=count
            if args.native:
                native_probe(folder,Path(temporary))
            print(f'{folder.name}: {count} arrays/language verified'+('; native probes passed' if args.native else ''),flush=True)
    print(f'{len(folders)} masters; {total} expected arrays per language; {total*252*5} expected values across five languages')
