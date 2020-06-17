import re
import lxml.html
from urllib.parse import urlparse, urldefrag
from utils import seenValidURL, relativeLink, simhash, hammingRatio, seenHashes


def scraper(url, resp):
	if not resp.raw_response:
		return []
	elif resp.status >= 400:
		return []
	else:
		doc = lxml.html.fromstring(resp.raw_response.content)
		try:
			text = doc.xpath('//h1//text()')
			text.extend(doc.xpath('//h2//text()'))
			text.extend(doc.xpath('//h3//text()'))
			text.extend(doc.xpath('//h4//text()'))
			text.extend(doc.xpath('//h5//text()'))
			text.extend(doc.xpath('//h6//text()'))
			text.extend(doc.xpath('//p//text()'))
			h, text = simhash(text)
			for seenHash in seenHashes:
				assert(hammingRatio(h, seenHash) < 0.90), f"Failed Hamming ratio {h}, {seenHash}"
			seenHashes.add(h)
			with open('documents/' + str(h) + '.txt', 'x') as file:
				file.write(str(url) + '\n')
				for word, count in text.items():
					file.write(str(word) + ' ' + str(count) + '\n')

		except (FileExistsError, AssertionError, UnicodeDecodeError) as e:
			print(e)
			return extract_next_links(url, doc)
		
	return extract_next_links(url, doc)


def extract_next_links(url, doc):
	return [link[2].strip('/') for link in doc.iterlinks() if is_valid(link[2].strip('/'), url)]


def is_valid(url, base=None):
	try:
		pattern = r"^(?P<standard>(www.)?(.*\.)?i?cs\.uci\.edu|(www.)?(.*\.)?cs\.uci\.edu|(www.)?(.*\.)?informatics\.uci\.edu|(www.)?(.*\.)?stat\.uci\.edu)$|^(?P<today>today\.uci\.edu)$"
		parsed = urlparse(url)
		with open('failedLinks.txt', 'a') as bad:
			if parsed.scheme not in ["http", "https"]:
				return False
			elif url in seenValidURL:
				return False
			elif re.search(
				r".*\.(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|xlsm|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
				return False
			elif urldefrag(url)[1]:
				bad.write('Fragment\t' + url + '\n')
				return False
			elif re.search('[12]\d{3}[-\/]([0][1-9]|1[012])', url):
				bad.write('Date\t' + url +'\n')                
				return False
			elif re.search('\/tag\/|\/category\/|\/wp-|\/very-top-footer-menu-items\/', parsed.path.lower()):
				bad.write('Tag\t' + url + '\n')
				return False
			else:
				match = re.match(pattern, parsed.netloc.lower())
				if match:
					if 'standard' in match.groupdict():
						return True
					elif 'today' in match.groupdict():
						if re.match('^\/department\/information_computer_sciences.*$', parsed.path.lower()):
							return True
				elif base:
					match = re.match(pattern, relativeLink(base, url))
					if match:
						if 'standard' in match.groupdict():
							return True
						elif 'today' in match.groupdict():
							if re.match('^\/department\/information_computer_sciences.*$', parsed.path.lower()):
								return True
		return False
	except TypeError:
		print("TypeError for ", parsed)
		raise
