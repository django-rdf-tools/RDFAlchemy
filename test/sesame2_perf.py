from datetime import datetime
from rdfalchemy.sparql.sesame2 import SesameGraph

import logging 

logging.getLogger('rdfalchemy.sparql').setLevel(logging.DEBUG)
logging.getLogger('rdfalchemy.sesame2').setLevel(logging.DEBUG)
logging.getLogger('root').addHandler(logging.StreamHandler())

url1 = 'http://www.openvest.com:8080/sesame/repositories/Portfolio/'
url2 = 'http://www.openvest.com:8080/sesame/repositories/Test/'

q1 = "select ?s ?p ?o where {?s ?p ?o} limit 1000"
q2 = "select ?o where {?s ?p ?o} limit 10000"


def tester(method,small, all):
    start = datetime.now()
    i=0
    for x in  g.query(q,resultMethod=method):
        i = i + 1
        if (i % small) == 0:
            print "c %s %s" % (i,datetime.now()-start)
        if (i % all) == 0:
            print "f %s %s" % (i,datetime.now()-start)
            return

g = SesameGraph(url1)
q = q1
print "testing\n  url: %s\n  query: %s\n" % (url1,q)
print "\n  method: %s" % ('brtr')
tester('brtr',100,1000) 

print "\n  method: %s" % ('xml')
tester('xml',100,1000) 

print "\n  method: %s" % ('json')
tester('json',100,1000) 

g = SesameGraph(url2)
q = q2
print "testing\n  url: %s\n  query: %s\n" % (url2,q)
print "\n  method: %s" % ('brtr')
tester('brtr',1000,5000) 

print "\n  method: %s" % ('xml')
tester('xml',1000,5000) 

print "\n  method: %s" % ('json')
tester('json',1000,5000) 

