# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 15:17:18 2020

@author: davek
"""

links = []
with open('sortedGoodLinks.txt') as sortedFiles, open('goodlinks.txt') as file:
	for link in file:
		links.append(link)
	links.sort()
	for link in links:
		sortedFiles.write(link + '\n')
		