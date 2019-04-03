# DESI Legacy Survey Exposure QA

The purpose of this repo is to support automated QA of [DECaLs](http://legacysurvey.org/decamls/) imaging used to select
DESI spectroscopic targets.  The three main components are described below.

## Prepare Data

Process the community pipeline output for all ~120K candidate DECaLS exposures to produce (inverse-variance weighted)
downsampled thumbnails.

More details [here](prepare/README.md).

## Visual Inspection

Allow rapid visual inspection of about 5% of the thumbnail images to collect expert labels for the main classes of bad exposures.

Try it out [here](https://dkirkby.github.io/legacyQA/).

## Machine Learning

Train various algorithms using the expert labeled data to automate the identification of bad exposures from the full dataset.

More details [here](ml/README.md).
