/*$(document).ready(function() {
    $('body').fadeIn(1000);
});*/

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
            //for (var i=0; i < imageList.length; ++i) {
            for (var i in imageList) {
                /*img = new Image();
                img.onLoad = (function() {
                    ++nLoaded;
                    settings.loaded($(this), nLoaded, nTotal);
                    if (nLoaded == nTotal)
                        settings.finished(_imageList);
                })();
                img.src = imageList[i];*/
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
            }
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
        init: function(nTotal) { console.log('starting to preload ' + nTotal + ' images'); },
        ready: function(index, image, url, nLoaded, nTotal) {
            console.log('loaded ' + nLoaded + '/' + nTotal + ' images: ' + url);
            $(".image-box").get(index).css(
                'background-image',
                'url(' + url + ')'
            );
        },
        success: function(list) {
            console.log('loaded ' + list.length + ' images');
        },
        error: function(url, event) {
            console.log('error when loading image: ' + url);
        },
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

// Galleria
/*$(document).ready(function() {
    $(".picture-link").galleria({
        width: 800,
        height: 600
    });
});*/

// fancybox
/*$(document).ready(function() {
    $(".picture-link").fancybox(
        {
            type : 'image',
            openEffect	: 'fade',
            closeEffect	: 'fade',
            nextEffect : 'fade',
            prevEffect : 'fade',
            openSpeed : 'fast',
            closeSpeed : 'fast',
            nextSpeed : 'fast',
            prevSpeed : 'fast',
            helpers: {
                title : {
                    type : 'float'
                },
            },
        }
    );
});*/

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
    console.log(click_index);
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
                    image_url = new_pictures[0].fullsize_url;
                else
                    image_url = new_pictures[0].display_url;*/
                image_url = new_pictures[0].fullsize_url;
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
            image_url = pictures[index].fullsize_url;
        else
            image_url = pictures[index].display_url;
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
    control_div.append($('<div/>'));
    control_div.append(control_bar);
    control_div.append($('<div/>'));
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

// picture-list dialog
function open_picture_list_dialog(json_url, pg_id, pg_context,
                                  modalOpenedCallback,
                                  updateCallback, cancelCallback)
{
    var errorHandler = function() {
        alert('Unable to retrieve thumbnails');
    };
    // get thumbnail data
    $.ajax({
        url: json_url,
        dataType: 'json',
        type: 'GET',
        data: {
            'pg-type': 'thumbnails',
            'pg-context': pg_context,
        },
    })
    .success(function(json_data) {
        if (json_data['pg-status'] == 'success') {
            var thumbnails = $.parseJSON(json_data['pg-thumbnails']);
            var container = $('<div/>').attr('id', pg_id);
            var list = $('<ul/>');
            thumbnails.forEach(function(t) {
                var picture_name = $('<p/>').html(
                    (t['index']+1) + ': ' + t['name']
                );
                var picture_url = t['url'];
                var picture = $('<img/>').attr('src', picture_url)
                    .attr('width', '150px');
                var list_element = $('<li/>').html(picture_name.after(picture));
                list_element
                    .data('pg-context', t['name'])
                    .data('pg-id', t['index']);
                list.append(list_element);
            });
            var control_div = $('<div/>').addClass('control-bar');
            var update_btn = $('<a/>').html('Update');
            var cancel_btn = $('<a/>').html('Cancel');
            update_btn.click(function() {
                updateCallback(container);
            });
            cancel_btn.click(function() {
                cancelCallback(container);
            });
            control_div.append(update_btn);
            control_div.append('&nbsp;&nbsp;|&nbsp;&nbsp;');
            control_div.append(cancel_btn);
            container.append(control_div);
            container.append(list);
            //container.hide();
            //$('body').append(container);
            container.modal({
                closeHTML: "",
                escClose: true,
                position: ["5%",],
                opacity: 80,
                overlayCss: {backgroundColor:"#000"},
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
            modalOpenedCallback(container);
            /*container.dialog({
                autoOpen: false,
                modal: true,
                width: '90%',
                buttons: {
                    "Update": function() {
                        updateCallback(container); 
                    },
                    "Cancel": function() {
                        cancelCallback(container);
                    },
                },
            });
            container.dialog('open');*/
        } else {
            errorHandler();
        }
    })
    .error(errorHandler);
}

// ordering functionality for the picture-list dialog
function open_picture_list_order_dialog(json_url, pg_id, pg_context) {
    function pgSuccessHandler(callback) {
        $.modal.close();
        callback();
    }
    function pgErrorHandler() {
        alert("Unable to reorder list, try again!");
    }
    var inputProvider = undefined;
    var modalOpenedCallback = function(container) {
        container
            .data('pg-context', pg_context)
            .data('pg-list-selector', '#' + container.attr('id') + ' ul')
            .data('pg-item-selector', '#' + container.attr('id') + ' li')
            .data('pg-name', 'children');
        inputProvider = pg_get_input_provider(
            'order-list', container, undefined
        );
    };
    var updateCallback = function(container) {
        pg_update(container, inputProvider, pgSuccessHandler, pgErrorHandler);
    };
    var cancelCallback = function(container) {
        $.modal.close();
    };
    open_picture_list_dialog(
        json_url, pg_id, pg_context,
        modalOpenedCallback,
        updateCallback, cancelCallback
    )
}
// selecting functionality for the picture-list dialog
function open_picture_list_select_dialog(json_url, pg_id, pg_context) {
    function pgSuccessHandler(callback) {
        $.modal.close();
        callback();
    }
    function pgErrorHandler() {
        alert("Unable to select picture, try again!");
    }
    var inputProvider = undefined;
    var modalOpenedCallback = function(container) {
        container
            .data('pg-context', pg_context)
            .data('pg-list-selector', '#' + container.attr('id') + ' ul')
            .data('pg-item-selector', '#' + container.attr('id') + ' li')
            .data('pg-name', 'children');
        inputProvider = pg_get_input_provider(
            'select-picture', container, undefined
        );
    };
    var updateCallback = function(container) {
        pg_update(container, inputProvider, pgSuccessHandler, pgErrorHandler);
    };
    var cancelCallback = function(container) {
        $.modal.close();
    };
    open_picture_list_dialog(
        json_url, pg_id, pg_context,
        modalOpenedCallback,
        updateCallback, cancelCallback
    )
}

// editing functionality
var pg_update_json_url = undefined;
var pg_input_providers = {};
function pg_register_input_provider(pg_type, input_provider)
{
    pg_input_providers[pg_type] = input_provider;
}
pg_register_input_provider('attribute-text', function (source, parent) {
    var input = $('<input/>').attr('type', 'text').addClass('pg-edit-text')
        .val(source.html().trim());
    if (source.data('pg-size') != undefined) {
        input.attr('size', source.data('pg-size'));
    }
    parent.html(input);
    return {
        method:
            'GET',
        type:
            'attribute-text',
        data:
            function() {
                return input.val();
            },
        update:
            function() {
                if (input.val() != source.html().trim()) {
                    source.html(input.val());
                }
            }
    };
});
pg_register_input_provider('attribute-multiline-text', function (source, parent) {
    var input = $('<textarea/>').attr('type', 'text').attr('cols', '100')
        .attr('rows', '8').addClass('pg-edit-multiline-text')
        .html(source.html().trim());
    if (source.data('pg-cols') != undefined) {
        input.attr('cols', source.data('pg-cols'));
    }
    if (source.data('pg-rows') != undefined) {
        input.attr('rows', source.data('pg-rows'));
    }
    parent.html(input);
    return {
        method:
            'POST',
        type:
            'attribute-multiline-text',
        data:
            function() {
                return input.val();
            },
        update:
            function(json_data) {
                if (input.val() != source.html().trim()) {
                    source.html(input.val());
                }
            }
    };
});
pg_register_input_provider('attribute-date', function (source, parent) {
    var input = $('<input/>').attr('type', 'text').addClass('pg-edit-date');
    parent.html(input);
    input.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-value'));
    return {
        method:
            'GET',
        type:
            'attribute-date',
        data:
            function() {
                return input.val();
            },
        update:
            function(json_data) {
                source.html(json_data['pg-date']);
            }
    };
});
pg_register_input_provider('attribute-date-from-to', function (source, parent) {
    var input_from = $('<input/>').attr('type', 'text').addClass('pg-edit-date');
    var input_to= $('<input/>').attr('type', 'text').addClass('pg-edit-date');
    parent.html(input_from.after('&nbsp;-&nbsp;').after(input_to));
    input_from.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-date-from'));
    input_to.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-date-to'));
    return {
        method:
            'GET',
        type:
            'attribute-date-from-to',
        data:
            function() {
                return {from: input_from.val(), to: input_to.val()};
            },
        update:
            function(json_data) {
                source.html(json_data['pg-date-from-to']);
            }
    };
});
pg_register_input_provider('order-list', function (source, parent) {
    var list = $(source.data('pg-list-selector')).first();
    list.sortable();
    return {
        method:
            'POST',
        type:
            'order-list',
        data:
            function() {
                var items = list.find($(source.data('pg-item-selector')));
                var ids = [];
                items.each(function (i) {
                    ids.push($(this).data('pg-id'));
                });
                return ids;
            },
        update:
            function(json_data) {
            }
    };
});
pg_register_input_provider('select-picture', function (source, parent) {
    var list = $(source.data('pg-list-selector')).first();
    // make only one item selectable
    list.selectable({
        stop: function(event, ui) {
            $(event.target).children('.ui-selected').not(':first').removeClass('ui-selected');
        },
    });
    return {
        method:
            'GET',
        type:
            'select-picture',
        data:
            function() {
                return list.children('.ui-selected').first().data('pg-context')
            },
        update:
            function(json_data) {
            }
    };
});

function pg_get_input_provider(pg_type, source, parent)
{
    return pg_input_providers[pg_type](source, parent);
}
function pg_update(source, inputProvider, successHandler, errorHandler)
{
    $.ajax({
        url: pg_update_json_url,
        dataType: 'json',
        type: inputProvider.method,
        data: {
            'pg-type': inputProvider.type,
            'pg-context': source.data('pg-context'),
            'pg-name': source.data('pg-name'),
            'pg-value': JSON.stringify(inputProvider.data()),
        },
    })
    .success(function(json_data) {
        if (json_data['pg-status'] == 'success') {
            inputProvider.update(json_data);
            successHandler(function() {
                // redirect to new page if necessary
                //if ('pg-replace-url' in json_data) {
                if (json_data.hasOwnProperty('pg-replace-url')) {
                    window.location.replace(json_data['pg-replace-url']);
                }
                //if ('pg-redirect-url' in json_data) {
                if (json_data.hasOwnProperty('pg-redirect-url')) {
                    window.location = json_data['pg-redirect-url'];
                }
            });
        } else {
            errorHandler();
        }
    })
    .error(errorHandler);
}

function pg_init_editing(json_url)
{
    pg_update_json_url = json_url;

    $(document).ready(function() {
        $(document).on("click", ".pg-editable", function() {
            var elem = $(this);
            // check if object is already being edited
            if (elem.data('pg-editing') == undefined) {
                // mark element as being edited
                elem.data('pg-editing', true);
            } else {
                // object is already being edited
                return false;
            }
            // retrieve pg-type attributes
            var pg_type = elem.data('pg-type');
            if (pg_type in pg_input_providers) {
                // if not already set, set the pg-value attribute
                //if (elem.data('pg-value') == undefined) {
                //    elem.data('pg-value', elem.html().trim());
                //}
                // add some elements to the DOM
                var container = $('<p/>').addClass('pg-edit-container');
                var input_div = $('<div/>').addClass('pg-edit-input');
                var action_div = $('<div/>').addClass('pg-edit-action');
                var update = $('<a/>').html('Update')
                    .addClass('pg-edit-update-button');
                var cancel = $('<a/>').html('Cancel')
                    .addClass('pg-edit-cancel-button');
                var status = $('<a/>').hide().html(
                    '&nbsp;|&nbsp;Failed'
                )
                .addClass('pg-edit-status-field');
                container.hide().html(
                    input_div.after('&nbsp;').after(
                        action_div.html(
                            update.after('&nbsp;|&nbsp;')
                            .after(cancel).after(status)
                        )
                    )
                )
                container.insertAfter(elem);
                // retrieve input provider
                var inputProvider = pg_get_input_provider(pg_type, elem, input_div);
                // slide in new DOM elements
                container.slideDown('fast');
                /*// extract the current click handler of the element
                var previousHandler = elem.data('events')['click'][0].handler;
                // remove click handler from object
                elem.off('click');*/
                // handler when editing is cancelled
                var cancelHandler = function() {
                    // slide out new DOM elements
                    container.slideUp('fast', function() {
                        container.remove();
                        // remove editing mark
                        elem.removeData('pg-editing');
                        /*// remove all click handler from the element
                        elem.off('click');
                        // and add the previous handler
                        elem.on('click', previousHandler);*/
                    });
                };
                elem.one('click', cancelHandler);
                cancel.one('click', cancelHandler);
                update.click(function() {
                    function successHandler(callback) {
                        status.css('color', '#00FF00')
                        .html('&nbsp;|&nbsp;Succeeded')
                        .fadeIn(100).delay(500).queue(function() {
                            container.slideUp('fast', function() {
                                // slide out new DOM elements
                                container.remove();
                                // remove editing mark
                                elem.removeData('pg-editing');
                                /*// remove all click handler from the element
                                elem.off('click');
                                // and add the previous handler
                                elem.on('click', previousHandler);*/
                            });
                        });
                        callback();
                    }
                    function errorHandler() {
                        status.css('color', '#FF0000')
                        status.fadeIn(200).fadeOut(200).fadeIn(200).fadeOut(200)
                            .fadeIn(200).delay(1000).fadeOut(200);
                    }
                    pg_update(elem, inputProvider, successHandler, errorHandler);
                });
            } else {
                // TODO: show some useful error message
                alert('Unknown input type: ' + pg_type);
            }
            // prevent default click action
            return false;
        });
    });
}

