# Synchronize the job outputs with the web file system and update the todo list.
# Run this after completing a batch of new processing jobs using
# "python sync.py" from the DESI conda environment on edison.

import os
import re
import json
from pathlib import Path
from shutil import copyfile

import numpy as np


def sync(nscan=500):
    # Load the list of all files to process.
    jobnums, expnums, names = [], [], []
    with open('all.txt') as f:
        for line in f.readlines():
            jobnum, expnum, name = line.split()
            jobnums.append(int(jobnum))
            expnums.append(int(expnum))
            names.append(name)
    jobnums = np.array(jobnums)
    expnums = np.array(expnums)
    njobs = len(jobnums)
    print(f'Synching {njobs} jobs...')
    # Define source and destination paths.
    src = Path(os.getenv('SCRATCH')) / 'LQA'
    dst = Path(os.getenv('DESI_WWW')) / 'users' / 'dkirkby' / 'LQA'
    # Initialize progress lists.
    todo = np.ones(njobs, bool)
    toscan = {'g': [], 'r': [], 'z': []}
    bandpat = re.compile('_([grz])_')
    # Loop over source directories.
    for i in range(njobs // 10000 + 1):
        path0 = Path(f'{i:02d}')
        if not (src / path0).is_dir():
            continue
        if not (dst / path0).is_dir():
            (dst / path0).mkdir()
        for j in range(100):
            path1 = path0 / f'{j:02d}'
            if not (src / path1).is_dir():
                continue
            if not (dst / path1).is_dir():
                (dst / path1).mkdir()
            ncopy = 0
            missing = np.ones(1000, bool)
            for jpg in (src / path1).glob('*.jpg'):
                jobnum, name, expnum = jpg.stem.split('-')
                jobnum = int(jobnum)
                expnum = int(expnum)
                # Lookup the corresponding job in the master list.
                assert jobnums[jobnum] == jobnum
                if expnum != expnums[jobnum]:
                    raise RuntimeError(f'EXPNUM msimatch: {expnum}, {expnums[jobnum]}.')
                # Check that this is the expected filename.
                expected = Path(names[jobnum]).name
                assert expected.endswith('.fits.fz')
                if name != expected[:-8]:
                    raise RuntimeError(f'Filename mismatch: "{name}", "{expected}".')
                # Extract the band (g,r,z) from the name.
                band = bandpat.search(name)
                if band is None:
                    raise RuntimeError(f'No band specified in "{name}".')
                band = band.group(1)
                # Record that we found this file.
                missing[jobnum % 1000] = False
                todo[jobnum] = False
                # Add this to the list of jobs for visual scanning if necessary.
                if len(toscan[band]) < nscan:
                    fullname = f'{jobnum:06d}-{name}-{expnum:06d}.jpg'
                    assert fullname == jpg.name
                    toscan[band].append(str(path1 / fullname[:-4]))
                    # Copy the file if necessary.
                    if not (dst / path1 / fullname).exists():
                        name += '.jpg'
                        copyfile(src / path1 / fullname, dst / path1 / fullname)
                        ncopy += 1
            missing = np.where(missing)[0]
            print(f'{path1}: copied {ncopy} / {1000 - len(missing)}, missing {len(missing)}.')
    # Write out toscan list.
    for band in 'grz':
        print(f'Found {len(toscan[band])} {band}-band images to scan.')
    with open(f'toscan.js', 'w') as f:
        f.write('initscan(')
        json.dump(toscan, f, separators=(',\n', ':'))
        f.write(');\n')
    print('Wrote "toscan.js". Move this to ../docs/js/ and push to master to update the web client.')
    # Write out todo list.
    todo = np.where(todo)[0]
    print(f'Still have {len(todo)} / {njobs} to process.')
    with open('todo.txt', 'w') as f:
        for k in todo:
            print(f'{jobnums[k]:06d} {expnums[k]:06d} {names[k]}', file=f)
    print('Updated "todo.txt" for future job submission.')


if __name__ == '__main__':
    sync()
