## gallery_layout.html.mako

<%inherit file="layout.html.mako"/>

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

<%block name="body">

    % if editing:
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
                    alert('not implemented yet');
                    //open_picture_edit_dialog(
                    //    '${request.resource_url(request.context, '@@retrieve') | n}',
                    //    pg_id,
                    //    pg_context
                    //);
                });
            });
        </script>
    % endif

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
            % if request.registry.settings.get('allow_editing', 'false') == 'true':
                % if editing:
                    <a class="navigation"
                        href="${request.resource_url(request.context, '@@') | n}">
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
        </div>
    </div>

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

## <%def name="render_resource(resource)">
##     % if resource is request.root:
##         Home
##     % else:
##         ${resource.name}
##     % endif
## </%def>

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
