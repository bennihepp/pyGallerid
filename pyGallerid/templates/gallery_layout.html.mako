## gallery_layout.html.mako

<%inherit file="layout.html.mako"/>

<%block name="html_title">
    ${lineage_list[-1].description}
</%block>

<%block name="header">
    % if len(lineage_list) > 1:
    <p class="hidden">
    % else:
    <p class="pg-editable" \
        data-pg-context="" \
        data-pg-type="attribute-text" \
        data-pg-name="description">
    % endif
        ${request.context.description}
    </p>
</%block>

## <%block name="html_body_tags">
##     data-json-update-url="${request.resource_url(request.context, '@@update') | n}"
## </%block>

<%block name="scripts">
    ${parent.scripts()}
    <script type="text/javascript">
        $(document).ready(function() {
            $('#login-link').click(function(event) {
                event.preventDefault();
                var form = $('<form method="post" action="${login_url}" />')
                var username = $('<input type="text" size="20" name="username" />');
                var password = $('<input type="password" size="20" name="password" />');
                var container = $('<div />').attr('id', 'login-lightbox');
                var usernamelabel = $('<span>Login:&nbsp;</span>');
                var passwordlabel = $('<span>Password:&nbsp;</span>');
                var usernamerow = $('<p />');
                var passwordrow = $('<p />');
                var login_button = $('<a>Login</a>');
                var cancel_button = $('<a>Cancel</a>');
                var button_row = $('<p />');
                usernamerow.append(usernamelabel);
                usernamerow.append(username);
                passwordrow.append(passwordlabel);
                passwordrow.append(password);
                button_row.append(login_button);
                button_row.append('&nbsp;&nbsp;');
                button_row.append(cancel_button);
                form.append(usernamerow);
                form.append(passwordrow);
                container.append(form);
                container.append(button_row);
                container.modal({
                    escClose: true,
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
                login_button.click(function() {
                    form.submit();
                    return false;
                });
                cancel_button.click(function() {
                    $.modal.close();
                });
            });
        });
    </script>
    % if editing:

        ## jquery-ui
        ##<script type="text/javascript" src="/static/js/jquery/jquery-ui-1.8.17.custom.min.js"></script>
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
        ## jquery-jstree
        <script type="text/javascript" src="/static/js/jquery/jquery.jstree.min.js"></script>

        <script type="text/javascript">
            pg_init_editing('${request.resource_url(request.context, '@@update') | n}');

            $(document).ready(function() {
                console.log('ready');
            });
            $(document).ready(function() {
                $('.pg-edit-order').click(function() {
                    pg_context = $(this).data('pg-context');
                    pg_id = $(this).data('pg-id');
                    open_picture_list_order_dialog(
                        '${request.resource_url(request.context, '@@retrieve') | n}',
                        pg_id,
                        pg_context
                    );
                });
                $('.pg-edit-select-preview-picture').click(function() {
                    pg_context = $(this).data('pg-context');
                    pg_id = $(this).data('pg-id');
                    open_picture_list_select_dialog(
                        '${request.resource_url(request.context, '@@retrieve') | n}',
                        pg_id,
                        pg_context
                    );
                });
                $('.pg-edit-preview-picture').click(function() {
                    pg_context = $(this).data('pg-context');
                    pg_id = $(this).data('pg-id');
                    alert('Not implemented yet');
                    //open_picture_edit_dialog(
                    //    '${request.resource_url(request.context, '@@retrieve') | n}',
                    //    pg_id,
                    //    pg_context
                    //);
                });
            });
        </script>
    % endif
</%block>

<%block name="stylesheets">
    ${parent.stylesheets()}
    % if editing:
        ## jquery-ui
        <link rel="stylesheet" href="/static/js/jquery/ui-lightness/jquery-ui-1.8.17.custom.css" type="text/css" media="screen" />
    % endif
</%block>

<%block name="body">

    <div class="content-navigation">
        &gt;&nbsp;
        % for elem in lineage_list[1:][::-1]:
            <a class="navigation"
                href="${request.resource_url(elem, '@@'+request.view_name) | n}">
                    ${render_resource(elem)}
            </a>
            &nbsp;&gt;&nbsp;
        % endfor
        <span class="content-navigation-current">
        % if request.context is request.root:
            <p style="display: inline;">
        % else:
            <p style="display: inline;" \
                class="pg-editable" \
                data-pg-context="" \
                data-pg-type="attribute-text" \
                data-pg-name="name">
        % endif
                ${render_resource(request.context)}
            </p>
        </span>
        <div class="content-navigation-options">
            <%block name="navigation_options">
            </%block>
            ## TODO
            % if allow_editing:
                % if editing:
                    <a class="navigation"
                        href="${request.resource_url(request.context) | n}">
                        Stop editing
                    </a>
                % else:
                    <a class="navigation"
                        href="${request.resource_url(request.context, '@@edit') | n}">
                        Edit content
                    </a>
                % endif
                &nbsp;|&nbsp;
            % endif
            % if user is None:
                <a id="login-link" class="navigation" \
                    href="${login_url}">
                    Login
                </a>
                &nbsp;|&nbsp;
            % else:
                <a class="navigation" \
                    href="${logout_url}">
                    Logout
                </a>
                &nbsp;|&nbsp;
            % endif
            % if about_url is not None:
                <a class="navigation" \
                    href="${about_url}">
                    About
                </a>
                &nbsp;|&nbsp;
            % endif
        </div>
    </div>

    % if len(messages) > 0:
        % for message in messages:
            <p class="content-message">
                ${message}
            </p>
        % endfor
    % endif

    % if len(lineage_list) > 1:
        <div class="content-header">
    % else:
        <div class="content-header hidden">
    % endif
            <h3 class="content-title pg-editable" \
                data-pg-context="" \
                data-pg-type="attribute-text" \
                data-pg-name="description">
                ${request.context.description}
            </h3>
        </div>

    ${next.body()}

</%block>

<%doc>
(function($) {
    var cache = [];
    // Arguments are image paths relative to the current page.
    $.preLoadImages = function() {
        var args_len = arguments.length;
        for (var i = args_len; i--;) {
            var cacheImage = document.createElement('img');
            cacheImage.src = arguments[i];
            cache.push(cacheImage);
        }
    }
})(jQuery)
</%doc>
