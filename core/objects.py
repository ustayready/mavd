from functions import clean_string

class Apk():
	def __init__(self):
		self.name = None
		self.clean_name = None
		self.app_name = None
		self.google_url = None
		self.search_domain = None
		self.download_link = None
		self.local_file = None

		self.vendor = None
		self.vendor_website = None
		self.vendor_email = None
		self.vendor_match = False

		self.found_urls = []
		self.found_keywords = []

		self.strict_search = None
		self.show_ide = None
		self.use_cache = None
		self.show_secrets = None


	def __str__(self):
		return 'Name: {}\nApp Name: {}\nGoogle URL: {}\n'.format(
			self.name, self.app_name, self.google_url
		)

class Config():
	def __init__(self):
		self.domain = None
		self.apk = None
		self.show_ide = None
		self.strict_search = None
		self.use_cache = None
		self.show_secrets = None
		self.verify_vendor = None
		self.local_apk = None
