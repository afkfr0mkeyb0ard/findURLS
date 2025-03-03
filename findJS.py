import requests
import re

#Return a list of all URLs that match the pattern
#(string,string ---> list)
def findPattern(pattern,content):
    compiled = re.compile(r''+pattern+'')
    urls = compiled.findall(content)
    urls = list(set(urls))
    return urls

#Return a list of all URLs found in a content
#(string ---> list)
def findURLinJS(content):
    JS_CONTENT = content

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

    #("http://example.com"
    FOUND['pattern13'] = findPattern('\(\"(https?\:[^"]+)\"',JS_CONTENT)

     #('http://example.com'
    FOUND['pattern14'] = findPattern("\(\'(https?\:[^']+)\'",JS_CONTENT)
    
    sub_result = []
    for key, value in FOUND.items():
        sub_result = sub_result + value

    RESULT = [x for x in sub_result if x != '' and x != ' ']
    return(RESULT)
