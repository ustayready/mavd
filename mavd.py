#!/usr/bin/env python
from core.functions import *
from core.objects import *
from core.apk import *
import multiprocessing, argparse, sys


def main(config):
	download_queue = []
	apks = []

	if config.local_apk:

		apk = Apk()
		apk.app_name = config.local_apk.split('/')[-1]
		apk.local_file = config.local_apk
		apk.use_cache = config.use_cache
		apk.show_ide = config.show_ide
		apk.strict_search = config.strict_search
		apk.show_secrets = config.show_secrets

		reversed_apk = reverse_apk(apk)

		print('[*] Found secrets in app {}: {} URL\'s and {} interesting keywords'.format(
				reversed_apk.app_name,
				len(reversed_apk.found_urls),
				len(reversed_apk.found_keywords)
			)
		)

	else:
		if config.domain:
			apks = find_apks_by_domain(config.domain, config.strict_search)
		else:
			apks = find_apk_by_name(config.apk)

		for app in apks:
			app.use_cache = config.use_cache
			app.show_ide = config.show_ide
			app.strict_search = config.strict_search
			app.show_secrets = config.show_secrets

			# TODO: use verify_vendor
			verify_apk(app)

	 		if app.vendor_match or not config.domain:
				# TODO: Multi-process getting links
				inflate_apk_link(app)

				if app.download_link:
					download_queue.append(app)

		print('[*] Found {} download link(s)!'.format(len(download_queue)))
		print('[*] Downloading app(s)...')

		if len(download_queue) == 1:
			ready_apk = download_apk(download_queue[0])

			print('[*] Downloaded app: {}'.format(ready_apk.local_file))

			reversed_apk = reverse_apk(download_queue[0])

			print('[*] Found secrets in app {}: {} URL\'s and {} interesting keywords'.format(
					reversed_apk.app_name,
					len(reversed_apk.found_urls),
					len(reversed_apk.found_keywords)
				)
			)

		elif len(download_queue) > 0:
				download_processes = multiprocessing.Pool(len(download_queue))
				ready_queue = download_processes.map(download_apk, download_queue)

				for ready_apk in ready_queue:
					print('[*] Downloaded app: {}'.format(ready_apk.local_file))

				reverse_processes = multiprocessing.Pool(len(ready_queue))
				reversed_queue = reverse_processes.map(reverse_apk, ready_queue)

				for reversed_apk in reversed_queue:

					print('[*] Found secrets in app {}: {} URL\'s and {} interesting keywords'.format(
							reversed_apk.app_name,
							len(reversed_apk.found_urls),
							len(reversed_apk.found_keywords)
						)
					)

	print('[*] Finished!')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--domain", help="domain name to search for apps")
	parser.add_argument("--apk-name", help="apk name to reverse engineer", dest="apk")
	parser.add_argument("--apk-file", help="apk filename to reverse engineer", dest="local_apk")
	parser.add_argument("--strict-search", help="strict search when searching apps", dest="strict_search", action="store_true", default=True)
	parser.add_argument("--show-ide", help="load app in IDE after reverse engineering", dest="show_ide", action="store_true", default=False)
	parser.add_argument("--show-secrets", help="print secrets to console", dest="show_secrets", action="store_true", default=True)
	parser.add_argument("--use-cache", help="use local cache when downloading apps", dest="use_cache", action="store_true", default=True)
	parser.add_argument("--verify-vendor", help="verify domain matches apps", dest="verify_vendor", action="store_true", default=True)

	args = parser.parse_args()

	if not args.domain and not args.apk and not args.local_apk:
		parser.print_help()
		print('\n[!] Error please provide a domain, APK name or local APK filename\n')
	else:
		config = Config()

		config.domain = args.domain
		config.apk = args.apk
		config.show_ide = args.show_ide
		config.strict_search = args.strict_search
		config.use_cache = args.use_cache
		config.show_secrets = args.show_secrets
		config.verify_vendor = args.verify_vendor
		config.local_apk = args.local_apk

		main(config)
