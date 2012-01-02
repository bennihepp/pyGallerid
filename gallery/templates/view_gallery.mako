## view_gallery.mako
<%inherit file="layout.mako"/>

<%block name="title">View gallery</%block>

<%block name="body">
<div class="username">
	Username: ${username}
</div>
<div class="albums">
    <ol>
        % for album in albums.values():
            <il>
                <a href="${album_href(album)}">${album.name}</a>
            </il>
        % endfor
    </ol>
</div>
</%block>
