## layout.mako

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

<title><%block name="html_title">
Untitled Document
</%block></title>

<link rel="stylesheet" type="text/css" href="/static/css/global.css" media="screen" />
<link rel="stylesheet" type="text/css" href="/static/css/custom.css" media="screen" />
<!--[if lte IE 7]>
<link rel="stylesheet" type="text/css" href="/static/css/global_ie.css" />
<![endif]-->
<%block name="html_header"/>

## <!-- Add javascript libraries -->
<script type="text/javascript" src="/static/js/jquery/jquery-1.7.1.min.js"></script>
<link rel="stylesheet" href="/static/js/jquery/smoothness/jquery-ui-1.8.16.custom.css" type="text/css" media="screen" />
<script type="text/javascript" src="/static/js/jquery/jquery-ui-1.8.16.custom.min.js"></script>
<script type="text/javascript" src="/static/js/jquery/jquery.mousewheel-3.0.6.pack.js"></script>
<link rel="stylesheet" href="/static/js/jquery/jquery.fancybox.css" type="text/css" media="screen" />
<script type="text/javascript" src="/static/js/jquery/jquery.fancybox.pack.js"></script>
<script type="text/javascript" src="/static/js/gallery.js"></script>

</head>

<body<%block name="html_body_tags"/>>

<div class="container">

  <div class="header">
	<h1>
	  <%block name="header">
		<p>
		</p>
	  </%block>
	</h1>
  </div>

  <div class="content">
	${next.body()}
  </div>

  <div class="footer">
	<%block name="footer" />
  </div>

</div>

</body>
</html>
