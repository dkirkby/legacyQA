## Script to build the list of extraction jobs to run.
## Run as "python init.py" at NERSC from a python 3 environment.
## After running this script, copy all.txt to todo.txt to initialize
## job control with extract.py and sync.py.

import sys
import os.path

import numpy as np

import requests

import astropy.table


# From https://github.com/legacysurvey/legacypipe/blob/master/py/legacyzpts/psfzpt_cuts.py#L274-L293
def read_bad_expid(fn='bad_expid.txt'):
    bad_expid = {}
    f = open(fn)
    for line in f.readlines():
        #print(line)
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        words = line.split()
        if len(words) < 2:
            continue
        try:
            expnum = int(words[0], 10)
        except:
            print('Skipping line', line)
            continue
        reason = ' '.join(words[1:])
        bad_expid[expnum] = reason
    return bad_expid


def build_all(bad_expid):
    # Read the list of candidate DR8 decam exposures.
    dr8ondisk = astropy.table.Table.read('/global/project/projectdirs/cosmo/work/legacysurvey/dr8/image-lists/dr8-ondisk-decam-v4.fits')
    # Select exposures to keep (and filter out duplicate EXPNUMs).
    keep = np.array(dr8ondisk['qkeep'])
    print(f'Selected {np.count_nonzero(keep)} / {len(dr8ondisk)} exposures with qkeep==True.')
    # Remove bad exposures.
    bad = np.array([expid in bad_expid for expid in dr8ondisk['expnum']], bool)
    keep &= ~bad
    print(f'Selected {np.count_nonzero(keep)} good exposures.')
    # Write out the list of exposures with qkeep==True that are not already marked bad.
    with open('all.txt', 'w') as f:
        for jobnum, row in enumerate(dr8ondisk[keep]):
            print(f'{jobnum:06d} {row["expnum"]:06d} {row["filename"]}', file=f)


def main():
    badname = 'decam-bad_expid.txt'
    if not os.path.exists(badname):
        print(f'Downloading {badname}...')
        URL = 'https://raw.githubusercontent.com/legacysurvey/legacypipe/master/py/legacyzpts/data/'
        try:
            response = requests.get(URL + badname)
            with open(badname, 'w') as f:
                f.write(response.text)
        except requests.exceptions.RequestException as e:
            print(f'Download failed with:\n{e}')
            sys.exit(-1)
    # Read the list of bad exposures from (a local copy of) legacyzpts/data/decam-bad_expid.txt
    bad_expid = read_bad_expid(badname)
    print(f'Read {len(bad_expid)} bad exposures from {badname}.')
    # Build the list of extraction jobs to run.
    build_all(bad_expid)
    print('Created all.txt. To initialize jobs, use "cp all.txt todo.txt"')


if __name__ == '__main__':
    main()
