/*$(document).ready(function() {
    $('body').fadeIn(1000);
});*/

$(document).ready(function() {
    console.log('running');
    $(".image-box")
        .load(function() { console.log("image loaded correctly"); })
        .error(function() { console.log("error loading image"); });
});
$(document).ready(function() {
    $(".image-box").each(function(i, box) {
        $(box).css(
            'background-image',
            'url(' + $(box).attr('data-src') + ')'
        );
    });
});

$(document).ready(function() {
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
});

var pg_input_providers = {};
function pg_register_input_provider(pg_type, input_provider)
{
    pg_input_providers[pg_type] = input_provider;
}
pg_register_input_provider('text', function (source, parent) {
    var input = $('<input/>').attr('type', 'text').addClass(source.attr('class'))
                .val(source.html().trim());
    if (source.data('pg-size') != undefined) {
        input.attr('size', source.data('pg-size'));
    }
    parent.html(input);
    return {
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
pg_register_input_provider('multiline', function (source, parent) {
    var input = $('<textarea/>').attr('type', 'text').attr('cols', '100')
                .attr('rows', '8').addClass(source.attr('class'))
                .html(source.html().trim());
    if (source.data('pg-cols') != undefined) {
        input.attr('cols', source.data('pg-cols'));
    }
    if (source.data('pg-rows') != undefined) {
        input.attr('rows', source.data('pg-rows'));
    }
    parent.html(input);
    return {
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
pg_register_input_provider('date', function (source, parent) {
    var input = $('<input/>').attr('type', 'text').addClass(source.attr('class'));
    //var input = $('<div/>').addClass(source.attr('class'));
    parent.html(input);
    input.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-value'));
    return {
        data:
        function() {
            return input.val();
        },
        update:
        function(json_data) {
            console.log(json_data);
            source.html(json_data['pg-date']);
        }
    };
});
pg_register_input_provider('date-from-to', function (source, parent) {
    var input_from = $('<input/>').attr('type', 'text').addClass(source.attr('class'));
    var input_to= $('<input/>').attr('type', 'text').addClass(source.attr('class'));
    parent.html(input_from.after('&nbsp;-&nbsp;').after(input_to));
    input_from.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-date-from'));
    input_to.datepicker({dateFormat: "yy-mm-dd"})
        .datepicker("setDate", source.data('pg-date-to'));
    return {
        data:
        function() {
            console.log({from: input_from.val(), to: input_to.val()});
            return {from: input_from.val(), to: input_to.val()};
        },
        update:
        function(json_data) {
            console.log(json_data);
            source.html(json_data['pg-date-from-to']);
        }
    };
});

function pg_init_editing(json_url)
{
    // TODO: Only allow one item to be edited???
    $(document).ready(function() {
        $(".pg-editable").click(function () {
            var elem = $(this);
            // check if object is already being edited
            //if (elem.data('pg-editing') == undefined) {
                // mark element as being edited
                //elem.data('pg-editing', true);
            // retrieve pg-type attributes
            var pg_type = elem.data('pg-type');
            // if not already set, set the pg-value attribute
            //if (elem.data('pg-value') == undefined) {
            //    elem.data('pg-value', elem.html().trim());
            //}
            // check if we can handle this type
            if (pg_type in pg_input_providers) {
                /*if (elem.is('.pg-editable-multiline')) {
                    input_factory = function(cls, value) {
                        return '<textarea class="' + cls +
                                '" type="text" cols="100" rows="8">' +
                                value + '</textarea>';
                    }
                } else if (elem.is('.pg-editable-date-from-to')) {
                    input_factory = function(cls, value) {
                        return '<input class="' + cls +
                                '" type="text" value="' +
                                elem.attr('data-value').split(' - ')[0] + '" />';
                    }
                } else {
                    input_factory = function(cls, value) {
                        return '<input class="' + cls +
                                '" type="text" value="' +
                                value + '"  />';
                    }
                }
                if (elem.is('.pg-editable-date-from-to')) {
                    input.datepicker("setDate", input.val());
                }*/
                // add some elements to the DOM
                var container = $('<p/>');
                var input_div = $('<div/>');
                var update = $('<a/>').html('Update');
                var cancel = $('<a/>').html('Cancel');
                var status = $('<span/>')
                    .css('font-weight', 'bold').hide().html(
                        '&nbsp;|&nbsp;Failed'
                    );
                container.hide().html(
                    input_div.after('&nbsp;').after(update)
                    .after('&nbsp;|&nbsp;').after(cancel)
                    .after(status)
                ).insertAfter(elem);
                // call the input provider
                var inputCallbacks = pg_input_providers[pg_type](elem, input_div);
                // slide in new DOM elements
                container.slideDown('fast');
                // extract the current click handler of the element
                previousHandler = elem.data('events')['click'][0].handler;
                // remove click handler from object
                elem.off('click');
                // handler when editing is cancelled
                cancelHandler = function () {
                    // slide out new DOM elements
                    container.slideUp('fast', function() {
                        container.remove();
                        // remove editing mark
                        //elem.removeData('pg-editing');
                        // remove all click handler from the element
                        elem.off('click');
                        // and add the previous handler
                        elem.on('click', previousHandler);
                    });
                };
                cancel.add(elem).one('click', cancelHandler);
                update.click(function () {
                    function errorHandler() {
                        status.css('color', '#FF0000')
                        status.fadeIn(200).fadeOut(200).fadeIn(200).fadeOut(200)
                            .fadeIn(200).delay(1000).fadeOut(200);
                    }
                    $.getJSON(
                        json_url,
                        {
                            'pg-id': elem.data('pg-id'),
                            'pg-name': elem.data('pg-name'),
                            'pg-value': inputCallbacks.data()
                        },
                        function(json_data) {
                            if (json_data['pg-status'] == 'success') {
                                inputCallbacks.update(json_data);
                                status.css('color', '#00FF00')
                                .html('&nbsp;|&nbsp;Succeeded')
                                .fadeIn(100).delay(500).queue(function() {
                                    container.slideUp('fast', function() {
                                        // slide out new DOM elements
                                        container.remove();
                                        // remove editing mark
                                        //elem.removeData('pg-editing');
                                        // remove all click handler from the element
                                        elem.off('click');
                                        // and add the previous handler
                                        elem.on('click', previousHandler);
                                    });
                                });
                            } else {
                                errorHandler();
                            }
                        }
                    )
                    .error(errorHandler);
                });
            } else {
                // TODO: show some useful error message
                alert('unknown input type: ' + pg_type);
            }
        });
    });
}
