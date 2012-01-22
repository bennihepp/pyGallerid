## view_document.html.mako

<%inherit file="gallery_layout.html.mako"/>

<%namespace file="gallery_layout.html.mako" name="helper"/>

<%block name="body">

<div class="content-description">
    <p class="pg-editable" \
        data-pg-context="" \
        data-pg-type="attribute-multiline-text" \
        data-pg-name="long_description">
        ${document.long_description | n}
    </p>
</div>
<div class="content-description-bottom-line">
</div>

</%block>
