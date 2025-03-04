import requests
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
import sys
from urllib.parse import urlparse
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import re
import time
import os
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
from findJS import *

for arg in sys.argv:
	if arg.find("http:") != -1 or arg.find("https:") != -1:
		BASE_URL = arg

def exitAndHelp():
    print('[-] Please enter a valid URL')
    print('Usage: python3 findUrls.py [-s] [-v] https://yourwebsite/')
    print('       -s       Enable Spider mode. Will repeat the scan for every new URL found')
    print('       -v       Enable Verbose mode. To display all found URLs')
    sys.exit()
    
try:
	url_check = urlparse(BASE_URL)
except Exception as e:
	exitAndHelp()

if url_check.scheme == '' or url_check.netloc == '' :
    exitAndHelp()

print(f'[+] Scanning url: {BASE_URL}')
print('')
print('-----------------------------------------------------------')
DOMAIN = url_check.netloc
FOUND_URLS = []
DONE_URLS = []
SPIDER = '-s' in sys.argv
VERBOSE = '-v' in sys.argv

CURRENT_DIR = os.getcwd()
timestamp = str(time.time()).split(".")[0]
OUTPUT_PATH = CURRENT_DIR + '/findUrls_result_' + timestamp + '_' + DOMAIN + '.txt'

def main():
    global FOUND_URLS,DONE_URLS

    urls = getURLS(BASE_URL)
    urls = removeDuplicatesList(urls)
    urls = buildURLS(urls)
    urls = excludeOtherDomainsURLS(urls,BASE_URL)

    FOUND_URLS = FOUND_URLS + urls
    
    writeURLStoFile(FOUND_URLS)
    if VERBOSE:
    	printAllElementsOfList(FOUND_URLS)
    
    DONE_URLS.append(BASE_URL)
    
    if len(FOUND_URLS) == 0 :
        print('[-] No new URL found, try another URL')
        sys.exit()

    newurlsfound = True
    if SPIDER :                                             #if Spider mode activated
        while newurlsfound :                                #while we find new URLS
            newurlsfound = False
            for url in FOUND_URLS :
                if url not in DONE_URLS \
                and (url.split(".")[-1] != 'png' \
                and url.split(".")[-1] != 'css' \
                and url.split(".")[-1] != 'svg' \
                and url.split(".")[-1] != 'jpg' \
                and url.split(".")[-1] != 'jpeg' \
                and url.split(".")[-1] != 'ico') \
                and url.find("#") == -1 :
                    print('')
                    print(f'[+] Scanning url: {url}')
                    urls = getURLS(url)
                    urls = removeDuplicatesList(urls)
                    urls = buildURLS(urls)
                    urls = excludeOtherDomainsURLS(urls,BASE_URL)
                    new_urls = getNewURLS(urls)
                    
                    if len(new_urls) != 0 :
                        newurlsfound = True 	                  # to continue spidering
                        for new_url in new_urls:
                            FOUND_URLS.append(new_url)
                        writeURLStoFile(FOUND_URLS)             # to save already discovered urls
                        if VERBOSE:
                            printAllElementsOfList(new_urls)
                    DONE_URLS.append(url)

        writeURLStoFile(FOUND_URLS) # Writting urls into a file
        print('')
        print(f'[+] File written to {OUTPUT_PATH}')
        print('')

#Print all elements of a list (one per line)
#(none)
def printAllElementsOfList(table):
    temp = table.copy()
    temp = list(set(temp))
    temp.sort()
    for el in temp:
        print(el)

#Write URLS into a file
#(none)
def writeURLStoFile(url_list):
    file = open(OUTPUT_PATH,'w+',encoding='utf-8')
    temp = url_list.copy()
    temp = list(set(temp))
    temp.sort()
    for url in temp :
        file.write(url + '\n')
    file.close()

#Return a list with the new URLS only
#(list --> list)
def getNewURLS(url_list):
    result = []
    for link in url_list :
        if link.find("#") == -1 :
            if link not in FOUND_URLS :
                result.append(link)
        else:
            if link.split("#")[0] not in FOUND_URLS :
                result.append(link.split("#")[0])
    return result

#Return a list of the URLS found in a page (parsed from the HTTP response)
#(str --> list)
def getURLS(url):
    rheaders = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url,headers=rheaders,verify=False)
        response = r.text
        result = []
        for link in findPattern('href\=\"([^"]+)"',response):
            result.append(link)
        for link in findPattern("href\=\'([^']+)'",response):
            result.append(link)
        for link in findPattern('src\=\"([^"]+)"',response):
            result.append(link)
        for link in findPattern("src\=\'([^']+)'",response):
            result.append(link)
        for link in findPattern('action\=\"([^"]+)"',response):
            result.append(link)
        for link in findPattern("action\=\'([^']+)'",response):
            result.append(link)
        for link in findPattern('content\=\"([^"]+)"',response):
            result.append(link)
        for link in findPattern("content\=\'([^']+)'",response):
            result.append(link)
    except Exception as e:
        print("[-] Error while requesting " + url)
        print(str(e))
        result = []
    return result

#Delete duplicates in a list 
#(list --> list)
def removeDuplicatesList(url_list) :
    result = url_list.copy()
    return list(set(result))

#Build URLS for non url links (#, /path/, ...)
#(list --> list)
def buildURLS(url_list):
    result = []
    for link in url_list :
        if link is None or len(link) == 0 :
            pass
        elif len(link) == 1 :
            result.append(BASE_URL + link)
        elif link[:2] == '//' :
            result.append(urlparse(BASE_URL).scheme + ':' + link)
        elif link[0] == '/' :
            result.append(urlparse(BASE_URL).scheme + '://' + urlparse(BASE_URL).netloc + link)
        elif link[0] == "#" or link[0] == "?" or link[0] == "@" or link[0] == ":" :
            result.append(BASE_URL + link)
        else :
            result.append(link)
    return result

#Exlude URLS from other domains
#(list --> list)
def excludeOtherDomainsURLS(url_list,base_url):
    result = []
    for link in url_list :
        if urlparse(link).netloc == DOMAIN :
            result.append(link)
    return result

def getDomain(url):
    try:
        return urlparse(url).netloc
    except Exception as e:
        print(e)
        sys.exit()

if __name__ == '__main__' :
    main()
    print('-----------------------------------------------------------')
    print('')
