import requests
from bs4 import BeautifulSoup
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
import sys
from urllib.parse import urlparse
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time
import os
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)


BASE_URL = sys.argv[-1]
url_check = urlparse(BASE_URL)
#print(url_check)
if url_check.scheme == '' or url_check.netloc == '' :
    print('--> Please enter a valid URL')
    print('--> Usage: python3 findUrls.py [-s] https://yourwebsite/')
    print('-s       Enable Spider mode. Will repeat the scan for every new URL found')
    sys.exit()

print(f'--> Using url: {BASE_URL}')
print('')
print('-----------------------------------------------------------')
DOMAIN = url_check.netloc
FOUND_URLS = []
DONE_URLS = []
SPIDER = False
if '-s' in sys.argv :
    SPIDER = True

CURRENT_DIR = os.getcwd()
timestamp = str(time.time()).split(".")[0]
FILE_PATH = CURRENT_DIR + '/findUrls_result_' + timestamp + '_' + DOMAIN + '.txt'

def main():
    global FOUND_URLS,DONE_URLS

    urls = getURLS(BASE_URL)
    urls = removeDuplicatesURLS(urls)
    urls = buildURLS(urls)
    urls = excludeOtherDomainsURLS(urls,BASE_URL)

    for url in urls :
        FOUND_URLS.append(url)
        print(url)

    DONE_URLS.append(BASE_URL)
    newurlsfound = True

    if len(FOUND_URLS) == 0 :
        print('[-] --> No new URL found, try another URL')
        sys.exit()

    writeURLStoFile(FOUND_URLS)


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
                    print(f'--> Using url: {url}')
                    urls = getURLS(url)
                    urls = removeDuplicatesURLS(urls)
                    urls = buildURLS(urls)
                    urls = excludeOtherDomainsURLS(urls,BASE_URL)
                    new_urls = getNewURLS(urls)
                    for new_url in new_urls :
                        if new_url not in FOUND_URLS :
                            FOUND_URLS.append(new_url)
                            print(new_url)
                    if len(new_urls) != 0 :
                        newurlsfound = True                     # to continue spidering
                        writeURLStoFile(FOUND_URLS)             # to save already discovered urls
                    DONE_URLS.append(url)
            

        writeURLStoFile(FOUND_URLS) # Writting urls into a file
        print('')
        print(f'[+] --> File written to {FILE_PATH}')
        print('')

#Write URLS into a file
def writeURLStoFile(url_list):
    file = open(FILE_PATH,'w+',encoding='utf-8')
    temp = url_list
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
    r = requests.get(url,headers=rheaders,verify=False)
    #print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    result = []
    for link in soup.find_all('a'):
        result.append(link.get('href'))
    for link in soup.find_all('link'):
        result.append(link.get('href'))
    return result


#Delete duplicates in a list 
#(list --> list)
def removeDuplicatesURLS(url_list) :
    result = []
    for link in url_list :
        if link in result :
            pass
        else :
            result.append(link)
    return result

#Build URLS for non url links (#, /path/, ...)
#(list --> list)
def buildURLS(url_list):
    result = []
    for link in url_list :
        if link is None or len(link) == 0 :
            pass
        elif link[0] == "/" :
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
    

