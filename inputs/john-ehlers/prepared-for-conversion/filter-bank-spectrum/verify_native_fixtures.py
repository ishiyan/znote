"""Compile and exercise every foreign-language fixture, standard library only.

Run python3 verify_native_fixtures.py, or select --language go/ts/rs/zig.
Requires locally available go, node (with TS stripping), rustc and zig.
Temporary harnesses and compiler caches live outside the research folder.
No package downloads, external libraries, or indicator ports are required.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('fbs_native_master', HERE/'filter-bank-spectrum.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


def manifest():
    arrays = MASTER._load_arrays(HERE/'test_testdata.py')
    # FNV over each binary64 word rather than its decimal text. Canonicalize
    # NaN payloads, since math.NaN()/f64::NAN/math.nan may choose different
    # payload bits. This checks EVERY compiled value, including signed zero.
    digest = 14695981039346656037
    records = []
    total = 0
    input_names = {'INPUT_CLOSE': ('testInput', 'test_input'),
                   'INPUT_HIGH': ('testHigh', 'test_high'),
                   'INPUT_LOW': ('testLow', 'test_low'),
                   'INPUT_OPEN': ('testOpen', 'test_open')}
    for name, values in arrays.items():
        if name.startswith('EXPECTED_'):
            suffix = name.removeprefix('EXPECTED_')
            camel, snake = 'expected'+suffix, 'expected_'+suffix.lower()
        else:
            camel, snake = input_names[name]
        matrix = isinstance(values[0], list)
        width = len(values[0]) if matrix else 0
        records.append((camel, snake, matrix, width))
        flat = [v for row in values for v in row] if matrix else values
        for value in flat:
            bits = (0x7ff8000000000000 if math.isnan(value)
                    else struct.unpack('>Q', struct.pack('>d', value))[0])
            digest = ((digest ^ bits)*1099511628211) & ((1 << 64)-1)
        total += len(flat)
    if len(records) != 76:
        raise ValueError('expected four inputs and 72 generated arrays')
    return records, digest, total


def run_language(language, records, digest, total):
    tool = {'go':'go', 'ts':'node', 'rs':'rustc', 'zig':'zig'}[language]
    if shutil.which(tool) is None:
        raise RuntimeError(f'{tool} is not installed')
    with tempfile.TemporaryDirectory(prefix='filter-bank-spectrum-'+language+'-') as temp:
        folder = Path(temp)
        filename = {'go':'testdata_test.go', 'ts':'testdata.ts',
                    'rs':'testdata.rs', 'zig':'testdata.zig'}[language]
        shutil.copyfile(HERE/filename, folder/filename)
        environment = os.environ.copy()
        calls = []
        if language == 'go':
            for camel, _, matrix, width in records:
                if matrix:
                    calls.append(f'if len({camel}) != 252 {{ t.Fatal("{camel} rows") }}\n'
                                 +f'for _, row := range {camel} {{ consume(row, {width}) }}')
                else:
                    calls.append(f'consume({camel}, 252)')
            source = '''package filterbankspectrum
import ("math"; "testing")
func TestAllFixtureValues(t *testing.T) {
    var hash uint64 = 14695981039346656037
    count := 0
    consume := func(values []float64, length int) {
        if len(values) != length { t.Fatal("incorrect array length") }
        for _, v := range values {
            bits := math.Float64bits(v)
            if math.IsNaN(v) { bits = 0x7ff8000000000000 }
            hash = (hash ^ bits) * 1099511628211
            count++
        }
    }
''' + '\n'.join(calls) + f'''
    if hash != 0x{digest:016x} || count != {total} {{ t.Fatalf("hash=%x count=%d", hash, count) }}
}}
'''
            (folder/'verify_test.go').write_text(source)
            environment.update(GOCACHE=str(folder/'go-cache'), GO111MODULE='off')
            commands = [['go', 'test', '-v']]
        elif language == 'ts':
            for camel, _, matrix, width in records:
                if matrix:
                    calls.append(f'if (data.{camel}.length !== 252) throw new Error("row count");\n'
                                 +f'for (const row of data.{camel}) consume(row, {width});')
                else:
                    calls.append(f'consume(data.{camel}, 252);')
            source = '''import * as data from './testdata.ts';
let hash = 14695981039346656037n;
let count = 0;
const view = new DataView(new ArrayBuffer(8));
function consume(values: number[], length: number) {
    if (values.length !== length) throw new Error('incorrect array length');
    for (const value of values) {
        view.setFloat64(0, value, false);
        const bits = Number.isNaN(value) ? 0x7ff8000000000000n : view.getBigUint64(0, false);
        hash = BigInt.asUintN(64, (hash ^ bits) * 1099511628211n);
        count++;
    }
}
''' + '\n'.join(calls) + f'''
if (hash !== 0x{digest:016x}n || count !== {total}) throw new Error(`hash=${{hash.toString(16)}} count=${{count}}`);
console.log('all TypeScript fixture values verified');
'''
            (folder/'verify.mts').write_text(source)
            commands = [['node', 'verify.mts']]
        elif language == 'rs':
            for _, snake, matrix, width in records:
                if matrix:
                    calls.append(f'let rows = data::{snake}(); assert_eq!(rows.len(), 252);\n'
                                 +f'for row in rows {{ consume(&row, {width}, &mut hash, &mut count); }}')
                else:
                    calls.append(f'consume(&data::{snake}(), 252, &mut hash, &mut count);')
            source = '''#[path = "testdata.rs"] mod fixtures;
use fixtures::testdata as data;
fn consume(values: &[f64], length: usize, hash: &mut u64, count: &mut usize) {
    assert_eq!(values.len(), length);
    for &value in values {
        let bits = if value.is_nan() { 0x7ff8000000000000 } else { value.to_bits() };
        *hash = (*hash ^ bits).wrapping_mul(1099511628211);
        *count += 1;
    }
}
#[test]
fn all_fixture_values() {
    let mut hash: u64 = 14695981039346656037;
    let mut count: usize = 0;
''' + '\n'.join(calls) + f'''
    assert_eq!(hash, 0x{digest:016x});
    assert_eq!(count, {total});
}}
'''
            (folder/'verify.rs').write_text(source)
            commands = [['rustc', '--test', 'verify.rs', '-o', str(folder/'verify-rust')],
                        [str(folder/'verify-rust')]]
        else:
            # Explicitly invoke every function: Zig's lazy compilation would
            # otherwise miss malformed literals in unused expected arrays.
            for camel, _, matrix, width in records:
                if matrix:
                    calls.append(f'{{ const rows = data.{camel}();\n'
                                 +f'for (rows) |row| {{ try consume(&row, {width}, &hash, &count); }} }}')
                else:
                    calls.append(f'{{ const values = data.{camel}(); try consume(&values, 252, &hash, &count); }}')
            source = '''const std = @import("std");
const data = @import("testdata.zig");
fn consume(values: []const f64, length: usize, hash: *u64, count: *usize) !void {
    try std.testing.expectEqual(length, values.len);
    for (values) |v| {
        const bits: u64 = if (std.math.isNan(v)) 0x7ff8000000000000 else @bitCast(v);
        hash.* = (hash.* ^ bits) *% 1099511628211;
        count.* += 1;
    }
}
test "all fixture values" {
    var hash: u64 = 14695981039346656037;
    var count: usize = 0;
''' + '\n'.join(calls) + f'''
    try std.testing.expectEqual(@as(u64, 0x{digest:016x}), hash);
    try std.testing.expectEqual(@as(usize, {total}), count);
}}
'''
            (folder/'verify.zig').write_text(source)
            commands = [['zig', 'test', 'verify.zig', '--cache-dir', str(folder/'zig-cache'),
                         '--global-cache-dir', str(folder/'zig-global-cache')]]
        for command in commands:
            result = subprocess.run(command, cwd=folder, env=environment, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f'{language} verification failed:\n{result.stdout}')
        return f'{language}: compiled and verified {len(records)} arrays, {total} values'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=('go', 'ts', 'rs', 'zig'))
    args = parser.parse_args()
    records, digest, total = manifest()
    languages = [args.language] if args.language else ['go', 'ts', 'rs', 'zig']
    with ThreadPoolExecutor(max_workers=len(languages)) as pool:
        futures = [pool.submit(run_language, language, records, digest, total) for language in languages]
        for future in as_completed(futures):
            print(future.result(), flush=True)
