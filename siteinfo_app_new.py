'''
Author: Kay Wang  kay.wang26@gmail.com
Date: Oct. 16 2017

siteinfo_app_new.py is a Windows command line application. It makes use of
getsiteinfo library which is on pypi: https://pypi.python.org/pypi/getsiteinfo/0.1.0

How to run: 
    siteinfo_app_new.py the_url
    e.g. siteinfo_app_new.py www.walmart.ca
        
'''
#! python
import os
import sys
import urllib.request
import re
import errno
import time
import logging, logging.handlers
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et
from collections import OrderedDict
from selenium import webdriver
from getsiteinfo import GetSiteInfo

webdriver_dir = 'C:\\Users\\qch2041\\AppData\\Local\\Programs\\Python\\Python36-32\\geckodriver.exe'
awis_access_key_id = 'AKIAJ2JL77AEEWWH6K7Q'
awis_secret_access_key = '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'
whois_user = 'kwang'
whois_pass = '123456'
google_geocode_key = 'AIzaSyC2NcgPW08eIRHNAElrYUw5zJgVroFI7Yw'
google_timezone_key = 'AIzaSyAwuYCM0yJEKoDexqItPqO16ViE3169yZE'
   
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(' Usage: {0} url'.format(sys.argv[0]))
        sys.exit(errno.EINVAL)
        
    site = GetSiteInfo(sys.argv[1], webdriver_dir, whois_user, whois_pass, google_geocode_key, google_timezone_key, awis_access_key_id, awis_secret_access_key)
    site_info = site.get_site_info()
    for item in site_info:
        print(item[0], ':', item[1], '\n')
