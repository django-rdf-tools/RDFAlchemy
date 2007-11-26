from rdfalchemy import rdfObject, rdflibSingle, rdflibMultiple
from rdflib import Namespace

DOAP=Namespace("http://usefulinc.com/ns/doap#")
FOAF=Namespace("http://xmlns.com/foaf/0.1/" )


class Project(rdfObject):
    rdf_type = DOAP.Project
    name = rdflibSingle(DOAP.name)
    created = rdflibSingle(DOAP.created)
    homepage = rdflibSingle(DOAP.homepage)
    shortdesc = rdflibMultiple(DOAP.shortdesc)
    releases = rdflibMultiple(DOAP.release)
    maintainer = rdflibSingle(DOAP.maintainer,range_type=FOAF.Person)

if __name__ == '__main__':
    from rdflib import ConjunctiveGraph
    rdfObject.db=ConjunctiveGraph()
    accs_uri="http://doapspace.org/doap/sf/accs.rdf"
    rdfObject.db.load(accs_uri)

    p = Doap.ClassInstances().next()
    print "Name is %s" % p.name
    print "created on %s" % p.created
    
    releases = p.releases
    releases[0][DOAP.revision]
    
    for release in p.releases:
        print "%s released on %s" % (release[DOAP.revision],release[DOAP.created])
    
    # A Place to gather more doap records
    pypirss="http://pypi.python.org/pypi?%3Aaction=rss"
