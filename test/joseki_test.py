from rdfalchemy.sparql import SPARQLGraph

url = 'http://localhost:2020/books'
g = SPARQLGraph(url)

q1 = "select ?s ?p ?o where {?s ?p ?o}"

responses = {}
x = set(list(g.query(q1,resultMethod='xml')))
j = set(list(g.query(q1,resultMethod='json')))

print len(x)

def sizes_test():
    assert len(x) == len(j)


def eq_jx_test():
    assert j == x
