## layout.mako

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title><%block name="html_title">
Untitled Document
</%block></title>

<link rel="stylesheet" type="text/css" href="/static/css/global.css" />
<link rel="stylesheet" type="text/css" href="/static/css/custom.css" />
<!--[if lte IE 7]>
<link rel="stylesheet" type="text/css" href="/static/css/global_ie.css" />
<![endif]-->
<%block name="html_header"/>
</head>

<body>

<div class="container">
  <div class="header">
  <%block name="header_logo">
  <a href="#"><img src="" alt="Insert Logo Here" name="Insert_logo" width="20%" height="90" id="Insert_logo" style="background: #8090AB; display:block;" /></a>
  </%block>
  <%block name="header"/>
    <!-- end .header --></div>
  <div class="sidebar1">
  	<%block name="sidebar_menu">
    <ul class="nav">
    	% for name,href in menu_urls.items():
    		<li><a href="${href | h}">${name | h}</a></li>
        % endfor
    </ul>
    </%block>
    <%block name="sidebar_body">
    <p> The above links demonstrate a basic navigational structure using an unordered list styled with CSS. Use this as a starting point and modify the properties to produce your own unique look. If you require flyout menus, create your own using a Spry menu, a menu widget from Adobe's Exchange or a variety of other javascript or CSS solutions.</p>
    <p>If you would like the navigation along the top, simply move the ul.nav to the top of the page and recreate the styling.</p>
    </%block>
    <!-- end .sidebar1 --></div>
  <div class="content">
    <h1><%block name="title">Instructions</%block></h1>
	${next.body()}
    <!-- end .content --></div>
  <div class="footer">
  <%block name="footer">
    <p>This .footer contains the declaration position:relative; to give Internet Explorer 6 hasLayout for the .footer and cause it to clear correctly. If you're not required to support IE6, you may remove it.</p>
  </%block>
    <!-- end .footer --></div>
  <!-- end .container --></div>
</body>
</html>
