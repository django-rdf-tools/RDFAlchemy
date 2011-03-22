from rdfalchemy.sparql.sesame2 import SesameGraph

url = 'http://www.openvest.com:8080/openrdf-sesame/repositories/Portfolio/'
url = 'http://localhost:8080/openrdf-sesame/repositories/murray'
url = 'http://bel-epa.com:8080/openrdf-sesame/repositories/journals'

g = SesameGraph(url)

q1 = "select ?s ?p ?o where {?s ?p ?o} limit 100"

responses = {}
x = set(list(g.query(q1,resultMethod='xml')))
j = set(list(g.query(q1,resultMethod='json')))
b = set(list(g.query(q1,resultMethod='brtr')))

print len(x)

def sizes_test():
    assert len(b) == len(x) == len(j)

def eq_bx_test():
    assert b == x

def eq_bj_test():
    assert b == j

def eq_jx_test():
    assert j == x

