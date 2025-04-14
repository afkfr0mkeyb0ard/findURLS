import requests
import warnings
import sys
from urllib.parse import urlparse
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import re
import time
import os
import validators

def exitAndHelp():
    print('[-] Please enter a valid URL and check your parameters.')
    print('Usage: python3 findUrls.py [-s] [-v] [-d 1] https://yourwebsite/')
    print('       -s       Enable Spider mode. Will repeat the scan for every new URL found')
    print('       -v       Enable Verbose mode. To display all found URLs')
    print('       -d       Define the delay between two requests (seconds)')
    sys.exit()

for arg in sys.argv:
    if arg.find("http:") != -1 or arg.find("https:") != -1:
        BASE_URL = arg

SPIDER = '-s' in sys.argv
VERBOSE = '-v' in sys.argv
DELAY = '-d' in sys.argv

try:
    url_check = urlparse(BASE_URL)
    if DELAY :
        DELAY_time = int(sys.argv[sys.argv.index('-d') + 1])
except Exception as e:
    exitAndHelp()

if url_check.scheme == '' or url_check.netloc == '' :
    exitAndHelp()

if SPIDER:
    print("[i] Using spidering mode (-s)")
if VERBOSE:
    print("[i] Using verbose mode (-v)")
if DELAY:
    print("[i] Using delay (" + str(DELAY_time) + " second)")

print(f'[+] Scanning url: {BASE_URL}')
print('')
print('-----------------------------------------------------------')
DOMAIN = url_check.hostname
FOUND_URLS = []
DONE_URLS = []
FOUND_POTENTIAL_PATHS = []
FOUND_IPS = []

CURRENT_DIR = os.getcwd()
timestamp = str(time.time()).split(".")[0]
OUTPUT_FOLDER = CURRENT_DIR + '/' + DOMAIN
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
OUTPUT_FILE_URLS = OUTPUT_FOLDER + '/urls_' + timestamp + '_' + DOMAIN + '.txt'
OUTPUT_FILE_PATHS = OUTPUT_FOLDER + '/potential_paths_' + timestamp + '_' + DOMAIN + '.txt'
OUTPUT_FILE_IPS = OUTPUT_FOLDER + '/ips_' + timestamp + '_' + DOMAIN + '.txt'

def main():
    global FOUND_URLS,DONE_URLS,FOUND_IPS,FOUND_POTENTIAL_PATHS

    content = makeRequest(BASE_URL)
    urls = getURLS(content)
    urls = removeDuplicatesList(urls)
    urls = buildURLS(urls,BASE_URL)
    urls = excludeOtherDomainsURLS(urls,BASE_URL)

    FOUND_URLS = FOUND_URLS + urls

    writeURLStoFile(FOUND_URLS)
    writePathstoFile(FOUND_POTENTIAL_PATHS)
    
    DONE_URLS.append(BASE_URL)
    
    if len(FOUND_URLS) == 0 :
        print('[-] No new URL found, try another URL')
        sys.exit()
    else:
        print('[+] New URL found: ' + str(len(FOUND_URLS)))
        if VERBOSE:
            printAllElementsOfList(FOUND_URLS)

    ips = getIPS(content)
    if len(ips) != 0:
        for ip in ips:
            print('[?] Potential IP found: ' + str(ip))
            FOUND_IPS.append(str(ip))
        writeIPStoFile(FOUND_IPS)

    newurlsfound = True
    if SPIDER :                                             #if Spider mode activated
        while newurlsfound :                                #while we find new URLS
            newurlsfound = False
            for url in FOUND_URLS :
                if DELAY :
                    time.sleep(DELAY_time)
                url = url.split('#')[0]
                url_path = urlparse(url).path
                if url not in DONE_URLS \
                and (url_path.split(".")[-1] != 'png' \
                and url_path.split(".")[-1] != 'css' \
                and url_path.split(".")[-1] != 'svg' \
                and url_path.split(".")[-1] != 'jpg' \
                and url_path.split(".")[-1] != 'jpeg' \
                and url_path.split(".")[-1] != 'ico') \
                and url.find(":javascript:") == -1 :
                    print('')
                    print(f'[+] Scanning url: {url}')
                    content = makeRequest(url)
                    urls = getURLS(content)
                    urls = removeDuplicatesList(urls)
                    urls = buildURLS(urls,url)
                    urls = excludeOtherDomainsURLS(urls,BASE_URL)
                    new_urls = getNewURLS(urls)
                    
                    if len(new_urls) != 0 :
                        newurlsfound = True                       # to continue spidering
                        for new_url in new_urls:
                            FOUND_URLS.append(new_url)
                        writeURLStoFile(FOUND_URLS)             # to save already discovered urls
                        print('[+] New URL found: ' + str(len(new_urls)))
                        if VERBOSE:
                            printAllElementsOfList(new_urls)
                    else:
                        print('[-] No new URL found, trying next one.')
                    DONE_URLS.append(url)
                    
                    #Writing found IPS to file
                    ips = getIPS(content)
                    if len(ips) != 0:
                        for ip in ips:
                            print('[?] Potential IP found: ' + str(ip))
                            FOUND_IPS.append(str(ip))
                        writeIPStoFile(FOUND_IPS)

        writeURLStoFile(FOUND_URLS) # Writting urls into a file
        writePathstoFile(FOUND_POTENTIAL_PATHS) # Writting other potential paths into a file
        print('')
        print(f'[+] File written to {OUTPUT_FILE_URLS}')
        print('')

#Make an HTTP request and returns the page content
#(string -> string)
def makeRequest(url):
    rheaders = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url,headers=rheaders,verify=False)
        response = r.text
        return response
    except Exception as e:
        print("[-] Error while requesting " + url)
        print(str(e))
        return None

#Print all elements of a list (one per line)
#(list -> none)
def printAllElementsOfList(table):
    temp = table.copy()
    temp = list(set(temp))
    temp.sort()
    for el in temp:
        print(el)

#Write IPS into a file
#(dic -> none)
def writeIPStoFile(ips_list):
    file = open(OUTPUT_FILE_IPS,'w+',encoding='utf-8')
    temp = ips_list.copy()
    temp = list(set(temp))
    temp.sort()
    for ip in temp :
        file.write(ip + '\n')
    file.close()

#Write potential paths into a file
#(list -> none)
def writePathstoFile(path_list):
    file = open(OUTPUT_FILE_PATHS,'w+',encoding='utf-8')
    temp = path_list.copy()
    temp = list(set(temp))
    temp.sort()
    for path in temp :
        file.write(path + '\n')
    file.close()

#Write URLS into a file
#(list -> none)
def writeURLStoFile(url_list):
    file = open(OUTPUT_FILE_URLS,'w+',encoding='utf-8')
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
def getURLS(content):
    result = []

    ### Search in HTML content
    for link in findPattern(r'href\=\"([^"]+)"',content):  #href="http://example.com"
        result.append(link)

    for link in findPattern(r"href\=\'([^']+)'",content):  #href='http://example.com'
        result.append(link)

    for link in findPattern(r'src\=\"([^"]+)"',content):  #src="http://example.com"
        result.append(link)

    for link in findPattern(r"src\=\'([^']+)'",content):  #src='http://example.com'
        result.append(link)

    for link in findPattern(r'action\=\"([^"]+)"',content):  #action="http://example.com"
        result.append(link)

    for link in findPattern(r"action\=\'([^']+)'",content):  #action='http://example.com'
        result.append(link)

    for link in findPattern(r"codebase\=\'([^']+)'",content):  #codebase='http://example.com'
        result.append(link)

    for link in findPattern(r'codebase\=\"([^"]+)"',content):  #codebase="http://example.com"
        result.append(link)

    for link in findPattern(r"cite\=\'([^']+)'",content):  #cite='http://example.com'
        result.append(link)

    for link in findPattern(r'cite\=\"([^"]+)"',content):  #cite="http://example.com"
        result.append(link)

    for link in findPattern(r"background\=\'([^']+)'",content):  #background='http://example.com'
        result.append(link)

    for link in findPattern(r'background\=\"([^"]+)"',content):  #background="http://example.com"
        result.append(link)

    for link in findPattern(r"longdesc\=\'([^']+)'",content):  #longdesc='http://example.com'
        result.append(link)

    for link in findPattern(r'longdesc\=\"([^"]+)"',content):  #longdesc="http://example.com"
        result.append(link)

    for link in findPattern(r"profile\=\'([^']+)'",content):  #profile='http://example.com'
        result.append(link)

    for link in findPattern(r'profile\=\"([^"]+)"',content):  #profile="http://example.com"
        result.append(link)

    for link in findPattern(r"classid\=\'([^']+)'",content):  #classid='http://example.com'
        result.append(link)

    for link in findPattern(r'classid\=\"([^"]+)"',content):  #classid="http://example.com"
        result.append(link)

    for link in findPattern(r"data\=\'([^']+)'",content):  #data='http://example.com'
        result.append(link)

    for link in findPattern(r'data\=\"([^"]+)"',content):  #data="http://example.com"
        result.append(link)

    for link in findPattern(r"formaction\=\'([^']+)'",content):  #formaction='http://example.com'
        result.append(link)

    for link in findPattern(r'formaction\=\"([^"]+)"',content):  #formaction="http://example.com"
        result.append(link)

    for link in findPattern(r"icon\=\'([^']+)'",content):  #icon='http://example.com'
        result.append(link)

    for link in findPattern(r'icon\=\"([^"]+)"',content):  #icon="http://example.com"
        result.append(link)

    for link in findPattern(r"manifest\=\'([^']+)'",content):  #manifest='http://example.com'
        result.append(link)

    for link in findPattern(r'manifest\=\"([^"]+)"',content):  #manifest="http://example.com"
        result.append(link)

    for link in findPattern(r"poster\=\'([^']+)'",content):  #poster='http://example.com'
        result.append(link)

    for link in findPattern(r'poster\=\"([^"]+)"',content):  #poster="http://example.com"
        result.append(link)

    for link in findPattern(r"archive\=\'([^']+)'",content):  #archive='http://example.com'
        result.append(link)

    for link in findPattern(r'archive\=\"([^"]+)"',content):  #archive="http://example.com"
        result.append(link)

    for link in findPattern(r'content\=\"(https?\:[^"]+)"',content):  #content="http://example.com"
        result.append(link)

    for link in findPattern(r"content\=\'(https?\:[^']+)'",content):  #content='http://example.com'
        result.append(link)
    
    for link in findPattern(r"<loc>(https?[^<]+)<\/loc>",content):  #<loc>https://example.com</loc>
        result.append(link)

    ### Search in JS content

    for link in findPattern(r'\:\s*"(https?\:[^"]+)"',content): #:"http://example.com"
        result.append(link)

    for link in findPattern(r"\:\s*'(https?\:[^']+)'",content): #:'http://example.com'
        result.append(link)

    for link in findPattern(r'\=\s*"(https?\:[^"]+)"',content): #="http://example.com"
        result.append(link)

    for link in findPattern(r"\=\s*'(https?\:[^']+)'",content): #='http://example.com'
        result.append(link)

    for link in findPattern(r'\+\s*"(https?\:[^"]+)"',content): #+"http://example.com"
        result.append(link)

    for link in findPattern(r"\+\s*'(https?\:[^']+)'",content): #+'http://example.com'
        result.append(link)

    for link in findPattern(r'\:\s*"(\/[^"]+)"',content):      #:"/api/event"
        result.append(link)

    for link in findPattern(r"\:\s*'(\/[^']+)'",content):      #:'/api/event'
        result.append(link)

    for link in findPattern(r'\=\s*"(\/[^"]+)"',content):    #="/api/event"
        result.append(link)

    for link in findPattern(r"\=\s*'(\/[^']+)'",content):    #='/api/event'
        result.append(link)

    for link in findPattern(r'\+\s*"(\/[^"]+)"',content):    #+"/api/event"
        result.append(link)

    for link in findPattern(r"\+\s*'(\/[^']+)'",content):    #+'/api/event'
        result.append(link)

    for link in findPattern(r'\(\"(https?\:[^"]+)\"',content):    #("http://example.com"
        result.append(link)

    for link in findPattern(r"\(\'(https?\:[^']+)\'",content):    #('http://example.com'
        result.append(link)

    for link in findPattern(r'\s+\"(https?\:[^"]+)\"',content):    # "http://example.com"
        result.append(link)

    for link in findPattern(r"\s+\'(https?\:[^']+)\'",content):    # 'http://example.com'
        result.append(link)

    for link in findPattern(r'\"(\/[^\s\;\"]+)\"',content):    # "/users/me"
        result.append(link)

    for link in findPattern(r"\'(\/[^\s\;\']+)\'",content):    # '/users/me'
        result.append(link)

    return result

#Return a list of the IP found in a page (parsed from the HTTP response)
#(str --> list)
def getIPS(content):
    result = []
    for ip in findPattern(r"[^\d\.]([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})[^\d\.]",content):
        if validators.ip_address.ipv4(ip):
            result.append(ip)
    return result

#Delete duplicates in a list 
#(list --> list)
def removeDuplicatesList(url_list):
    result = url_list.copy()
    return list(set(result))

#Build an URL from urlparse elements
#(string,string,string,string,string,string -> string)
def buildURL(scheme,netloc,path='',params='',query='',fragment=''):
    url = scheme + "://" + netloc
    if path != '' :
        url = url + path
    if params != '' :
        url = url + ';' + params
    if query != '' :
        url = url + '?' + query
    if fragment != '' :
        url = url + '#' + fragment
    return url

#Build URLS for non url links (#, /path/, ...)
#(list,string --> list)
def buildURLS(url_list,current_url):
    global FOUND_POTENTIAL_PATHS
    result = []
    for link in url_list :
        link = link.replace("&amp;","&")
        built_scheme = urlparse(link).scheme if urlparse(link).scheme != '' else urlparse(current_url).scheme
        built_netloc = urlparse(link).netloc if urlparse(link).netloc != '' else urlparse(current_url).netloc
        built_path = urlparse(link).path
        built_params = urlparse(link).params
        built_query = urlparse(link).query.replace(' ','%20')
        built_fragment = urlparse(link).fragment
        if link is None or len(link) == 0 or link == " ":
            pass
        elif len(link) == 1 :
            if link == '/' :
                new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path='/')
            else:
                new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path='/' + link)
            if validators.url(new_url) :
                result.append(new_url)
            else:
                print("[-] Invalid URL found: " + new_url)
        elif link[:2] == '//' and link[:3] != '///' :
            new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment)
            if validators.url(new_url) :
                result.append(new_url)
            else:
                print("[-] Invalid URL found: " + new_url)
        elif link[:2] == './' :
            new_path = os.path.dirname(urlparse(current_url).path) + link.replace('./','/',count=1)
            new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path=new_path,params=built_params,query=built_query,fragment=built_fragment)
            if validators.url(new_url) :
                result.append(new_url)
            else:
                print("[-] Invalid URL found: " + new_url)
        elif link[0] == '/' :
            split_link = link.split('/')
            if urlparse(current_url).hostname in split_link[1] :
                print("[-] Invalid link found: " + link)
            else:
                new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment)
                if validators.url(new_url) :
                    result.append(new_url)
                else:
                    print("[?] Potential path found " + link)
                    if link not in FOUND_POTENTIAL_PATHS:
                        FOUND_POTENTIAL_PATHS.append(link)
        elif link[0] == "#" or link[0] == "?" or link[0] == "@" or link[0] == ":" :
            new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment)
            if validators.url(new_url) :
                result.append(new_url)
            else:
                print("[-] Invalid URL found: " + new_url)
        elif link[:4] == 'http' :
            new_link = cleanJSUrl(link)
            built_scheme = urlparse(new_link).scheme
            built_netloc = urlparse(new_link).netloc
            built_path = urlparse(new_link).path
            built_params = urlparse(new_link).params
            built_query = urlparse(new_link).query
            built_fragment = urlparse(new_link).fragment
            new_url = buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment)
            if validators.url(new_url) :
                result.append(new_url)
            else:
                print("[-] Invalid URL found: " + link)
        elif link[:11] == "javascript:" :
            new_url = current_url + ':' + link
            result.append(new_url)
        elif link[:10] == "data:image" :
            pass
        elif validators.url(link) :
            result.append(link)
        elif validators.url(buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment)) :
            result.append(buildURL(scheme=built_scheme,netloc=built_netloc,path=built_path,params=built_params,query=built_query,fragment=built_fragment))
        elif validators.url(buildURL(scheme=built_scheme,netloc=built_netloc,path='/'+built_path,params=built_params,query=built_query,fragment=built_fragment)) :
            result.append(buildURL(scheme=built_scheme,netloc=built_netloc,path='/'+built_path,params=built_params,query=built_query,fragment=built_fragment))
        else:
            print("[-] Invalid URL found: " + link)
    return result

#Return a clean URL ('http://myexample.com' + '/file' -> http://myexample.com/file)
#(string ---> string)
def cleanJSUrl(url):
    result = url
    find1 = re.search(r"\'\s*\+\s*\'",result)
    if find1 : #check if link found in JS: 'https://' + 'mydomain.com?example=1'
        result = re.sub(r"\'\s*\+\s*\'",'',result)
    find2 = re.search(r'\"\s*\+\s*\"',result)
    if find2 : #check if link found in JS: "https://" + "mydomain.com?example=1"
        result = re.sub(r'\"\s*\+\s*\"',result,'',result)
    return result

#Return a list of all URLs that match the pattern
#(string,string ---> list)
def findPattern(pattern,content):
    compiled = re.compile(r''+pattern+'')
    urls = compiled.findall(content)
    urls = list(set(urls))
    return urls

#Exlude URLS from other domains
#(list --> list)
def excludeOtherDomainsURLS(url_list,base_url):
    result = []
    for link in url_list :
        if urlparse(link).hostname == DOMAIN :
            result.append(link)
    return result

if __name__ == '__main__' :
    main()
    print('-----------------------------------------------------------')
    print('')
