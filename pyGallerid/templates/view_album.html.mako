## view_album.html.mako

<%inherit file="gallery_layout.html.mako"/>

<%namespace file="gallery_layout.html.mako" name="helper"/>

<%block name="navigation_options">
    ${parent.navigation_options()}
    % if display_mode != 'list':
        <a class="navigation"
            href="${request.resource_url(request.context, '@@'+request.view_name, query=dict(page=1, display_mode='list')) | n}">
            Show as list
        </a>
        &nbsp;|&nbsp;
    % endif
    % if display_mode != 'grid':
        <a class="navigation"
            href="${request.resource_url(request.context, '@@'+request.view_name, query=dict(display_mode='grid')) | n}">
            Show as grid
        </a>
        &nbsp;|&nbsp;
    % endif
</%block>

<%block name="body">

<div class="content-info">
    <span class="content-navigation-current pg-editable" \
        data-pg-context="" \
        data-pg-type="attribute-date-from-to" \
        data-pg-name="__date_from_to" \
        data-pg-date-from="${album.date_from}" \
        data-pg-date-to="${album.date_to}">
        ${album.date_from.day}
        % if album.date_from.year != album.date_to.year:
            ${album.date_from.strftime('%B')} ${album.date_from.year}
        % elif album.date_from.month != album.date_to.month:
            ${album.date_from.strftime('%B')}
        % endif
        - ${album.date_to.day} ${album.date_to.strftime('%B')} ${album.date_to.year}
    </span>
</div>

<div class="content-description">
    <p class="pg-editable" \
        data-pg-context="" \
        data-pg-type="attribute-multiline-text" \
        data-pg-name="long_description">
        ${album.long_description | n}
    </p>
</div>
<div class="content-description-bottom-line">
</div>

<div class="album-navigation-top">
<%block name="album_navigation">
% if display_mode != 'gallery':
    <a class="navigation-first" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=1, display_mode=display_mode)) | n}"
        % if page <= 1:
            style="visibility: hidden"
        % endif
    >&lt;&lt;</a>
    <a class="navigation-prev" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=page-1, display_mode=display_mode)) | n}"
        % if page <= 1:
            style="visibility: hidden"
        % endif
    >&lt; Prev</a>
    Page ${page} of ${num_of_pages}
    <a class="navigation-next" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=page+1, display_mode=display_mode)) | n}"
        % if page >= num_of_pages:
            style="visibility: hidden">
        % endif
    >Next &gt;</a>
    <a class="navigation-last" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=num_of_pages, display_mode=display_mode)) | n}"
        % if page >= num_of_pages:
            style="visibility: hidden">
        % endif
    >&gt;&gt;</a>
% endif
</%block>
</div>

<%block name="scripts">
    ${parent.scripts()}
    <script type="text/javascript">
        % if display_mode in ('list', 'grid'):
            $(document).ready(function() {
                var pictures = [];
                var i;
                for (i = 0; i < ${total_num_of_pictures}; i++) {
                    pictures.push(undefined);
                }
                $(".picture-item").each(function() {
                    var index = parseInt($(this).data('pg-index'));
                    var name = $(this).data('pg-context');
                    var regular_url = $(this).data('pg-regular-url');
                    var big_url = $(this).data('pg-big-url');
                    var width = $(this).data('pg-width');
                    var height = $(this).data('pg-height');
                    var picture = {
                        index: index,
                        name: name,
                        regular_url: regular_url,
                        big_url: big_url,
                        width: width,
                        height: height,
                    };
                    pictures[index] = picture;
                });
                $(".picture-link").click(function(event) {
                    event.preventDefault();
                    var item = $(this).parentsUntil(".picture-item").parent();
                    var index = parseInt(item.data('pg-index'));
                    var json_url = '${request.resource_url(request.context, '@@retrieve') | n}';
                    open_picture_lightbox(json_url, "", 'picture-lightbox',
                                          index, pictures);
                    //return false;
                });
            });
        % elif display_mode == 'gallery':
            Galleria.loadTheme('/static/js/galleria/themes/classic/galleria.classic.min.js');
            $(document).ready(function() {
                $(".pictures").galleria({
                    width: 800,
                    height: 600
                });
            });
        % endif
    </script>
</%block>

<div class="pictures">
    <ul class="picture-list">

        % if editing:
            <div class="children-order-edit">
                <p class="pg-edit-order" \
                    data-pg-id="picture-order-list-dialog" \
                    data-pg-context="">
                    Edit order
                </p>
            </div>
        % endif

        % for index, picture in pictures:
            <li class="picture-item" \
                data-pg-context="${picture.name}" \
                data-pg-index="${index}" \
                data-pg-regular-url="${regular_url(picture) | n}" \
                data-pg-big-url="${big_url(picture) |n}" \
                data-pg-width="${regular_width(picture)}" \
                data-pg-height="${regular_height(picture)}">
                <div class="picture-cell">
                <!-- max 1024x536 -->
                    <div class="picture-container">
                        <a class="picture-link" \
                            title="${picture.description}" \
                            href="${big_url(picture) | n}" \
                            rel="picture-gallery">
                        <img class="image-box" \
                            alt="${picture.name}" \
                            src="/static/img/spacer.gif" \
                            % if display_mode == 'list':
                                width="${regular_width(picture)}" \
                                height="${regular_height(picture)}" \
                                data-src="${regular_url(picture) | n}" \
                            % else:
                                width="${small_width(picture)}" \
                                height="${small_height(picture)}" \
                                data-src="${small_url(picture) | n}" \
                            % endif
                            />
                        </a>
                    </div>
                    % if editing:
                        <div class="picture-edit" style="width: \
                                ${regular_width(picture) if display_mode == 'list' else small_width(picture)}\
                            px;">
                            <p class="pg-edit-picture" \
                                data-pg-id="picture-dialog" \
                                data-pg-context="${picture.name}">
                                Edit picture
                            </p>
                        </div>
                    % endif
                    <div class="picture-info" style="width: \
                            ${regular_width(picture) if display_mode == 'list' else small_width(picture)}\
                        px;">
                        <div class="picture-descr">
                            <p class="pg-editable" \
                                data-pg-context="${picture.name}" \
                                data-pg-type="attribute-text" \
                                data-pg-name="description">
                                ${picture.description}
                            </p>
                        </div>
                    </div>
                </div>
            </li>
        % endfor
    </ul>
</div>

<div class="album-navigation-bottom">
    ${album_navigation()}
</div>
<div class="content-footer">
</div>

</%block>
