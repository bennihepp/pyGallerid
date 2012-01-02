## view_album.mako
<%inherit file="layout.mako"/>

<%block name="title">View album</%block>

<%block name="body">
<div class="username">
	Username: ${username}
</div>
<div class="pictures">
    <ol>
        % for picture in pictures.values():
            <il>
                <a href="${picture_href(picture)}">${picture.name}</a>
            </il>
        % endfor
    </ol>
</div>
</%block>
