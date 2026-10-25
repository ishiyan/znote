"""Compare the master directly with the supplied, unchanged eSignal source.

This optional repository check needs Node and the original MAAF.efs file.
The numerical unit tests remain independent of both requirements. The tip is
run in a stubbed chart context, one completed NEWBAR for each supplied close.
Its high and low both equal close, so its (H+L)/2 input is exactly INPUT_CLOSE.
No source code fixes are injected; nThreshold is assigned as configuration.
"""

import importlib.util
import json
import math
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('maaf_source_master', HERE/(HERE.name+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


def verify():
    source_path = HERE.parent.parent/'tasc/2005-03-whats-the-difference/tips/MAAF.efs'
    data = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']
    payload = json.dumps(dict(source=source_path.read_text(), closes=data,
                              thresholds=[case['threshold'] for case in MASTER.REFERENCE_CASES]))
    harness = r'''
const vm = require('node:vm');
const fs = require('node:fs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = [];
for (const threshold of input.thresholds) {
    let index = 0;
    const ctx = {Color: {red:0}, BARSTATE_NEWBAR:1,
        getBarState:()=>1, setDefaultBarThickness:()=>{}, setDefaultBarFgColor:()=>{},
        high:()=>input.closes[index], low:()=>input.closes[index]};
    vm.createContext(ctx);
    vm.runInContext(input.source, ctx);
    ctx.nThreshold = threshold;
    const values = [];
    for (; index<input.closes.length; index++) {
        const value = ctx.main(2,0);
        values.push([value == null ? null : value, ctx.Value2]);
    }
    result.push(values);
}
console.log(JSON.stringify(result));
'''
    # Data travels over stdin, not shell interpolation or JavaScript eval.
    result = subprocess.run(['node', '-e', harness], input=payload,
                            text=True, check=True, capture_output=True)
    tip_cases = json.loads(result.stdout)
    count = 0
    for case, tip_values in zip(MASTER.REFERENCE_CASES, tip_cases):
        stream = MASTER.MedianAverageAdaptiveFilter(case['threshold'])
        assert len(tip_values) == len(data) == 252
        for bar, (price, (tip_value, tip_trial)) in enumerate(zip(data, tip_values), 1):
            value = stream.update(price)
            assert (math.isnan(value) if tip_value is None else value == tip_value), (
                case['threshold'], bar, value, tip_value)
            assert stream.state.candidate_ema == tip_trial, (case['threshold'], bar, 'Value2')
            count += 1
    assert len(tip_cases) == len(MASTER.REFERENCE_CASES)
    return len(tip_cases), count


if __name__ == '__main__':
    cases, bars = verify()
    print(f'eSignal source equivalence passed: {cases} thresholds, {bars} bars; exact public and trial-EMA values.')
