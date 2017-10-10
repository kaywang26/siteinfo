#! python
#-----------------------------------------------------------------------------
#  File:        siteinfo_web_app.py
#  Description: This Web application is used for getting specific information
#               for a url. 
#  It's based on a web framework CherryPy which is a pure Python library.
#
#  Revision:
#  Date            Author          Description
#  Oct. 9 2017     Kay Wang        Initial version
#-----------------------------------------------------------------------------
import os
import sys
import shutil
import string
from configparser import ConfigParser
import cgi
import cherrypy
from siteinfo import SiteInfo


# These are in configuration file
server_name = None
server_port = None

def parse_config(file):
    global server_name, server_port, outdir   

    config = ConfigParser()
    config.read_file(open(file, 'r'))            
    
    server_name = config.get('app', 'server_name')
    server_port = int( config.get('app', 'server_port') )
    
    
class SiteInfoWeb(object):
    def __init__(self):
        self._text_tbl = {}
       
    def _indent(self, elem, level=0):
        ''' for pretty xml file '''
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i  
                
    
    def _template(self, section):
        parse_config(app_path + '\\app.conf')
        html = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Site Information</title>
        <style>
        #header {
            background-color:lightgray;
            text-align:center;}
        #footer {
            background-color:#39352d;
            color:white;
            position:fixed;
            bottom:0px;
            height:40px;
            width:100%%;
            text-align:center;}
        #div2 {
            width:2500px; 
            float:center;
            margin-top:5px;
            margin-bottom:5px;}
        form {text-align:left;}
        h3 {text-align:center;}
        </style>                
        </head>                
        <body>
            <div id="header">
                <table style="width:100%%">
                <tr>
                <td width="5%%"><img src="\\logo_forHQ.png" alt="Hubba logo" ></td>
                <td width="95%%"><h1>Site&nbsp;&nbsp; Information</h1></td>
                </tr>
                </table>
            </div>
            %s
            <div id="footer">
                Copyright 2017 © Hubba.&nbsp; All Rights Reserved.&nbsp; For Internal Use Only.
            </div>
        </body>
        </html>
        """ % section
        return(html)
        
    
    ############################################################################
    #                             Index Page
    ############################################################################
    @cherrypy.expose
    def index(self):
        section = """
        <div id="section">
        <form method="get" onsubmit="return validateForm()" action="submit_url">
            <p id="errmsg" style="color:red"></p>
            <div id="div2">
                <b>URL(example: http://www.walmart.ca):</b>
                <input id="urlinput" name="urlinput" type="text" maxlength="64" size="64" value=""/> 
                &nbsp;&nbsp;<input type="submit" value="Submit"/>
            </div>        
        </form>
        </div>
        """
        return self._template(section)        
        
    ############################################################################
    #                  Display site information
    ############################################################################
    @cherrypy.expose
    def submit_url(self, urlinput):
        site = SiteInfo(urlinput)
        site_info = site.get_site_info()
        section = """<h3>{0}</h3>""".format(urlinput)
        for k, v in site_info.items():
            section += """<p>
                          <b>{0}&nbsp;&nbsp;</b>""".format(k)        
            if k == 'Keywords':
                section += """
                <textarea rows = "6" cols = "100">{0}</textarea>
                </p>""".format(v)
                
            elif k == 'Description' or k == 'Title':
                section += """
                <textarea rows = "3" cols = "100">{0}</textarea> 
                </p>""".format(v)
            else:
                section += """
                <textarea rows = "1" cols= "100">{0}</textarea> 
                </p>""".format(v)            
        return self._template(section)
 
# instantiate instance of the class SiteInfoWeb   
site_info_web = SiteInfoWeb()

    
###################################################################################
#                                 Main function
###################################################################################
if __name__ == '__main__':
  app_path = os.path.abspath(os.getcwd())
  
  parse_config(app_path + '\\app.conf')
   
  conf = {
    '/': {
         'tools.sessions.on': True,
         'tools.staticdir.root': os.path.abspath(os.getcwd()),
         'tools.staticdir.on':  True,
         'tools.staticdir.dir': '.'
    },
  } 
  
  cherrypy.server.socket_host = server_name
  cherrypy.server.socket_port = server_port
  #cherrypy.quickstart(site_info_web, '/', conf)
  cherrypy.tree.mount(site_info_web, '/', conf)
  cherrypy.engine.start()
  cherrypy.engine.block()

