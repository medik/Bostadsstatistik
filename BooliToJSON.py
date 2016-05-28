"""
BooliToJSON, senast ändrad 2016-05-08

Pythonskript som utnyttjar Boolis API för att generera en JSON objekt med
bostadsdata.

Licenserad med 'MIT Licence'. Se bilagan 'LICENCE' för mer information.
"""
from hashlib import sha1

import urllib.request
import urllib.parse
import time
import random
import string
import json

def getSoldObjects(inp):
    userAgent = inp['user_agent']
    callerId = inp['caller_id']
    privateKey = inp['private_key']
    query = inp['query']

    def getJSONBooli(offset, limit):
        timestamp = str(int(time.time()))
        unique = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        toHash = callerId + timestamp + privateKey + unique
        hashstr = sha1(toHash.encode('utf-8')).hexdigest()

        o = urllib.parse.quote(query)

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', userAgent)]

        url = "http://api.booli.se/sold?q=%s&callerId=%s&time=%s&unique=%s&hash=%s&limit=%d&offset=%d" % (o, callerId, timestamp, unique, hashstr, limit, offset)

        resp = opener.open(url)
        data = resp.read()

        ret = json.loads(data.decode('utf-8'))
        return ret

    # HACK

    # OK, nu vill vi iterera igenom alla resultat från booli.
    # För att inte skämma ut oss, så bör vi kontrollera att den gör det den ska
    # först.


    offsetNu = 0
    limit = 500
    ret = getJSONBooli(offsetNu, limit)
    antalSkickade = ret['count']

    if antalSkickade == 0:
        print("Inga resultat.")
        exit()

    print( str(ret['totalCount']) + " från " + query + " kommer att sparas" )
    # input()

    temp = ret['sold']

    while (offsetNu + antalSkickade + 1) < ret['totalCount']:
        if (offsetNu + limit + antalSkickade + 1) > ret['totalCount']:
            print(str(ret['totalCount']) + " av "+  str(ret['totalCount']))
        else:
            print(str(offsetNu + limit) + " av " + str(ret['totalCount']))

        ret = getJSONBooli(offsetNu + antalSkickade + 1, limit)
        temp.extend(ret['sold'])
        offsetNu += limit

        time.sleep(0.5)

    return temp

def retrievePrivateKey(filepath):
    # TODO: Kontroll om denna existerar?
    with open(filepath, 'r') as infile:
        ret = infile.read().strip('\n')
        return ret

def makeStringValid(string):
    # UGLY

    ret = ""
    for s in string:
        if s == " ":
            ret += "-"
        else:
            ret += s
    return ret


def main():
    print("Skriv in din söksträng:")
    query = input().strip('\n')
    fileQuery = makeStringValid(query)
    
    filename = "booli-såld-" + fileQuery + ".json"

    print("Programmet lever! Allt data kommer att sparas till %s" % filename)
    
    privKey = retrievePrivateKey('BooliAPIKey')
    searchParam = {'user_agent' : 'Blubb/1.0',
            'caller_id' : 'Blubb',
            'private_key' : privKey,
            'query' : query }

    soldobjects = getSoldObjects(searchParam)

    with open(filename, 'w') as outfile:
        json.dump(soldobjects, outfile)

if __name__ == "__main__":
    main()
