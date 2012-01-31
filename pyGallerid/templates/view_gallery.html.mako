## view_gallery.html.mako

<%inherit file="gallery_layout.html.mako"/>

<%namespace file="gallery_layout.html.mako" name="helper"/>

<%block name="body">

<div class="albums">
    <ul class="album-list">

            % if editing:
                <div class="children-order-edit">
                    <p class="pg-edit-order" \
                        data-pg-id="picture-order-list-dialog" \
                        data-pg-context="">
                        Edit order
                    </p>
                </div>
                ##<div class="children-order-edit">
                ##    <p class="pg-editable" \
                ##        data-pg-context="" \
                ##        data-pg-type="order-list" \
                ##        data-pg-list-selector="ul.album-list" \
                ##        data-pg-item-selector="li.album-item[data-pg-context]" \
                ##        data-pg-name="children">
                ##        Edit order by dragging
                ##    </p>
                ##</div>
            % endif

        % for item_id, item in items:
            <li class="album-item" \
                data-pg-id="${item_id}" \
                data-pg-context="${item.name}">
                <div class="album-cell">
                <!-- max 1024x536 -->
                    <div class="album-container">
                        <a class="album-link"
                            title="${item.description}"
                            href="${request.resource_url(item, '@@'+request.view_name) | n}">
                        <img class="image-box"
                            alt="${item.name}"
                            width="${small_width(item)}"
                            height="${small_height(item)}"
                            src="/static/img/spacer.gif"
                            data-src="${small_url(item) | n}" />
                        </a>
                    </div>
                    % if editing:
                        <div class="preview-picture-edit" style="width: ${small_width(item)}px;">
                            <p class="pg-edit-select-preview-picture" \
                                data-pg-id="select-preview-picture-dialog" \
                                data-pg-context="${item.name}">
                                Select preview picture
                            </p>
                            <p class="pg-edit-preview-picture" \
                                data-pg-id="preview-picture-dialog" \
                                data-pg-context="${item.name}">
                                Edit preview picture
                            </p>
                        </div>
                    % endif
                    <div class="album-info" style="width: ${small_width(item)}px;">
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
