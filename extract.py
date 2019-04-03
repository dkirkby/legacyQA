# Setup the DESI environment first using:
# source /project/projectdirs/desi/software/desi_environment.sh master
# To test interactively, use e.g.
# python extract.py 201
# To run in batch, use:
# sbatch extract.slurm

import os
import sys
from pathlib import Path
import warnings
import imageio

import numpy as np
import numpy.lib.stride_tricks

import fitsio

import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

def extract(idx, jobspec, offsets, downsampling=128, n1=2046, n2=4094, clip_percent=2.5):
    # Parse the job spec.
    jobnum, expnum, name = jobspec.split()
    jobnum = int(jobnum)
    expnum = int(expnum)
    # Prepare the output path for this job.
    path = f'{(jobnum//10000):02d}/{(jobnum//100)%100:02d}'
    OUTDIR = Path(os.getenv('SCRATCH')) / 'LQA' / path
    os.makedirs(OUTDIR, exist_ok=True)
    assert name.endswith('.fits.fz')
    basename = Path(name).name[:-8]
    outname = str(OUTDIR / f'{jobnum:06d}-{basename}-{expnum:06d}')
    print(f'[{idx}] {outname}')
    # Process the input FITS file for this exposure.
    width, height = 7 * n2, 12 * n1
    nx, ny = int(np.ceil(width / downsampling)), int(np.ceil(height / downsampling))
    alldata = np.zeros((ny, nx), dtype=np.float32)
    allivar = np.zeros_like(alldata)
    ROOT = Path('/global/project/projectdirs/cosmo/work/legacysurvey/dr8/images/decam')
    name = str(ROOT / name)
    hdus1 = fitsio.FITS(name)
    hdr = hdus1[0].read_header()
    if hdr['EXPNUM'] != expnum:
        print('EXPNUM mismatch:'. hdr['EXPNUM'], expnum)
    hdus2 = fitsio.FITS(name.replace('ooi', 'oow'))
    for name, (x0, y0) in offsets.items():
        if name not in hdus1:
            continue
        data = hdus1[name].read()[::-1, ::-1].T
        ivar = np.clip(hdus2[name].read()[::-1, ::-1].T, a_min=0., a_max=None)
        assert data.shape == (n1, n2) and ivar.shape == (n1, n2)
        # Pad this chip so it is aligned with our downsampling grid.
        xlo, ylo = x0 // downsampling, y0 // downsampling
        xhi, yhi = (x0 + n2 - 1) // downsampling + 1, (y0 + n1 - 1) // downsampling + 1
        xdst = slice(xlo, xhi)
        ydst = slice(ylo, yhi)
        dx, dy = x0 - downsampling * xlo, y0 - downsampling * ylo
        xsrc = slice(dx, dx + n2)
        ysrc = slice(dy, dy + n1)
        padded = np.zeros((downsampling * (yhi - ylo), downsampling * (xhi - xlo)))
        blocks = block_view(padded, (downsampling, downsampling))
        padded[ysrc, xsrc] = ivar
        allivar[ydst, xdst] += blocks.sum(axis=(2, 3))
        padded[ysrc, xsrc] *= data
        alldata[ydst, xdst] += blocks.sum(axis=(2, 3))
    hdus1.close()
    hdus2.close()
    nonzero = allivar > 0
    alldata[nonzero] /= allivar[nonzero]
    # Save the downsampled image and its ivar to a numpy binary file.
    np.save(outname + '.npy', np.vstack((alldata.reshape(-1), allivar.reshape(-1))))
    # Also save a JPG image using histogram equalization.
    zero = (alldata == 0)
    eq = np.zeros_like(alldata)
    eq[~zero] = equalize(alldata[~zero], clip_percent=clip_percent)
    # Convert to RGB using viridis_r, which mostly uses the GB channels.
    cmap = plt.get_cmap('viridis_r')
    rgb = cmap(eq)[:,:,:3]
    # Use the red channel to display equalized SNR.
    # This sqrt triggers spurious RuntimeWarnings.
    rgb[:,:,0] = 0.25 * equalize(alldata * np.sqrt(allivar), clip_percent=clip_percent)
    # Force the outside region to white.
    rgb[zero] = 1.
    # Save as a jpg image.
    plt.imsave(outname + '.jpg', rgb, origin='lower')
    ##plt.imshow(rgb, interpolation='none', origin='lower')

def block_view(A, block_shape):
    """Provide a 2D block view of a 2D array.
    Returns a view with shape (n, m, a, b) for an input 2D array with
    shape (n*a, m*b) and block_shape of (a, b).
    """
    assert len(A.shape) == 2, '2D input array is required.'
    assert A.shape[0] % block_shape[0] == 0, \
        'Block shape[0] does not evenly divide array shape[0].'
    assert A.shape[1] % block_shape[1] == 0, \
        'Block shape[1] does not evenly divide array shape[1].'
    shape = (A.shape[0] // block_shape[0], A.shape[1] // block_shape[1]) + block_shape
    strides = (block_shape[0] * A.strides[0], block_shape[1] * A.strides[1]) + A.strides
    return numpy.lib.stride_tricks.as_strided(A, shape=shape, strides=strides)

def equalize(A, clip_percent=5):
    """Equalize the values of an array.
    The returned array has values between 0-1 such that clip_percent
    of the values are clipped symmetrically at 0 and 1, and the
    histogram of values between 0 and 1 is flat. This is a non-linear
    transformation and primarily useful for showing small variations
    over a large dynamic range.
    """
    A_flat = A.reshape(-1)
    n = len(A_flat)
    num_clip = round(n * clip_percent / 100.)
    num_clip_lo = num_clip // 2
    num_clip_hi = num_clip - num_clip_lo
    equalized = np.empty_like(A_flat, dtype=float)
    order = np.argsort(A_flat)
    equalized[order] = np.clip(
        (np.arange(n) - num_clip_lo) / float(n - num_clip), 0., 1.)
    return equalized.reshape(A.shape)

def get_offsets(n1=2046, n2=4094):
    offsets = {}
    width, height = 7 * n2, 12 * n1
    n2by2 = n2 // 2
    for i in range(1, 8):
        x = width - i * n2
        offsets[f'S{i}'] = x, 6 * n1
        offsets[f'N{i}'] = x, 5 * n1
    for i in range(8, 14):
        x = width - (i - 7) * n2 - n2by2
        offsets[f'S{i}'] = x, 7 * n1
        offsets[f'S{i+6}'] = x, 8 * n1
        offsets[f'N{i}'] = x, 4 * n1
        offsets[f'N{i+6}'] = x, 3 * n1
    for i in range(20, 25):
        x = width - (i - 18) * n2
        offsets[f'S{i}'] = x, 9 * n1
        offsets[f'N{i}'] = x, 2 * n1
    for i in range(25, 29):
        x = width - (i - 23) * n2 - n2by2
        offsets[f'S{i}'] = x, 10 * n1
        offsets[f'N{i}'] = x, 1 * n1
    for i in range(29, 32):
        x = width - (i - 26) * n2
        offsets[f'S{i}'] = x, 11 * n1
        offsets[f'N{i}'] = x, 0 * n1
    return offsets

def main(myid, stride=10):
    # Open the list of remaining jobs to run.
    with open('todo.txt') as f:
        todo = [line.strip() for line in f.readlines()]
    print(f'Starting job {myid} with stride {stride}.')
    offsets = get_offsets()
    # Extract this job's exposures.
    for i, jobspec in enumerate(todo[stride * myid : stride * (myid + 1)]):
        extract(stride * myid + i, jobspec, offsets)

if __name__ == '__main__':
    # Silence RuntimeWarning from np.sqrt bug.
    warnings.simplefilter('ignore')
    if len(sys.argv) > 1:
        myid = int(sys.argv[1])
    else:
        from mpi4py import MPI
        # Add an offset here to skip a completed block of jobs.
        myid = MPI.COMM_WORLD.rank
    main(myid)
