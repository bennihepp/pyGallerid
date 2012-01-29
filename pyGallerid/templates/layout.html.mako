## layout.mako

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
## Use Chrome Frame on Internet Explorer
<meta http-equiv="X-UA-Compatible" content="chrome=1">

<title><%block name="html_title"/></title>

## <!-- Add stylesheets -->
<%block name="stylesheets">

    <link rel="stylesheet" type="text/css" href="/static/css/global.css" media="screen" />
    <link rel="stylesheet" type="text/css" href="/static/css/pyGallerid.css" media="screen" />
    ## <!--[if lte IE 7]>
    ## <link rel="stylesheet" type="text/css" href="/static/css/global_ie.css" />
    ## <![endif]-->

    ## fancybox
    ##<link rel="stylesheet" href="/static/js/jquery/jquery.fancybox.css" type="text/css" media="screen" />
    ## shadowbox
    ##<link rel="stylesheet" type="text/css" href="/static/js/shadowbox/shadowbox.css">

</%block>

<%block name="html_header"/>

</head>

<body<%block name="html_body_tags"/>>

    ## Prompt for Chrome Frame installation in IE
    <!--[if IE]>

        <script type="text/javascript" 
            src="http://ajax.googleapis.com/ajax/libs/chrome-frame/1/CFInstall.min.js">
        </script>

        <div id="prompt">
        </div>

        <script>
            window.attachEvent("onload", function() {
                CFInstall.check({
                    mode: "inline",
                    node: "prompt"
                });
            });
        </script>

    <![endif]-->

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
        <%block name="footer">
          <div class="copyright">
            © Copyright 2011-2012 Benjamin Hepp<br \>
            benjamin (at) hepp.webfactional.com
          </div>
        </%block>
      </div>

    </div>

    <%block name="scripts">
        ## <!-- Add javascript libraries -->
        ## jquery
        ##<script type="text/javascript" src="/static/js/jquery/jquery-1.7.1.min.js"></script>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        ## <script type="text/javascript" src="/static/js/jquery/jquery.mousewheel-3.0.6.pack.js"></script>
        ## simplemodal
        <script type="text/javascript" src="/static/js/jquery/jquery.simplemodal.1.4.2.min.js"></script>
        ## fancybox
        ##<script type="text/javascript" src="/static/js/jquery/jquery.fancybox.pack.js"></script>
        ## shadowbox
        ##<script type="text/javascript" src="/static/js/shadowbox/shadowbox.js"></script>
        ## Galleria
        ##<script type="text/javascript" src="/static/js/galleria/galleria-1.2.6.min.js"></script>
        ## pyGallerid
        <script type="text/javascript" src="/static/js/pyGallerid.js"></script>
    </%block>

</body>
</html>
