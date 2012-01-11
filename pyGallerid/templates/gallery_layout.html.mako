## gallery_layout.html.mako

<%inherit file="layout.html.mako"/>

<%block name="header">
    % if len(lineage_list) > 1:
    <p class="hidden">
    % else:
    <p>
    % endif
        ${request.context.description}
    </p>
</%block>

## <%block name="html_body_tags">
##     data-json-update-url="${request.resource_url(request.context, '@@update')}"
## </%block>

<%block name="body">

    % if editing:
        <script type="text/javascript">
            pg_init_editing('${request.resource_url(request.context, '@@update')}');
        </script>
    % endif

    <div class="content-navigation">
        &gt;&nbsp;
        % for elem in lineage_list[1:][::-1]:
            <a class="navigation"
                href="${request.resource_url(elem, '@@'+request.view_name)}">
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
                data-pg-id="GalleryContainer:" \
                data-pg-type="text" \
                data-pg-name="name">
        % endif
                ${render_resource(request.context)}
            </p>
        </span>
        <div class="content-navigation-options">
            <%block name="navigation_options">
            </%block>
            % if editing:
                <a class="navigation"
                    href="${request.resource_url(request.context, '@@')}">
                    Stop editing
                </a>
            % else:
                <a class="navigation"
                    href="${request.resource_url(request.context, '@@edit')}">
                    Edit content
                </a>
            % endif
            &nbsp;|&nbsp;
        </div>
    </div>

    ${next.body()}
</%block>

<%def name="render_resource(resource)">
    % if resource is request.root:
        Home
    % else:
        ${resource.name}
    % endif
</%def>

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
