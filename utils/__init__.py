import os
import logging
from hashlib import md5, sha256
from urllib.parse import urlparse
from re import match, findall
from collections import defaultdict

#Global variable declarations
global stopWords
stopWords = frozenset(["a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","only","or","other","ought","our","ours", "ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves""then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself", "yourselves"])
global wordCounts
wordCounts = defaultdict(int)
global seenValidURL
seenValidURL = set()
global seenHashes
seenHashes = set()


def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
       "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_urlhash(url):
    parsed = urlparse(url)
    # everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()

def normalize(url):
    if url.endswith("/"):
        return url.rstrip("/")
    return url

def cleanURL(url):
    def findMatch(d):
        m = [key for key, value in d.items() if value != None]
        return m[0] if len(m) == 1 else None

    m = match('^https?:\/\/(www\.)?(?P<ics>(.*\.)?ics\.uci\.edu.*)|(?P<cs>(.*\.)?cs\.uci\.edu.*)|(?P<stat>(.*\.)?stat\.uci\.edu.*)|(?P<informatics>(.*\.)?informatics\.uci\.edu.*)|(?P<today>https?:\/\/today\.uci\.edu\/department\/information_computer_sciences.*)$', url)
    if m:
        m = findMatch(m.groupdict())
        return m
    else:
        return None
		   
    
def relativeLink(base, path):
	base = base.strip('/')
	path = path.strip('/')
	return base + '/' + path + '/'
	

def simhash(text : [str]):
	freq = computeTokenFrequencies(tokenize(text))
	V = ""
	hashdict = dict()
	for token in freq:
		hashdict[token] = int(md5(token.encode('utf-8')).hexdigest(), 16)
	bit = 1
	for _ in range(128):
		currentCount = 0
		for token, hashValue in hashdict.items():
			if bit & hashValue:
				currentCount += freq[token]
			else:
				currentCount -= freq[token]
		V += '1' if currentCount > 0 else '0'
		bit = bit << 1
	return (int(V, 2), freq)


	


def tokenize(text : [str]):
	pattern = r"(?P<word>[a-z0-9]+(?:'[a-z]+)?)"
	tokens = []
	for line in text:
		line = line.lower()
		for word in line.split():
			m = match(pattern, word)
			if m and m.groupdict()['word'] and m.groupdict()['word'] not in stopWords:
						tokens.append(m.groupdict()['word'])
	return tokens


def computeTokenFrequencies(tokens : [str]):
	count = defaultdict(int)
	for token in tokens:
		count[token] += 1
	return count


def hammingRatio(h1, h2):
	currentCount = 0
	bit = 1
	hashComp = h1 ^ h2
	for _ in range(128):
		if bit & hashComp:
			currentCount += 1
		bit = bit << 1
	return (1-currentCount/128)


a, b = simhash(["oh", "ok"])
print(a, b)
