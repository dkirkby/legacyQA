# Prepare Thumbnail Images

The initial list of DR8 images is taken from (at nersc):
```
/global/project/projectdirs/cosmo/work/legacysurvey/dr8/image-lists/dr8-ondisk-decam-v4.fits
```
filtering on `qkeep == True`.  Known bad exposures listed [here](https://raw.githubusercontent.com/legacysurvey/legacypipe/master/py/legacyzpts/data/decam-bad_expid.txt) are filtered out, leaving 119053 exposures. Note that `v4` is not
the final list for DR8.  The script `prepare/init.py` is used to build this initial list.

Jobs are submitted on edison using slurm with:
```
sbatch extract.slurm
```
which runs the python code in `prepare/extract.py` to read the exposure FITS file and produced the downsampled thumbnail.

After a batch of jobs have completed, compile statistics and prepare to submit a new batch using:
```
python sync.py
```
