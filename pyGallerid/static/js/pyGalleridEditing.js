/*
pyGalleridEditing.js -- Editing functionality for pyGallerid.

This software is distributed under the FreeBSD License.
See the accompanying file LICENSE for details.

Copyright 2012 Benjamin Hepp
*/

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

function pg_init_editing(update_json_url, retrieve_json_url)
{
    pg_update_json_url = update_json_url;

    pg_init_resource_tree(retrieve_json_url);
    pg_init_dialogs(retrieve_json_url);

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
                alert('Unknown input type: ' + pg_type);
            }
            // prevent default click action
            return false;
        });
    });
}

// Resource tree view
function pg_init_resource_tree(json_url) {
    $(document).ready(function() {
        $('#tree-link').click(function(event) {
            event.preventDefault();
            var container = $('<div />').attr('id', 'resource-tree-lightbox');
            var tree_div = $('<div />').attr('class', 'tree');
            var list_div = $('<div />').attr('class', 'attributes');
            tree_div.jstree({
                core: {
                },
                json_data: {
                    ajax: {
                        url: json_url,
                        dataType: 'json',
                        type: 'GET',
                        data: function(n) {
                            if (n == -1)
                                return {'pg-type': 'resource-lineage'}
                            else
                                return {'pg-type': 'resource-children', 'pg-path': n.attr('pg-path')}
                        },
                        success: function(json_data) {
                            return $.parseJSON(json_data['pg-data']);
                        }
                    },
                    progressive_render: true,
                },
                themes: {
                    'theme': 'apple',
                    'dots': true,
                    'icons': false,
                },
                plugins: ['json_data', 'themes', 'ui'],
            })
            .bind('select_node.jstree', function(e, data) {
                var json_data = [];
                var attributes = data.rslt.obj.data();
                for (index in attributes) {
                    json_data.push({'data': index, 'state': 'open', 'children': [attributes[index]]});
                }
                list_div.jstree({
                    core: {
                    },
                    json_data: {
                        data: json_data,
                    },
                    themes: {
                        'theme': 'apple',
                        'dots': false,
                        'icons': false,
                    },
                    plugins: ['json_data', 'themes'],
                });
            });
            container.append(tree_div);
            container.append(list_div);
            var viewport_size = get_viewport_size();
            container.modal({
                escClose: true,
                opacity: 80,
                overlayCss: {backgroundColor:"#000"},
                minWidth: 0.9 * viewport_size['width'],
                maxWidth: 0.9 * viewport_size['width'],
                minHeight: 0.9 * viewport_size['height'],
                maxHeight: 0.9 * viewport_size['height'],
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
        });
    });
}

function pg_init_dialogs(json_url)
{
    $(document).ready(function() {
        $('.pg-edit-order').click(function() {
            pg_context = $(this).data('pg-context');
            pg_id = $(this).data('pg-id');
            open_picture_list_order_dialog(
                json_url,
                pg_id,
                pg_context
            );
        });
        $('.pg-edit-select-preview-picture').click(function() {
            pg_context = $(this).data('pg-context');
            pg_id = $(this).data('pg-id');
            open_picture_list_select_dialog(
                json_url,
                pg_id,
                pg_context
            );
        });
        $('.pg-edit-preview-picture').click(function() {
            pg_context = $(this).data('pg-context');
            pg_id = $(this).data('pg-id');
            alert('Not implemented yet');
            //open_picture_edit_dialog(
            //    json_url,
            //    pg_id,
            //    pg_context
            //);
        });
    });
}
