# Synchronize the job outputs with the web file system and update the todo list.
# Run this after completing a batch of new processing jobs.

import os
from pathlib import Path
from shutil import copyfile

import numpy as np


def sync():
    # Load the list of files to process.
    with open('image-list-decam-dr8.txt') as f:
        files = [line.strip() for line in f.readlines()]
    print(f'Synching {len(files)} files...')
    # Define source and destination paths.
    src = Path(os.getenv('SCRATCH')) / 'badexp'
    dst = Path(os.getenv('DESI_WWW')) / 'users' / 'dkirkby' / 'LQA'
    todo = np.ones(len(files), bool)
    for i in range(len(files) // 10000 + 1):
        path0 = Path(f'{i:02d}')
        if not (src / path0).is_dir():
            continue
        if not (dst / path0).is_dir():
            (dst / path).mkdir()
        for j in range(100):
            path1 = path0 / f'{j:02d}'
            if not (src / path1).is_dir():
                continue
            if not (dst / path1).is_dir():
                (dst / path1).mkdir()
            ncopy = 0
            missing = np.ones(1000, bool)
            for jpg in (src / path1).glob('*.jpg'):
                name = jpg.name
                idx = name.index('_')
                k = int(name[:idx])
                # Check that this is the expected filename.
                expected = Path(files[k]).name
                assert expected.endswith('.fits.fz')
                if name[idx+1:-4] != expected[:-8]:
                    raise RuntimeError(f'Filename mismatch: "{name}", "{expected}".')
                # Record that we found this file.
                missing[k % 1000] = False
                todo[k] = False
                # Copy the file if necessary.
                if not (dst / path1 / name).exists():
                    copyfile(src / path1 / name, dst / path1 / name)
                    ncopy += 1
            missing = np.where(missing)[0]
            print(f'{path1}: copied {ncopy} / {1000 - len(missing)}, missing {len(missing)}.')
    # Write out todo list.
    todo = np.where(todo)[0]
    print(f'Still have {len(todo)} / {len(files)} to process.')
    with open('todo.txt', 'w') as f:
        for k in todo:
            print(f'{k} {files[k]}', file=f)


if __name__ == '__main__':
    sync()
