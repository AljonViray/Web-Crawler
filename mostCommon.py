from os import listdir
from collections import defaultdict
fileNames = listdir()
wordCount = defaultdict(int)
subdomainCount = defaultdict(int)


def mostCommon():
    for fileName in fileNames:
        with open(fileName) as file:
            file.readLine()
            for line in file:
                pair = line.split()
                wordCount[pair[0]] += int(pair[1])
    return wordCount.items()[:50]


def longestFile():
    max, url = 0, ""
    for fileName in fileNames:
        with open(fileName) as file:
            url = file.readLine()
            sum([int(line.split()[1]) for line in file])
            if sum > max:
                max = sum
                maxName = url

def uniqueURL():
    with open('goodlinks.txt') as file:
        return sum([1 for _ in url in file])

def subdomains():
    def scrubURL(url):
        m = match('(?P<scheme>https:\/\/|http:\/\/)?(?P<www>www\.)?(?P<url>.+)', url)
        if m:
            return m.groupdict()['url']
        else:
            return None

    with open('goodlinks.txt') as file:
        for url in file:
            subdomainCount[scrubURL(url)] += 1
    return subdomainCount
