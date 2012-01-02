## view_album.mako
<%inherit file="layout.mako"/>

<%block name="title">View picture</%block>

<%block name="body">
<div class="username">
	Username: ${username}
</div>
<div class="album">
	Album name: ${album.name}
</div>
<div class="picture">
    Picture name: ${picture.name}
</div>
</%block>
