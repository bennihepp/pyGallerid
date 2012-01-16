## view_gallery.html.mako

<%inherit file="gallery_layout.html.mako"/>

<%namespace file="gallery_layout.html.mako" name="helper"/>

<%block name="body">

% if len(lineage_list) > 1:
<div class="content-header">
% else:
<div class="content-header hidden">
% endif
    <h3 class="content-title">${gallery_container.description}</h3>
</div>

<div class="albums">
    <ul class="album-list">

        % if editing:
            <div class="children-order-edit">
                <p class="pg-editable" \
                    data-pg-context="" \
                    data-pg-type="list-order" \
                    data-pg-list-selector="ul.album-list" \
                    data-pg-item-selector="li.album-item[data-pg-context]" \
                    data-pg-name="children">
                    Edit order
                </p>
            </div>
        % endif

        % for item_id, item in items:
            <li class="album-item" \
                data-pg-id="${item_id}" \
                data-pg-context="${item.name}">
                <div class="album-cell"
                    style="width: ${preview_width(item)}px;
                           height: ${preview_height(item)}px;">
                <!-- max 1024x536 -->
                    <div class="album-container">
                        <a class="album-link"
                            title="${item.description}"
                            href="${request.resource_url(item, '@@'+request.view_name) | n}">
                        <img class="image-box"
                            alt="${item.name}"
                            width="${preview_width(item)}"
                            height="${preview_height(item)}"
                            src="/static/img/spacer.gif"
                            data-src="${preview_url(item) | n}"
                            style="
                                background-repeat: no-repeat;" />
                        </a>
                    </div>
                    % if editing:
                        <div class="preview-picture-edit" style="width: ${preview_width(item)}px;">
                            <p class="pg-editable" \
                                data-pg-context="" \
                                data-pg-type="preview-picture" \
                                data-pg-name="preview_picture">
                                Edit preview picture
                            </p>
                        </div>
                    % endif
                    <div class="album-info" style="width: ${preview_width(item)}px;">
                        <div class="album-descr">
                            <p class="pg-editable" \
                                data-pg-context="${item.name}" \
                                data-pg-type="attribute-text" \
                                data-pg-size="33" \
                                data-pg-name="description">
                                ${item.description}
                            </p>
                        </div>
                    </div>
                </div>
            </li>
        % endfor
    </ul>
</div>

</%block>
