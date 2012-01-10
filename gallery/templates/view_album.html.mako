## view_album.html.mako

<%inherit file="gallery_layout.html.mako"/>

<%namespace file="gallery_layout.html.mako" name="helper"/>

<%block name="navigation_options">
    ${parent.navigation_options()}
    % if show_as_grid == 'True':
        <a class="navigation"
            href="${request.resource_url(request.context, '@@'+request.view_name, query=dict(page=1, grid=False))}">
            Show as list
        </a>
    % else:
        <a class="navigation"
            href="${request.resource_url(request.context, '@@'+request.view_name, query=dict(page=1, grid=True))}">
            Show as grid
        </a>
    % endif
    &nbsp;|&nbsp;
</%block>

<%block name="body">

<div class="content-info">
    <span class="content-navigation-current pg-editable" \
        data-pg-id="Album:" \
        data-pg-type="date-from-to" \
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
        data-pg-id="Album:" \
        data-pg-type="multiline" \
        data-pg-name="long_description">
        ${album.long_description}
    </p>
</div>
<div class="content-description-bottom-line">
</div>

<div class="album-navigation-top">
<%block name="album_navigation">
    <a class="navigation-first" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=1, grid=show_as_grid))}"
        % if page <= 1:
            style="visibility: hidden"
        % endif
    >&lt;&lt;</a>
    <a class="navigation-prev" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=page-1, grid=show_as_grid))}"
        % if page <= 1:
            style="visibility: hidden"
        % endif
    >&lt; Prev</a>
    Page ${page} of ${num_of_pages}
    <a class="navigation-next" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=page+1, grid=show_as_grid))}"
        % if page >= num_of_pages:
            style="visibility: hidden">
        % endif
    >Next &gt;</a>
    <a class="navigation-last" href="${request.resource_url(album, '@@'+request.view_name, query=dict(page=num_of_pages, grid=show_as_grid))}"
        % if page >= num_of_pages:
            style="visibility: hidden">
        % endif
    >&gt;&gt;</a>
</%block>
</div>

<div class="pictures">
    <ul class="picture-list">
        % for picture in pictures:
            <li class="picture-item">
                <div class="picture-cell"
                    style="width: ${preview_width(picture)}px;
                           height: ${preview_height(picture)}px;">
                <!-- max 1024x536 -->
                    <div class="picture-container">
                        <a class="picture-link"
                            title="${picture.description}"
                            href="${display_url(picture)}"
                            rel="picture-gallery">
                        <img class="image-box"
                            alt="${picture.name}"
                            width="${preview_width(picture)}"
                            height="${preview_height(picture)}"
                            src="/static/img/spacer.gif"
                            data-src="${preview_url(picture)}"
                            style="
                                background-repeat: no-repeat;" />
                        </a>
                    </div>
                    <div class="picture-info" style="width: ${preview_width(picture)}px;">
                        <div class="picture-descr">
                            <p class="pg-editable" \
                                data-pg-id="Picture:${picture.name}" \
                                data-pg-type="text" \
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
