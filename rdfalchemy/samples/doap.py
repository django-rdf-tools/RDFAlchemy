from rdfalchemy import rdfSubject, rdflibSingle, rdflibMultiple
from rdflib import Namespace

DOAP=Namespace("http://usefulinc.com/ns/doap#")
FOAF=Namespace("http://xmlns.com/foaf/0.1/" )


class Project(rdfSubject):
    rdf_type = DOAP.Project
    name = rdflibSingle(DOAP.name)
    created = rdflibSingle(DOAP.created)
    homepage = rdflibSingle(DOAP.homepage)
    shortdesc = rdflibMultiple(DOAP.shortdesc)
    releases = rdflibMultiple(DOAP.release)
    language = rdflibSingle(DOAP['programming-language']) # the hyphen means we can't use DOAP.programming-language
    maintainer = rdflibSingle(DOAP.maintainer,range_type=FOAF.Person)

if __name__ == '__main__':
    from rdflib import ConjunctiveGraph
    rdfSubject.db=ConjunctiveGraph()
    accs_uri="http://doapspace.org/doap/sf/accs.rdf"
    rdfSubject.db.load(accs_uri)

    p = Project.ClassInstances().next()
    print "Name is %s" % p.name
    print "created on %s" % p.created
    
    releases = p.releases
    releases[0][DOAP.revision]
    
    for release in p.releases:
        print "%s released on %s" % (release[DOAP.revision],release[DOAP.created])
    
    # A Place to gather more doap records
    pypirss="http://pypi.python.org/pypi?%3Aaction=rss"
