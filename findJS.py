import requests
import re

#JS_FILE = open("myscript.js","r",encoding="utf-8")
#JS_CONTENT = JS_FILE.read()
#JS_FILE.close()

def findPattern(pattern,content):
    compiled = re.compile(r''+pattern+'')
    urls = compiled.findall(content)
    urls = list(set(urls))
    return urls

def findURLinJS(url):
    JS_URL = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'})
    JS_CONTENT = JS_URL.text

    FOUND = {}

    #:"http://example.com"
    FOUND['pattern1'] = findPattern('\:\s*"(http[^"]+)"',JS_CONTENT)

    #:'http://example.com'
    FOUND['pattern2'] = findPattern("\:\s*'(http[^']+)'",JS_CONTENT)

    #="http://example.com"
    FOUND['pattern3'] = findPattern('\=\s*"(http[^"]+)"',JS_CONTENT)

    #='http://example.com'
    FOUND['pattern4'] = findPattern("\=\s*'(http[^']+)'",JS_CONTENT)

    #+"http://example.com"
    FOUND['pattern5'] = findPattern('\+\s*"(http[^"]+)"',JS_CONTENT)

    #+'http://example.com'
    FOUND['pattern6'] = findPattern("\+\s*'(http[^']+)'",JS_CONTENT)

    #:"/api/event"
    FOUND['pattern7'] = findPattern('\:"(\/[^"]+)"',JS_CONTENT)

    #:'/api/event'
    FOUND['pattern8'] = findPattern("\:'(\/[^']+)'",JS_CONTENT)

    #="/api/event"
    FOUND['pattern9'] = findPattern('\="(\/[^"]+)"',JS_CONTENT)

    #='/api/event'
    FOUND['pattern10'] = findPattern("\='(\/[^']+)'",JS_CONTENT)

    #+"/api/event"
    FOUND['pattern11'] = findPattern('\+"(\/[^"]+)"',JS_CONTENT)

    #+'/api/event'
    FOUND['pattern12'] = findPattern("\+'(\/[^']+)'",JS_CONTENT)

    print(FOUND)

    sub_result = []
    for key, value in FOUND.items():
        sub_result = sub_result + value

    RESULT = [x for x in sub_result if x != '' and x != ' ']
    print(RESULT)

