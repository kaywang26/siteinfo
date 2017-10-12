u'''
Author: Kay Wang  kay.wang26@gmail.com

This module is the implementation of SiteInfo class.
You can get following information by calling the class object's get_site_info method:    

1. Title, Description, Keywords
   Get the data by parsing HTML response for accessing the url. 
   Use Python library selenium in order to get the complete JavaScript rendered page.  
   Selenium requires a Web driver to interface with the chosen browser:
   FireFox: geckodriver
   Chrome: chromedriver
   Safari: https://webkit.org/blog/6900/webdriver-support-in-safari-10/
   
2. Organization, Email, Telephone, Fax, Address
   Get the data by calling whoisxmlapi RESTful API
   
3. Time Zone Offset, Time Zone Name
   Call Google Map Geocoding RESTful API to get the latitude
   and longitude from the address, then call Google Map Time
   zone RESTful API to get the time zone information.
   
4. E-commerce Platform
   Get the data by parsing HTML response for accessing www.builtwith.com. 
   Use Python library selenium in order to get the complete JavaScript rendered page. 
   In my opinion, the best way is calling a RESTful API to get the E-commerce platform  
   information, but I couldn't find it due to time limitation, or maybe it doesn't exist.  
          
5. Alexa Global Ranking
   Get the data by calling Alexa Web Information Service API.
   I installed python-awis, however it didn't work because it was written in Python 2,
   I changed the code to make it work in Python 3. 

This file is written in Python 3
Required Python Libraries and Web Drivers:
    BeautifulSoup - parse HTML file. To install: pip install bs4
    Selenium Python Bindings - API to access Selenium WebDrivers
    geckodriver - Web driver to interface with Firefox
    python-awis - AWIS Python Wrapper
    
The response format of the 3rd party RESTful API is XML, I use Python standard library ElementTree to parse          
'''
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
import awis
from selenium import webdriver

VERSION = '1.0'

class SiteInfo:
    def __init__(self, url):
        self.url = url
        self.app_path = os.path.abspath(os.getcwd())
        self.logger = logging.getLogger('siteinfo.py')
        self.loginit() 
        self.info = [] # list of lists storing site information
                       # e.g. [['title','Amazon.com'], ['keywords','Amazon, Amazon.com, Books'] , ... ]  
        self.address = None                       
        
    def loginit(self):
        loghdlr = logging.FileHandler(os.path.join(self.app_path, 'siteinfo.log'))
        formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s - %(message)s', '%Y-%m-%d,%H:%M:%S') 
        loghdlr.setFormatter(formatter)
        self.logger.addHandler(loghdlr)
        self.logger.setLevel(logging.DEBUG)  
        self.logger.info('siteinfo.py version {0} started'.format(VERSION))  

    def httpget(self, url):
        u = None
        status = -1
        resp = ''
        try:
            with urllib.request.urlopen(url) as f:
                time.sleep(1)
                resp = f.read()
                status = f.getcode()
        except Exception as e:
            self.logger.error('HTTP request failed {0}: {1}'.format(url, str(e))) 
        return status, resp   

    def get_admin_from_whois(self, whois_url):
      try:
        status, resp = self.httpget(whois_url)
        #print('status {0}'.format(status))
        
        root = et.fromstring(resp)
        with open(os.path.join(self.app_path, 'whois.xml'), 'w', encoding='utf-8') as f:
            print(et.tostring(root, encoding="unicode"), file=f)
            
        admin = root.find('.//administrativeContact')
        if admin == None:
            return False
        for child in admin.iter():
            if child.tag != 'name' and child.tag != 'rawText' and child.tag != 'unparsable' and child.tag != 'administrativeContact':
                if child.tag == 'street1':
                    street1 = child.text
                elif child.tag == 'city':
                    city = child.text
                elif child.tag == 'state':
                    state = child.text
                elif child.tag == 'postalCode':
                    postalCode = child.text 
                elif child.tag == 'country':
                    country = child.text 
                else:
                    self.info.append([child.tag, child.text])
        self.address = '{0} {1} {2} {3} {4}'.format(street1, city, state, postalCode, country)           
        self.info.append(['Address', self.address])
      except Exception as e:
        self.logger.error('exception accessing {0}:{1}'.format(whois_url, str(e)))
        return False        
      return True         
    
    def get_ecommerce_from_builtwith(self, builtwith_url):
      try:
        #status, resp = self.httpget(builtwith_url)
        driver = webdriver.Firefox(executable_path = 'C:\\Users\\qch2041\\AppData\\Local\\Programs\\Python\\Python36-32\\geckodriver.exe')
        driver.get(builtwith_url)
        time.sleep(5)
        resp = driver.page_source
        soup = BeautifulSoup(resp, 'html.parser')
        driver.quit()
        #print('status {0}'.format(status)) 
        #with open(os.path.join(self.app_path, 'walmart_builtwith.html'), 'w', encoding='utf-8') as f:
            #print(soup.prettify(), file=f)

        ecommerce_span_tag = soup.find('span', string='Ecommerce')
        if ecommerce_span_tag != None:
            ecommerce_div_tag = ecommerce_span_tag.find_parent('div')
        else:
            return
    
        i = 0
        techitem_div_tags = ecommerce_div_tag.find_next_siblings('div')
        for techitem_div_tag in techitem_div_tags:
          #print('techitem_div_tag', techitem_div_tag)
          if 'techItem' not in techitem_div_tag.attrs["class"]: # class attribute is not like other attributes, it's a list
              break
          techitem_a_tags = techitem_div_tag.find('h3').find_all('a', limit=2)
          findit = techitem_a_tags[1]
          self.info.append(['E-commerce platform ' + str(i), findit.string])
          i += 1
      except Exception as e:
        self.logger.error('exception accessing {0}:{1}'.format(builtwith_url, str(e)))

    def get_latlon_from_google_geocode(self, google_geocode_url):
      try:
        status, resp = self.httpget(google_geocode_url)
        latlon = []
        root = et.fromstring(resp)
        with open(os.path.join(self.app_path, 'google_geocode.xml'), 'w', encoding='utf-8') as f:
            print(et.tostring(root, encoding="unicode"), file=f)
            
        location = root.find('.//location')
        latlon.append(location.find('lat').text) 
        latlon.append(location.find('lng').text)         
        return latlon
      except Exception as e:
        self.logger.error('exception accessing {0}:{1}'.format(google_geocode_url, str(e)))
        
    def get_timezone_from_google_timezone(self, google_timezone_url):
      try:
        status, resp = self.httpget(google_timezone_url)
        root = et.fromstring(resp)
        with open(os.path.join(self.app_path, 'google_timezone.xml'), 'w', encoding='utf-8') as f:
            print(et.tostring(root, encoding="unicode"), file=f)
            
        offset = root.find('.//raw_offset').text
        offset = float(offset)/3600
        timezone_name = root.find('.//time_zone_name').text
        self.info.append(['Time Zone Offset(hour)', offset]) 
        self.info.append(['Time Zone Name', timezone_name])  
      except Exception as e:
        self.logger.error('exception accessing {0}:{1}'.format(google_timezone_url, str(e)))     

    def get_ranking_from_awis(self, url): 
      try:
        api = awis.AwisApi("AKIAJ2JL77AEEWWH6K7Q", "yPYqsQCSanoPRhRJXugc7f4FtGikHq2xM5owN1s8")
        tree = api.url_info(url, "Rank", "LinksInCount") # url = 'www.walmart.ca'
        
        ns = {'ns0':'http://alexa.amazonaws.com/doc/2005-10-05/', 'ns1':'http://awis.amazonaws.com/doc/2005-07-11'}
        #elem = tree.find('.//{http://alexa.amazonaws.com/doc/2005-10-05/}StatusCode') # another format without defining ns
        elem = tree.find('.//ns0:StatusCode', ns)
        assert elem.text == "Success" 
        
        root = tree.getroot() 
        with open(os.path.join(self.app_path, 'alexa.xml'), 'w', encoding='utf-8') as f:
            print(et.tostring(root, encoding="unicode"), file=f)
        self.info.append(['Alexa Global Ranking', root.find('.//ns1:Rank', ns).text])
      except Exception as e:
        self.logger.error('exception calling AWIS API for {0}:{1}'.format(url, str(e)))
        
    def get_site_info(self):
      try:
        #status, resp = self.httpget(self.url)
        driver = webdriver.Firefox(executable_path = 'C:\\Users\\qch2041\\AppData\\Local\\Programs\\Python\\Python36-32\\geckodriver.exe')
        driver.get('http://' + self.url)
        time.sleep(5)
        resp = driver.page_source
        soup = BeautifulSoup(resp, 'html.parser')
        driver.quit()
        #with open(os.path.join(self.app_path, 'page_source.html'), 'w', encoding='utf-8') as f:
            #print(soup.prettify(), file=f)
      except Exception as e:
        self.logger.error('exception accessing {0}:{1}'.format(self.url, str(e)))
        print('{0} is unaccessible'.format(self.url))
        return self.info
    
      try:    
        title = soup.title
        if title != None:    
            self.info.append(['Title', title.string]) 
        else:
            title = soup.find('meta', {'name':'title'})
            if title != None:
                self.info.append(['Title', title['content']])
        
        description = soup.find('meta', {'name':'description'})
        if description != None:
            self.info.append(['Description', description['content']])
        
        keywords = soup.find('meta', {'name':re.compile('^keyword')}) # some sites like thebay uses "keyword" instead of "keywords"
        if keywords != None:
            self.info.append(['Keywords', keywords['content']])
            
        # Find social media pages
        facebook_pages = soup.find('a', {'href':re.compile('facebook.com')}) 
        if facebook_pages != None:
            self.info.append(['facebook', facebook_pages['href']])  
        twitter_pages = soup.find('a', {'href':re.compile('twitter.com')}) 
        if twitter_pages != None:
            self.info.append(['twitter', twitter_pages['href']]) 
        linkedin_pages = soup.find('a', {'href':re.compile('linkedin.com')}) 
        if linkedin_pages != None:
            self.info.append(['linkedin', linkedin_pages['href']]) 
        youtube_pages = soup.find('a', {'href':re.compile('youtube.com')}) 
        if youtube_pages != None:
            self.info.append(['youtube', youtube_pages['href']]) 
        instagram_pages = soup.find('a', {'href':re.compile('instagram.com')}) 
        if instagram_pages != None:
            self.info.append(['instagram', instagram_pages['href']]) 
        googleplus_pages = soup.find('a', {'href':re.compile('google.com/\+')}) 
        if googleplus_pages != None:
            self.info.append(['google+', googleplus_pages['href']])            
      except Exception as e:
        self.logger.error('exception parsing source of {0}:{1}'.format(self.url, str(e)))
     
      try:     
        '''
        Get E-commerce by parsing HTML response for accessing www.builtwith.com
        url = 'www.walmart.ca'
        builtwith_url = 'http://www.builtwith.com/www.walmart.ca'
        '''
        builtwith_url = 'http://www.builtwith.com/{0}'.format(self.url)
        self.get_ecommerce_from_builtwith(builtwith_url) 
        
        '''
        Get Alexa ranking from Alexa Web Information Service API
        '''
        self.get_ranking_from_awis(self.url)        
        
        '''
        Get Admin data by calling whoisxmlapi RESTful API
        url = 'www.walmart.ca'
        whois_url = 'https://www.whoisxmlapi.com/whoisserver/WhoisService?domainName=www.walmart.com&username=kwang&password=123456'
        '''
        whois_url = 'https://www.whoisxmlapi.com/whoisserver/WhoisService?domainName={0}&username=kwang&password=123456'.format(self.url)
        if self.get_admin_from_whois(whois_url) == False:
            return self.info
       
        '''        
        Get lat/long by calling Google Map Geocoding RESTful API 
        google_geocode_url = 'https://maps.googleapis.com/maps/api/geocode/xml?address=xxxxx&key=AIzaSyC2NcgPW08eIRHNAElrYUw5zJgVroFI7Yw'
        '''
        address = self.address.replace(' ', '+')
        google_geocode_url = 'https://maps.googleapis.com/maps/api/geocode/xml?address={0}&key=AIzaSyC2NcgPW08eIRHNAElrYUw5zJgVroFI7Yw'.\
                              format(address)
        latlon = self.get_latlon_from_google_geocode(google_geocode_url)  
        if latlon == []:
            return self.info       

        '''
        Get time zone by calling Google Map Time zone RESTful API
        google_timezone_url = 'https://maps.googleapis.com/maps/api/timezone/xml?location=lat,lon&timestamp=xxxxxxxxxx&key=AIzaSyAwuYCM0yJEKoDexqItPqO16ViE3169yZE'
        '''
        t = time.time()
        google_timezone_url = 'https://maps.googleapis.com/maps/api/timezone/xml?location={0},{1}&timestamp={2}&key=AIzaSyAwuYCM0yJEKoDexqItPqO16ViE3169yZE'. \
                               format(latlon[0], latlon[1], t)
        self.get_timezone_from_google_timezone(google_timezone_url)

        return self.info
      except Exception as e:
        self.logger.error('exception {0}:{1}'.format(self.url, str(e)))
        return self.info