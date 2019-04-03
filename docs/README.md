<p>
    DR9 of the <a href="http://legacysurvey.org/decamls/">Legacy Surveys</a> will include about 120K
    <a href="http://legacysurvey.org/decamls/">DECaLs</a> exposures. The purpose of this page is build a
    relatively small (6K exposures) dataset labeled by experts that can be used to train a machine-learning model to automatically
    classify the whole data set.
</p>
<p>
    To get started, click on a tab above to display thumbnails of (inverse-variance weighted) downsampled DECaLs exposures (using the 
    community pipeline output) for different bands. The code used to build each thumbnail is
    <a href="https://github.com/dkirkby/legacyQA/blob/master/extract.py">here</a>.
</p>
<p>
    Click on the thumbnail corners to mark an exposure as either definitely bad ("&cross;") or else possibly bad ("?")
    and needing more investigation. Any exposures you view that are not labeled this way are assumed to be of sufficient quality for DR9.
    You can change your label as often as you like (although each labeling action is recorded).
</p>
<p>
    Click on the center of any thumbnail to
    open a dialog where the focal plane is displayed 2x larger, together with a label identifying the exposure with the format
    JOBNUM-CPNAME-EXPNUM.  Use the LINK button to open this image directly (e.g., to grab its URL for sharing).  Click within this image 
    to view the corresponding chip image with the DR7 ccd viewer. Click the CLOSE button (or hit SPACE or ESC) to close this dialog.
</p>
<p>
    To report a bug or suggest a feature, review the <a href="https://github.com/dkirkby/legacyQA/issues">existing issues</a>, and
    <a href="https://github.com/dkirkby/legacyQA/issues/new">create a new one</a> if needed.
</p>
