from rdfalchemy.sesame2 import SesameGraph

url = 'http://www.openvest.com:8080/sesame/repositories/Portfolio/'
g = SesameGraph(url)

q1 = "select ?s ?p ?o where {?s ?p ?o}"

responses = {}
b = set(list(g.query(q1,resultMethod='brtr')))
x = set(list(g.query(q1,resultMethod='xml')))
j = set(list(g.query(q1,resultMethod='json')))

print len(x)

def sizes_test():
    assert len(b) == len(x) == len(j)

def eq_bx_test():
    assert b == x

def eq_bj_test():
    assert b == j

def eq_jx_test():
    assert j == x
