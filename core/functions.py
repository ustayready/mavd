import requests
import re


def clean_string(title):
	pattern = re.compile('([^\s\w]|_)+')
	title = pattern.sub('', title).lower()
	title = title.replace(' ','-')

	return title


def clean_url(url):
	url = url.split('')[0]
	url = url.split('>')[0]

	if len(url) > 9:
		return url
	else:
		return None