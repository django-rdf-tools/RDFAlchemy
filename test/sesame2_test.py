from rdfalchemy.sparql.sesame2 import SesameGraph

url = 'http://www.openvest.com:8080/openrdf-sesame/repositories/Portfolio/'
url = 'http://bel-epa.com:8080/openrdf-workbench/repositories/otter/query'

g = SesameGraph(url)

q1 = "select ?s ?p ?o where {?s ?p ?o} limit 10"

responses = {}
x = set(list(g.query(q1,resultMethod='xml')))
try:
	j = set(list(g.query(q1,resultMethod='json')))
except ValueError:
	from nose import SkipTest
	raise SkipTest("It's that JSON problem again")

def sizes_test():
    assert len(x) == len(j)

def eq_jx_test():
    assert j == x

