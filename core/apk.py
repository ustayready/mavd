import requests, re, subprocess, json, os
from bs4 import BeautifulSoup
from objects import Apk
from functions import * 
from constants import *


def inflate_apk_link(apk):
	try:
		apk_url = 'https://apkpure.com/{}/{}/download?from=developer'.format(apk.clean_name, apk.app_name)
		headers = {
			'user-agent' : 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
		}

		print('[*] Searching for download link for: {}'.format(apk.app_name))

		http = requests.get(apk_url, headers=headers)
		soup = BeautifulSoup(http.text, "lxml")
		link = soup.find('a', {'id': "download_link"})
		href = link.get('href')

		apk.download_link = href

		return apk
	except Exception as ex:
		return apk

def find_apk_by_name(apk_name):
	apks = []
	try:
			search_url = 'https://play.google.com/store/apps/details?id={}'.format(apk_name)
			http = requests.get(search_url)
			soup = BeautifulSoup(http.text, "lxml")

			app_apk = Apk()

			name = soup.find("div", class_ = "id-app-title")
			vendor = soup.find("a", class_ = "document-subtitle primary").find('span')

			app_apk.app_name = apk_name
			app_apk.name = name.text.strip()
			app_apk.clean_name = clean_string(app_apk.name)
			app_apk.google_url = '/store/apps/details?id={}'.format(apk_name)
			
			app_apk.vendor = vendor.text.strip()

			apks.append(app_apk)

			return apks

	except Exception as ex:
		print('[!] Error searching for apk using name: {} -> {}'.format(apk_name, ex))
		return None

def find_apks_by_domain(domain, strict=False):
	try:
		search_url = None

		if strict:
			search_url = 'https://play.google.com/store/search?q=%22%40{}%22&c=apps'.format(domain)
		else:
			search_url = 'https://play.google.com/store/search?q=%40{}&c=apps'.format(domain)

		http = requests.get(search_url)
		soup = BeautifulSoup(http.text, "lxml")
		
		apks = []
		
		print('[*] Searching apps using domain: {}'.format(domain))

		for app in soup.find_all("div", class_ = "card-content id-track-click id-track-impression"):
			app_apk = Apk()

			cover = app.find("div", class_ = "cover")
			details = app.find("div", class_ = "details")
			subdetails = details.find("div", class_ = "subtitle-container")

			link = details.find("a", class_= "title")
			sublink = subdetails.find("a", class_= "subtitle")

			app_apk.app_name = app.get('data-docid').strip()
			app_apk.google_url = link.get('href').strip()
			app_apk.name = link.get('title').strip()
			app_apk.clean_name = clean_string(app_apk.name)
			app_apk.vendor = sublink.get('title')
			app_apk.search_domain = domain

			apks.append(app_apk)

		return apks
	except Exception as ex:
		print('[!] Error searching for apks using domain: {} -> {}'.format(domain, ex))
		return None


def download_apk(apk):
	local_file = '{}/{}.apk'.format(APK_DIR, apk.clean_name)

	try:
		continue_download = True

		if os.path.isfile(local_file):
			if apk.use_cache:
				continue_download = False

		if continue_download:
			r = requests.get(apk.download_link, stream=True)
			with open(local_file, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk:
						f.write(chunk)
		
		apk.local_file = local_file

		return apk
	except Exception as ex:
		return apk


def verify_apk(apk):
	app_url = 'https://play.google.com{}'.format(apk.google_url)

	try:
		http = requests.get(app_url)
		soup = BeautifulSoup(http.text, "lxml")

		dev_info = soup.find('div', class_ = 'details-section metadata')

		for info in dev_info.find_all('a', class_ = 'dev-link'):
			href = info.get('href')

			if href.startswith('https://www.google.com/'):
				# https://www.google.com/url?q=http://www.programacion4d.com&amp;sa=D&amp;usg=AFQjCNFief1csyYeqCD4t78HKrA1o9rUbg
				url_match = re.search(r"(?<=q=)(.*?)(?=&)", href)

				if url_match:
					if url_match.group(0):
						url = url_match.group(0)
						apk.vendor_website = url

			elif href.startswith('mailto'):
				email = href.split(':')[1]
				apk.vendor_email = email

		if apk.search_domain in apk.vendor_website or apk.search_domain in apk.vendor_email:
			apk.vendor_match = True

		print('[*] Verifying app {} belongs to {}... {}'.format(apk.app_name, apk.search_domain, apk.vendor_match))

		return apk
	except Exception as ex:
		return apk


def reverse_apk(apk):
	file_name = apk.local_file.split('/')[-1]
	apk_root = ''.join(file_name.split('.')[:-1])

	apk_path = '{}/{}'.format(APK_DIR, file_name)
	jar_path = '{}/{}.jar'.format(JAR_DIR, apk_root)
	files_path = '{}/{}/'.format(FILE_DIR, apk_root)

	print('[*] Reversing {} APK...'.format(file_name))
	subprocess.check_call([D2J, "-f", "-o", jar_path, apk_path])

	print('[*] Extracting {} source code...'.format(file_name))
	subprocess.check_call([UNZIP, "-o", "-qq", jar_path, "-d", files_path])

	print('[*] Searching files from {}'.format(files_path))
	interesting = search_apk_secrets(files_path, True, True)
	apk.found_urls = interesting['urls']
	apk.found_keywords = interesting['keywords']

	if apk.show_secrets:
		print('[*] Found URL(s) from {}: '.format(apk.app_name))
		for url_info in apk.found_urls:
			path = url_info['path']
			url = url_info['url']
			print('{} -> {}'.format(path,url))

		print('[*] Found Keywords(s) from {}: '.format(apk.app_name))
		for keyword_info in apk.found_keywords:
			path = keyword_info['path']
			keyword = keyword_info['keyword']
			print('{} -> {}'.format(path,keyword))


	print('[*] Launching {} in IDE? {}'.format(file_name, apk.show_ide))	
	if apk.show_ide:
		subprocess.check_call([JAVA, "-jar", JDGUI, jar_path])

	return apk


def search_apk_secrets(walk_dir, search_urls=False, search_secrets=False):
	interesting = {
		'urls' : [],
		'keywords' : []
	}

	for root, subdirs, files in os.walk(walk_dir):
		for filename in files:
			file_path = os.path.join(root, filename)

			with open(file_path, 'rb') as f:
				content = f.read()

				if search_urls:
					match_urls = re.search("(?P<url>https?://[^\s]+)", content)

					if match_urls:
						if match_urls.group(1):
							url = clean_url(match_urls.group(1))
							
							if url:
								interesting_url = {
									'path' : file_path,
									'url' : url
								}
								interesting['urls'].append(interesting_url)

				if search_secrets:
					for keyword in SECRETS:
						if keyword in content:
							interesting_secret = {
								'path' : file_path,
								'keyword' : keyword
							}
							interesting['keywords'].append(interesting_secret)
	
	return interesting