"""
Versions:
Anaconda 4.3.1 (x86_64), Python: 3.6.0
Selenium: 3.4.3
bs4: 4.5.3
chromedriver: 2.31 (for mac)
geckodriver: 0.18.0 (for mac)
Tor Browser: 6.5.2
Firefox browser: 55.0.3
"""

import urllib.request as ureq
import urllib 
import selenium
from selenium import webdriver
import requests
#from bs4 import BeautifulSoup as bs
#import pandas as pd
import re
import csv
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.webdriver import WebDriver as FD
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from tbselenium.tbdriver import TorBrowserDriver
import os
import codecs
import socks   # pip install PySocks
import socket
from stem import Signal
from stem.control import Controller


# for randomizing waiting time
import time
from random import randint

# for creating random user agent for webdriver
from fake_useragent import UserAgent



def get_tds_w_descriptions_ls(div_w_descriptions):
	tds_w_descriptions_ls = []
	for td in tds_w_descriptions:
		if(td.get('class')==[''] and td.get('style')=='text-align: left;' and (int(td.get('tabindex'))-2)%8==0):   # from all tds get specific ones that contain descriptions
			tds_w_descriptions_ls.append(td)
	return tds_w_descriptions_ls

def get_tds_w_cat_path_ls(div_w_descriptions):
	tds_w_cat_path_ls = []
	for td in tds_w_descriptions:
		if(td.get('class')==[''] and td.get('style')=='text-align: left;' and (int(td.get('tabindex'))-5)%8==0):   # from all tds get specific ones that contain category_path
			tds_w_cat_path_ls.append(td)
	return tds_w_cat_path_ls

def get_description_from_td(td):
	if(td.get('class')==[''] and td.get('style')=='text-align: left;' and (int(td.get('tabindex'))-2)%8==0):   # from all tds get specific ones that contain descriptions
		return td.select('span[title='']')[0].text
	else:
		return None

def get_cat_path_from_td(td):
	if(td.select('span[title='']') != []):
		return td.select('span[title='']')[0].text                      # original cat path
	else:
		return td.select("div[class='cell-staged-value']")[0].text      # edited cat path

def norm_str_to_alphanum(sentence_):
    printable_ = 'abcdefghijklmnopqrstuvwxyz0123456789'
    sentence_processed = "".join((char if char in printable_ else "") for char in str(sentence_).lower())
    
    return sentence_processed

def norm_str_to_alpha(sentence_):
    printable_ = 'abcdefghijklmnopqrstuvwxyz'
    sentence_processed = "".join((char if char in printable_ else "") for char in str(sentence_).lower())
    
    return sentence_processed

def experiment_code_1():
	img_link = 'https://images-na.ssl-images-amazon.com/images/I/618i-ri+HJL._AC_US480_QL65_.jpg'
	txt = open('/Users/altay.amanbay/Desktop/img.jpg', "wb")
	download_img = ureq.urlopen(img_link)
	txt.write(download_img.read())
	txt.close()

def chrome_options_random():
	rand_agent = UserAgent().random
	options = webdriver.ChromeOptions()
	return options.add_argument(rand_agent)

def open_log_txt(my_outfile_log):
	return codecs.open(my_outfile_log, "a", encoding='utf-8-sig', errors='ignore')

def switchIP():
    with Controller.from_port(port=9151) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
		

controller = Controller.from_port(port=9151)
def switchIP_2():
	global controller
	controller.authenticate()
	controller.signal(Signal.NEWNYM)


def get_IP_address(browser_):
	# browser_.get("http://www.icanhazip.com")
	# xpath_ip = "//body//pre"  # 'a' tag
	# ip_address_elem = browser_.find_elements_by_xpath(xpath_ip)

	ip_address_elem = None
	for i in range(0,3):
		while True:
			try:
				browser_.get("http://www.icanhazip.com")
				xpath_ip = "//body//pre"  # 'a' tag
				ip_address_elem = browser_.find_elements_by_xpath(xpath_ip)
			except TimeoutException:
				print('\nTimeout #%g, retrying ...' % i)
				print('Trial link: http://www.icanhazip.com')
				write_to_log_file(values_ls = ['\nTimeout 1, retrying ...\n', 'Trial link: http://www.icanhazip.com\n'])
				continue
				#browser_.refresh()
			break
			

	if(ip_address_elem is not None):
		return ip_address_elem[0].get_attribute("innerHTML")
	else:
		print('IP address not detected')
		return None

def write_to_log_file(values_ls = None):	
	with open_log_txt(my_outfile_log) as outfile_log:
		for i in values_ls:
			outfile_log.write(i)



# Global vars
PROFILE_glob = None
CAPABILITIES_glob = None
SCRIPT_DIR_glob = None
EXECUTABLE_PATH_glob = None
PROXY_ADDRESS_glob = None
PROXY_glob = None

def init_glob_vars():
	global PROFILE_glob
	global CAPABILITIES_glob
	global SCRIPT_DIR_glob
	global EXECUTABLE_PATH_glob
	global PROXY_ADDRESS_glob
	global PROXY_glob

	# Browser settings
	PROFILE_glob = FirefoxProfile('/Users/altay.amanbay/Library/Application Support/Firefox/Profiles')
	PROFILE_glob.set_preference("network.proxy.type", 1)
	PROFILE_glob.set_preference("network.proxy.socks", "127.0.0.1")
	PROFILE_glob.set_preference("network.proxy.socks_port", 9150)
	PROFILE_glob.set_preference("network.proxy.socks_version", 5)
	PROFILE_glob.set_preference("network.proxy.socks_remote_dns", True)
	PROFILE_glob.update_preferences()

	CAPABILITIES_glob = DesiredCapabilities.FIREFOX
	CAPABILITIES_glob["marionette"] = True
	CAPABILITIES_glob["binary"] = "/Applications/Firefox.app/Contents/MacOS/firefox-bin"

	# Proxy (start Tor browser before executing script)
	PROXY_ADDRESS_glob = "127.0.0.1:9150"  # localhost and Tor browser's default port number
	PROXY_glob = Proxy({
	    'proxyType': ProxyType.MANUAL,
	    'httpProxy': PROXY_ADDRESS_glob,
	})

	# Webdriver path
	SCRIPT_DIR_glob = os.path.dirname(os.path.abspath(__file__))
	print('Abs path:', SCRIPT_DIR_glob)
	EXECUTABLE_PATH_glob = SCRIPT_DIR_glob + '/webdrivers/geckodriver - v0.18.0/geckodriver'


# Print Selenium version
print('Selenium version: ', selenium.__version__)


if __name__ == '__main__':
	# ================================================================================================================================
	# Selenium implementation


	# --------------------------------------------------------------------------------------------------------------------------------
	# 0 - init web driver using tor as proxy
	init_glob_vars()
	browser_1 = webdriver.Firefox(capabilities = CAPABILITIES_glob
								,executable_path = EXECUTABLE_PATH_glob
								,proxy = PROXY_glob
								,firefox_profile = PROFILE_glob
								)



	# --------------------------------------------------------------------------------------------------------------------------------
	# Get starting url with Amazon's search results
	# Amazon's search results at page 1
	url_pg1 = 'https://www.amazon.com/s/ref=sr_pg_1?fst=as%3Aon&rh=n%3A1055398%2Cn%3A1063278%2Cn%3A1063298%2Cn%3A684541011%2Ck%3Aarea+rugs&keywords=area+rugs&ie=UTF8&qid=1501789698&spIA=B0168Y18HK,B0168Y1LOA,B01MYGFAXK,B06Y5VGDQJ,B073K1DKH5,B0742CVJRY,B06XSNH22G,B06XBHPFVK,B07424TKQX,B016WT6BNM,B06W5SXCXZ,B0716Y9D12,B01GIOSM2O,B00YFECHB2,B0168Y0DT4,B07427DB33,B01N3AMK9A,B06WGRJWW6,B01GS0VV62,B07428GBRN,B071JZLZN6,B01MUA3BTB,B00WGU6WSQ,B07234DWJX'

	page_count = 1
	prod_counter = 1
	img_num = 100 * prod_counter

	my_outfile_log = SCRIPT_DIR_glob+'/prod_data/logs.txt'
	my_outfile     = SCRIPT_DIR_glob+'/prod_data/prod_data.csv'
	outfile        = codecs.open(my_outfile, "w", encoding='utf-8-sig', errors='ignore')
	csv_writer     = csv.writer(outfile)

	my_outfile_2   = SCRIPT_DIR_glob+'/prod_data/prod_data_w_img_links.csv'
	outfile_2      = codecs.open(my_outfile_2, "w", encoding='utf-8-sig', errors='ignore')
	csv_writer_2   = csv.writer(outfile_2)

	# Start scraping
	while(url_pg1 != ''):
		# rotate ip address 1
		#switchIP()
		switchIP_2()

		# get ip address at icanhazip.com
		ip_address_str     = get_IP_address(browser_1)
		ip_address_log_str = 'IP addres for products pages: %s \n' % ip_address_str

		# log IP address
		write_to_log_file(values_ls = ['='*100+'\n', ip_address_log_str])


		# --------------------------------------------------------------------------------------------------------------------------------
		# 1.1 - open page
		browser_1.get(url_pg1)
		#print(type(browser_1))

		# 1.2 - wait for certain elements to be loaded completely implictly
		timeout = 10
		try:
		    element_present_1 = EC.presence_of_element_located((By.ID, 's-results-list-atf'))   # element 1 for waiting
		    element_present_2 = EC.presence_of_element_located((By.ID, 'pagnNextLink'))         # element 2 for waiting
		    WebDriverWait(browser_1, timeout).until(element_present_1, element_present_2)
		except TimeoutException:
		    print("Timed out waiting for page to load")


		# 1.3 - check if next page and get next page url for scraping
		next_page_xpath_1 = "//div[@id='centerBelowMinus']//a[@id='pagnNextLink']"  # 'a' tag
		next_page_link_ls = browser_1.find_elements_by_xpath(next_page_xpath_1)

		page_href = None
		curr_url = None
		if(len(next_page_link_ls) > 0):
			for pg in next_page_link_ls:
				next_page_url         = pg.get_attribute('href')
				next_page_url_log_str = 'Next products page %g url:\n %s \n\n' % (page_count+1, next_page_url)
				curr_page_url         = browser_1.current_url
				curr_page_url_log_str = 'Products curr_url:\n %s \n\n' % curr_page_url

				# log
				write_to_log_file(values_ls = ['='*100+'\n', curr_page_url_log_str, next_page_url_log_str])

				print('='*100)
				print('Curr page url: \n', curr_page_url)
				print('Next page url: \n', next_page_url, '\n')

				# save next page url for scraping
				url_pg1 = next_page_url
		else:
			url_pg1 = ''
			# log
			write_to_log_file(values_ls = ['no next page'])
			print('no next page')




		# --------------------------------------------------------------------------------------------------------------------------------
		# 2 - scrape prod names and links
		
		page_num   = 'page %g' % page_count
		page_count = page_count + 1
		
		csv_writer.writerow([page_num, curr_page_url, ''])
		csv_writer.writerow(['id', 'prod_name', 'prod_link'])

		csv_writer_2.writerow([page_num, curr_page_url])
		csv_writer_2.writerow(['Next page url:', next_page_url])

		xpath_1 = "//ul[@id='s-results-list-atf']//a[@class='a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal']"  # 'a' tags from 5th element of each 'li'
		a_ls = browser_1.find_elements_by_xpath(xpath_1)

		items_n_links = {}
		for idx, a in enumerate(a_ls):
			prod_name = a.get_attribute('title')
			prod_link = a.get_attribute('href')
			items_n_links[idx] = (prod_name, prod_link)

			csv_writer.writerow([idx, prod_name, prod_link])

			print()
			print(idx, prod_name)
			print(idx, prod_link)
			print()



		
		# --------------------------------------------------------------------------------------------------------------------------------
		# 3 - follow each prod link and scrape images
		print('\nProd items count: ', len(items_n_links))


		browser_2 = webdriver.Firefox(capabilities = CAPABILITIES_glob
								,executable_path = EXECUTABLE_PATH_glob
								,proxy = PROXY_glob
								,firefox_profile = PROFILE_glob
								)

		# iterate products
		for k, v in items_n_links.items():
			prod_name_n_link = v

			csv_writer_2.writerow([ 'Product name:', prod_name_n_link[0] ])
			csv_writer_2.writerow([ 'Product link:', prod_name_n_link[1] ])

			# rotate ip address 2
			#switchIP()
			switchIP_2()

			# get ip address at icanhazip.com
			ip_address_str     = get_IP_address(browser_2)
			ip_address_log_str = 'IP address for single product page: %s ' % ip_address_str
			prod_link_log_str  = 'Scraping single product :\n %s \n\n' % str(prod_name_n_link[1])

			# log IP address
			write_to_log_file(values_ls = [ip_address_log_str, prod_link_log_str])


			# 3.1 - open single product page

			#body = browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
			#browser_2.get(prod_name_n_link[1])

			for t in range(1,5):
				sleep_secs = 2 # randint(6, 11)
				time.sleep(sleep_secs)
				print('Trial %g forproduct page' % t)
				browser_2.get(prod_name_n_link[1])
				html_source = browser_2.page_source
				if(len(html_source) > 200000):
					break
				# else:
				# 	# rotate ip address 3
				# 	#switchIP()
				# 	switchIP_2() 

				# 	# get ip address at icanhazip.com
				# 	ip_address_str     = get_IP_address(browser_2)
				# 	ip_address_log_str = 'IP address for single product page: %s ' % ip_address_str
				# 	trial_msg = 'Trial %g triggered' % t

				# 	# log IP address
				# 	write_to_log_file(values_ls = [trial_msg, ip_address_log_str])



			

			# 3.2 - scrape script containning single product image urls
			xpath_2 = "//ul[@class='a-unordered-list a-nostyle a-button-list a-vertical a-spacing-top-micro']//li[contains(@class, 'a-spacing-small item imageThumbnail a-declarative') or contains(@class, 'a-spacing-small item videoThumbnail a-declarative')]//img"  # 'ul' tag containing all imgaes
			xpath_2 = "//div[@id='leftCol']//div[@id='imageBlock_feature_div']//script"
			img_ls = browser_2.find_elements_by_xpath(xpath_2)

			# 3.3 - split script containning single product image urls
			for img in img_ls:
				script_str = img.get_attribute("innerHTML")
				script_parts_ls = re.split(r"]|\[|{|}|,", script_str)

			# 3.4 - iterate script splits
			scrape_images = False
			for idx, p in enumerate(script_parts_ls):
				if('hiRes' in p and 'null' not in p):
					img_link_ls = p.split('":"')
					img_link = img_link_ls[1].replace('"','')
			
					csv_writer_2.writerow([ 'Image link:', img_link ])


					if(scrape_images == True):
						# change ip address 4
						switchIP()
						#switchIP_2()

						try:
							browser_2.get("http://www.icanhazip.com")
						except TimeoutException:
							print('\nTimeout 1, retrying ...')
							print('Trial link: http://www.icanhazip.com')
							#browser_2.refresh()
							browser_2.get("http://www.icanhazip.com")

						xpath_ip = "//body//pre"  # 'a' tag
						ip_address = browser_2.find_elements_by_xpath(xpath_ip)
						ip_address_str = '\tIP address for single image scrape: %s ' % ip_address[0].get_attribute("innerHTML")
						log_str = '\timage link %g: %s \n\n' % (idx, img_link)
						with open_log_txt(my_outfile_log) as outfile_log:
							outfile_log.write(ip_address_str)
							outfile_log.write(log_str)
						#socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9150)
						old_socket = socket.socket
						socks.setdefaultproxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9150)
						socket.socket = socks.socksocket
						#socket.getaddrinfo =  [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ("127.0.0.1", 9150))]


						img_num = img_num + 1
						txt = open(script_dir+'/prod_images/img_%g.jpg' % img_num, "wb")
						print('Image text urls: ', img_link)
						download_img = None
						try:
							download_img = ureq.urlopen(img_link)
						except Exception:
							print('\nTimeout 2, retrying ...')
							print('Trial links: %s' % img_link)
							download_img = ureq.urlopen(img_link)
							
						txt.write(download_img.read())
						txt.close()
						socket.socket = old_socket

						sleep_secs = 2 # randint(6, 11)
						time.sleep(sleep_secs)

			
			prod_counter = prod_counter + 1
			img_num = 100 * prod_counter


		# wait a bit and quit browser
		#sleep_secs = randint(6, 11)
		#time.sleep(sleep_secs)
		browser_2.close()
		#browser_2.quit()
		
		


	browser_1.close()
	#browser_1.quit()
	outfile.close()
	


