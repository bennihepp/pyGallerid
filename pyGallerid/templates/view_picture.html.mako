## view_album.mako
<%inherit file="layout.html.mako"/>

<%block name="title">View picture</%block>

<%block name="body">
<div class="username">
	Username: ${username}
</div>
<div class="album">
	Album name: ${album.name}
</div>
<div class="picture">
    Picture name: ${picture.name}<br />
	Original URL: <a href="${original_url(picture)}">${original_url(picture)}</a><br />
	Display URL: <a href="${display_url(picture)}">${display_url(picture)}</a><br />
	Thumbnail URL: <a href="${thumbnail_url(picture)}">${thumbnail_url(picture)}</a><br />
</div>
</%block>
