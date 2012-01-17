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
    % if display_mode != 'gallery':
        <a class="navigation"
            href="${request.resource_url(request.context, '@@'+request.view_name, query=dict(page=1, display_mode='gallery')) | n}">
            Show as slideshow
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
        ${album.long_description}
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

<script type="text/javascript">
% if display_mode in ('list', 'grid'):
    /*Shadowbox.init({
        skipSetup: true,
    });*/
    $(document).ready(function() {
        /*Shadowbox.setup(".picture-link", {
                gallery: 'album',
                overlayOpacity: 0.9,
                viewportPadding: 0,
                width: 1024,
                height: 800,
            }
        );*/
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

<div class="pictures">
    % if display_mode in ('list', 'grid'):
        <ul class="picture-list">
    
            % if editing:
                <div class="children-order-edit">
                    <p onclick="sorting_dialog();">
                        Edit order
                    </p>
                </div>
                ##<div class="children-order-edit">
                ##    <p class="pg-editable" \
                ##        data-pg-context="" \
                ##        data-pg-type="list-order" \
                ##        data-pg-list-selector="ul.picture-list" \
                ##        data-pg-item-selector="li.picture-item[data-pg-context]" \
                ##        data-pg-name="children">
                ##        Edit order by dragging
                ##    </p>
                ##</div>
            % endif
    
            % for picture_id, picture in pictures:
                <li class="picture-item" \
                    data-pg-id="${picture_id}" \
                    data-pg-context="${picture.name}">
                    <div class="picture-cell">
                    <!-- max 1024x536 -->
                        <div class="picture-container">
                            <a class="picture-link"
                                title="${picture.description}"
                                href="${display_url(picture) | n}"
                                rel="picture-gallery">
                            <img class="image-box"
                                alt="${picture.name}"
                                width="${preview_width(picture)}"
                                height="${preview_height(picture)}"
                                src="/static/img/spacer.gif"
                                data-src="${preview_url(picture) | n}"
                                style="
                                    background-repeat: no-repeat;" />
                            </a>
                        </div>
                        % if editing:
                            <div class="preview-picture-edit" style="width: ${preview_width(picture)}px;">
                                <p class="pg-editable" \
                                    data-pg-context="${picture.name}" \
                                    data-pg-type="preview-picture" \
                                    data-pg-name="preview_picture">
                                    Edit preview picture
                                </p>
                            </div>
                        % endif
                        <div class="picture-info" style="width: ${preview_width(picture)}px;">
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
    % elif display_mode == 'gallery':
        % for picture_id, picture in pictures:
            <a href="${display_url(picture) | n}" \
                rel="${original_url(picture) | n}">
            <img class="image-box" \
                alt="${picture.name}" \
                title="${picture.description}" \
                ## width="${preview_width(picture)}" \
                ## height="${preview_height(picture)}" \
                src="${preview_url(picture) | n}" />
            </a>
        % endfor
    % endif
</div>

<div class="album-navigation-bottom">
    ${album_navigation()}
</div>
<div class="content-footer">
</div>

</%block>
