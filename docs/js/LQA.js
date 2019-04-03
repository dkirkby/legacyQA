$(document).ready(function() {
    initialize();
});

var sessionData = null;

var bbox = {"S1": [192, 224, 96, 112], "N1": [192, 224, 80, 96], "S2": [160, 192, 96, 112], "N2": [160, 192, 80, 96], "S3": [128, 160, 96, 112], "N3": [128, 160, 80, 96], "S4": [96, 128, 96, 112], "N4": [96, 128, 80, 96], "S5": [64, 96, 96, 112], "N5": [64, 96, 80, 96], "S6": [32, 64, 96, 112], "N6": [32, 64, 80, 96], "S7": [0, 32, 96, 112], "N7": [0, 32, 80, 96], "S8": [176, 208, 112, 128], "S14": [176, 208, 128, 144], "N8": [176, 208, 64, 80], "N14": [176, 208, 48, 64], "S9": [144, 176, 112, 128], "S15": [144, 176, 128, 144], "N9": [144, 176, 64, 80], "N15": [144, 176, 48, 64], "S10": [112, 144, 112, 128], "S16": [112, 144, 128, 144], "N10": [112, 144, 64, 80], "N16": [112, 144, 48, 64], "S11": [80, 112, 112, 128], "S17": [80, 112, 128, 144], "N11": [80, 112, 64, 80], "N17": [80, 112, 48, 64], "S12": [48, 80, 112, 128], "S18": [48, 80, 128, 144], "N12": [48, 80, 64, 80], "N18": [48, 80, 48, 64], "S13": [16, 48, 112, 128], "S19": [16, 48, 128, 144], "N13": [16, 48, 64, 80], "N19": [16, 48, 48, 64], "S20": [160, 192, 144, 160], "N20": [160, 192, 32, 48], "S21": [128, 160, 144, 160], "N21": [128, 160, 32, 48], "S22": [96, 128, 144, 160], "N22": [96, 128, 32, 48], "S23": [64, 96, 144, 160], "N23": [64, 96, 32, 48], "S24": [32, 64, 144, 160], "N24": [32, 64, 32, 48], "S25": [144, 176, 160, 176], "N25": [144, 176, 16, 32], "S26": [112, 144, 160, 176], "N26": [112, 144, 16, 32], "S27": [80, 112, 160, 176], "N27": [80, 112, 16, 32], "S28": [48, 80, 160, 176], "N28": [48, 80, 16, 32], "S29": [128, 160, 176, 192], "N29": [128, 160, 0, 16], "S30": [96, 128, 176, 192], "N30": [96, 128, 0, 16], "S31": [64, 96, 176, 192], "N31": [64, 96, 0, 16]};

function initialize() {
    // Load the help tab content.
    $('#help').load('README.md');
    // Get the user name.
    console.log('initialize');
    sessionData = localStorage.getItem('LegacyQA.session');
    if(!sessionData) {
        console.log('No saved session data');
        sessionData = {
            'user': 'unknown'
        };
    }
    else {
        sessionData = JSON.parse(sessionData);
    }
    console.log('session:', sessionData);
}

function initscan(toscan) {
    console.log('Loaded', toscan.g.length, 'g-band images to scan.');
    console.log('Loaded', toscan.r.length, 'r-band images to scan.');
    console.log('Loaded', toscan.z.length, 'z-band images to scan.');
    var IMGSRC = 'https://portal.nersc.gov/project/desi/users/dkirkby/LQA/';
    var bands = ['g', 'r', 'z'];
    bands.forEach(function(band) {
        // Add each image to its tab.
        var parent = $('div#' + band + 'band');
        var list = toscan[band];
        for(var i = 0; i < list.length; i++) {
            var div = $('<div>').addClass('thumb');
            div.append($('<img>', {'data-src': IMGSRC + list[i] + '.jpg', src: "", class: 'lazy'}));
            var tag = list[i].slice(6);
            div.append($('<span>').addClass('qa-button topleft').attr('id', 'Q_' + tag).html('?'));
            div.append($('<span>').addClass('qa-button btmleft').attr('id', 'X_' + tag).html('&cross;'));
            div.append($('<span>').addClass('details-button').attr('id', tag));
            parent.append(div);
        }
        // Images are loaded into hidden elements, so make them visible when their
        // tab is selected.
        $('a[href="#' + band + 'band-tab"]').click(function(){
            $('div#' + band + 'band .thumb').css('visibility', 'visible');
         });
    });
    // Add handler for QA buttons.
    $('.qa-button').click(function() {
        var tag = $(this).attr('id');
        // Do nothing if this image has not been loaded yet.
        var src = $(this).siblings('img').attr('src');
        if(src == '') return;
        var selected = $(this).hasClass('selected');
        if(selected) {
            $(this).removeClass('selected');
            tag = 'O' + tag.slice(1);
        }
        else {
            $(this).addClass('selected');
            // Deselect the other button.
            other = (tag[0] == 'Q') ? 'X' : 'Q';
            $('#' + other + tag.slice(1)).removeClass('selected');
        }
        console.log('click', $(this).text(), tag, selected);
    });
    // Add dialog support for old browsers.
    var dialog = document.querySelector('dialog'); //$('#details');
    if (!dialog.showModal) {
        console.log('polyfilling dialog...');
        dialogPolyfill.registerDialog(dialog);
    }
    // Add handler for details buttons.
    $('.details-button').click(function() {
        // Lookup this image's tag of the form <JOBNUM>-<NAME>-<EXPNUM>.
        var tag = $(this).attr('id');
        $('#details-title').text(tag);
        // Decode the image exposure number and band.
        var fields = tag.split('-');
        var expnum = parseInt(fields[2], 10);
        fields = fields[1].split('_');
        var band = fields[fields.length - 2];
        console.log('Opening details view for expnum', expnum, 'band', band);
        // Do nothing if this image has not been loaded yet.
        var src = $(this).siblings('img').attr('src');
        if(src == '') return;
        $('#details-content img').attr('src', src).attr('data-expnum', expnum).attr('data-band', band);
        dialog.showModal();
    });
    // Add hanlder for the "Close" button on the details page.
    $('.close').click(function() {
        dialog.close();
    });
    // Add handler for the "Link" button on the details dialog.
    $('#img-link').click(function() {
        var img = $(this).parent().siblings('.mdl-dialog__content').children('img').attr('src');
        window.open(img, '_blank');
    });
    // Add handler for mouse clicks over the details image.
    $('#details img').click(function(e) {
        var offset = $(this).offset();
        var x = e.pageX - offset.left;
        var y = 192 - (e.pageY - offset.top);
        // Locate the chip corresponding to this (x,y).
        var chip = null;
        for(var key in bbox) {
            edges = bbox[key]
            if((x >= edges[0]) && (x < edges[1]) && (y >= edges[2]) && (y < edges[3])) {
                chip = key;
                break;
            }
        }
        if(chip != null) {
            var expnum = $(this).attr('data-expnum');
            var band = $(this).attr('data-band');
            var url = 'http://legacysurvey.org/viewer/ccd/decals-dr7/decam-' +
                expnum + '-' + chip + '-' + band;
            console.log('Selected chip', chip, 'opens', url);
            window.open(url, '_blank');
        }
    });
    // Enable lazy image loading.
    $('img.lazy').Lazy({scrollDirection: 'vertical'});
}
