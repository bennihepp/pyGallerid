/*
pyGallerid.js -- Image preloading and lightbox functionality for pyGallerid.

This software is distributed under the FreeBSD License.
See the accompanying file LICENSE for details.

Copyright 2012 Benjamin Hepp
*/

// retrieve browser viewport size
function get_viewport_size() {
    var width, height;
    if (typeof window.innerWidth != 'undefined') {
        // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight
        width = window.innerWidth,
        height = window.innerHeight
    } else if (typeof document.documentElement != 'undefined'
        // IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)
            && typeof document.documentElement.clientWidth !=
            'undefined' && document.documentElement.clientWidth != 0) {
        width = document.documentElement.clientWidth,
        height = document.documentElement.clientHeight
    } else {
        // older versions of IE
        width = document.getElementsByTagName('body')[0].clientWidth,
        height = document.getElementsByTagName('body')[0].clientHeight
    }
    return {width: width, height: height};
}

// Image preloading.
// Adapted from http://ditio.net/2010/02/14/jquery-preload-images-tutorial-and-example/
(function($) {
    $.extend({
        preloadImages: function(imageList, options) {
            var _imageList = [];
            var settings = $.extend({
                init: function(nTotal) {},
                ready: function(index, image, url, nLoaded, nTotal) {},
                success: function(imageList) {},
                error: function(url, event) {},
            }, options);
            var nTotal = imageList.length;
            var nLoaded = 0;

            settings.init(nTotal);
            $(imageList).each(function (i) {
                //img = new Image();
                //img.onLoad = (function() {
                    //++nLoaded;
                    //settings.loaded($(this), nLoaded, nTotal);
                    //if (nLoaded == nTotal)
                        //settings.finished(_imageList);
                //})();
                //img.src = imageList[i];
                img = $('<img/>');
                img.load(function() {
                    ++nLoaded;
                    settings.ready(i, $(this), $(this).attr('src'),
                                   nLoaded, nTotal);
                    if (nLoaded == nTotal)
                        settings.success(_imageList);
                });
                img.error(function(event) {
                    settings.error($(this).attr('src'), event);
                });
                img.attr('src', imageList[i]);
                _imageList.push(img);
            });
        }
    });
})(jQuery);

// A simpler function for preloading a single image
(function($) {
    $.extend({
        preloadImage: function(image, callback) {
            var _imageList = [image];
            var _options = {}
            if (callback != undefined)
                _options.ready = function(index, image, url,
                                          nLoaded, nTotal) {
                    callback(image, url);
                };
            $.preloadImages(_imageList, _options);
        }
    });
})(jQuery);

// image loading helper
$(document).ready(function() {
    var imageList = [];
    $(".image-box").each(function(i, box) {
        imageList.push($(box).data('src'));
    });
    $.preloadImages(imageList, {
        //init: function(nTotal) {
            //console.log('starting to preload ' + nTotal + ' images');
        //},
        ready: function(index, image, url, nLoaded, nTotal) {
            //console.log('loaded ' + nLoaded + '/' + nTotal + ' images: ' + url);
            $($(".image-box")[index]).css(
                'background-image',
                'url("' + url + '")'
            );
        },
        //success: function(list) {
            //console.log('loaded ' + list.length + ' images');
        //},
        //error: function(url, event) {
            //console.log('error when loading image: ' + url);
        //},
    });
    /*$(".image-box")
        .load(function() { console.log("image loaded correctly"); })
        .error(function() {
            alert('error loading image: ' + $(this).data('src'));
            console.log("error loading image: " + $(this).data('src'));
            window.location = window.location;
        });
    $(".image-box").each(function(i, box) {
        $(box).css(
            'background-image',
            'url(' + $(box).data('src') + ')'
        );
    });*/
});

function retrieve_pictures(json_url, pg_context, slice, callback)
{
    var errorHandler = function() {
        alert('Unable to retrieve picture');
    };
    // get picture data
    $.ajax({
        url: json_url,
        dataType: 'json',
        type: 'GET',
        data: {
            'pg-type': 'pictures',
            'pg-context': pg_context,
            'pg-slice' : slice,
        },
    })
    .success(function(json_data) {
        if (json_data['pg-status'] == 'success') {
            var pictures = $.parseJSON(json_data['pg-pictures']);
            callback(pictures);
        } else {
            errorHandler();
        }
    })
    .error(errorHandler);
}
function retrieve_picture(json_url, pg_context, index, callback)
{
    slice = index + ":" + (index + 1);
    return retrieve_pictures(json_url, pg_context, slice, callback);
}

// lightbox functionaliy through simplemodal
function open_picture_lightbox(json_url, pg_context, pg_id, click_index, pictures)
{
    // get size of viewport
    var viewport_size = get_viewport_size();
    // create DOM elements
    var container = $('<div/>').attr('id', pg_id);
    var control_div = $('<div/>').addClass('control-box');
    var control_bar = $('<div/>').addClass('control-bar');
    var content_div = $('<div/>').addClass('content-box');
    var picture_div = $('<div/>').addClass('picture');
    var picture_img = $('<img/>');
    //var close_btn = $('<a/>').html('Close');
    var zoom100_btn = $('<a/>').html('100&#37;');
    var zoom125_btn = $('<a/>').html('125&#37;');
    var zoom150_btn = $('<a/>').html('150&#37;');
    var zoom200_btn = $('<a/>').html('200&#37;');
    var prev_btn = $('<a/>').html('Previous');
    var next_btn = $('<a/>').html('Next');
    var close_btn = $('<a/>').html('Close');
    container.data('pg-zoom', 1.0);
    container.data('pg-current-index', click_index);
    function update_picture_lightbox(index) {
        if (index == undefined || isNaN(index))
            var index = container.data('pg-current-index');
        else {
            if (index < 0)
                index = 0;
            else if (index >= pictures.length)
                index = pictures.length - 1;
            if (isNaN(index))
                index = click_index;
            container.data('pg-current-index', index);
        }
        if (pictures[index] == undefined) {
            // load a new picture before changing size etc.
            retrieve_picture(json_url, pg_context, index, function(new_pictures) {
                var image_url;
                /*if (zoom > 1.0)
                    image_url = new_pictures[0].big_url;
                else
                    image_url = new_pictures[0].regular_url;*/
                image_url = new_pictures[0].big_url;
                $.preloadImage(image_url, function(image, url) {
                    pictures[index] = new_pictures[0];
                    update_picture_lightbox();
                });
            });
            return;
        }
        var zoom = container.data('pg-zoom');
        var picture_width = pictures[index]['width'];
        var picture_height = pictures[index]['height'];
        var container_width = viewport_size['width'] - 24 - 16;
        var container_height = viewport_size['height'] - 24 - 50;
        var scale = container_width / picture_width;
        if (Math.round(scale * picture_height) > container_height)
            scale = container_height / picture_height;
        var width = Math.round(picture_width * scale * zoom);
        var height = Math.round(picture_height * scale * zoom);
        picture_img.attr('width', width).attr('height', height);
        var xoffset = (container_width - width) / 2;
        var yoffset = (container_height - height) / 2;
        var position = [0, 0];
        if (xoffset >= 0)
            xoffset += 8;
        else
            xoffset = 0;
        if (yoffset < 0)
            yoffset = 0;
        container.css('left', xoffset + 'px')
            .css('top', yoffset + 'px');
        // show or hide prev and next buttons
        if ((index - 1) < 0)
            prev_btn.addClass('pg-disabled');
        if ((index - 1) >= 0)
            prev_btn.removeClass('pg-disabled');
        if ((index + 1) >= pictures.length)
            next_btn.addClass('pg-disabled');
        if ((index + 1) < pictures.length)
            next_btn.removeClass('pg-disabled');
        // load image
        var image_url;
        //if (width > picture_width || height > picture_height)
        if (zoom > 1.0)
            image_url = pictures[index].big_url;
        else
            image_url = pictures[index].regular_url;
        picture_img.attr('src', image_url);
        //picture_img.css('background-image', 'url(' + image_url + ')');
        // open modal dialog
        container.modal({
            closeHTML: "",
            //closeHTML: "<a href='#' title='Close' class='modal-close'>x</a>",
            escClose: true,
            opacity: 80,
            minWidth: viewport_size['width'],
            maxWidth: viewport_size['width'],
            minHeight: viewport_size['height'],
            maxHeight: viewport_size['height'],
            position: position,
            overlayCss: {backgroundColor:"#000"},
            overlayClose: true,
            onOpen: function (dialog) {
                dialog.overlay.fadeIn('fast', function () {
                    dialog.data.hide();
                    dialog.container.fadeIn('fast');
                    dialog.data.fadeIn('fast');
                });
            },
            onClose: function (dialog) {
                dialog.data.fadeOut('fast');
                dialog.container.fadeOut('fast', function () {
                    dialog.overlay.fadeOut('fast', function () {
                        $.modal.close();
                    });
                });
            },
        });
    }
    // connect DOM elements
    control_bar.append(zoom100_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(zoom125_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(zoom150_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(zoom200_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(prev_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(next_btn);
    control_bar.append('&nbsp;&nbsp;|&nbsp;&nbsp;')
    control_bar.append(close_btn);
    control_div.append(control_bar);
    picture_div.append(picture_img);
    content_div.append(picture_div);
    container.append(control_div);
    container.append(content_div);
    // show dialog
    update_picture_lightbox();
    // connect event handlers
    close_btn.click(function() {
        $.modal.close();
    });
    zoom100_btn.click(function() {
        container.data('pg-zoom', 1.0);
        update_picture_lightbox();
    });
    zoom125_btn.click(function() {
        container.data('pg-zoom', 1.25);
        update_picture_lightbox();
    });
    zoom150_btn.click(function() {
        container.data('pg-zoom', 1.5);
        update_picture_lightbox();
    });
    zoom200_btn.click(function() {
        container.data('pg-zoom', 2.0);
        update_picture_lightbox();
    });
    function prev_callback() {
        var index = container.data('pg-current-index');
        if (index != undefined)
            update_picture_lightbox(index - 1);
    }
    prev_btn.on("click", prev_callback);
    function next_callback() {
        var index = container.data('pg-current-index');
        if (index != undefined)
            update_picture_lightbox(index + 1);
    }
    next_btn.on("click", next_callback);
    picture_div.on("click", next_callback);
    // attach keydown event handler
    $(document).on("keydown", function(event) {
        if (event.which == 37) {
            prev_callback();
            event.preventDefault();
        } else if (event.which == 39) {
            next_callback();
            event.preventDefault();
        }
    });
}
