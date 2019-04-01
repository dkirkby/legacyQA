$(document).ready(function() {
    initialize();
});

var sessionData = null;

function initialize() {
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
            div.append($('<img>', {src: IMGSRC + list[i] + '.jpg'}));
            var tag = list[i].slice(6);
            div.append($('<span>').addClass('qa-button topleft').attr('id', 'Q_' + tag).html('?'));
            div.append($('<span>').addClass('qa-button btmleft').attr('id', 'X_' + tag).html('&cross;'));
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
        var selected = $(this).hasClass('selected');
        if(selected) {
            $(this).removeClass('selected');
            tag = 'O' + tag.slice(1);
        }
        else {
            $(this).addClass('selected');
            // Deselect the other button.
            other = (tag[0] == 'Q') ? 'X' : 'Q';
            console.log('other: #' + other + tag.slice(1));
            $('#' + other + tag.slice(1)).removeClass('selected');
        }
        console.log('click', $(this).text(), tag, selected);
    });
}
