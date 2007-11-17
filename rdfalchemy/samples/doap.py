from rdfalchemy import rdfObject, rdflibSingle, rdflibMultiple
from rdflib import Namespace

doap=Namespace("http://usefulinc.com/ns/doap#")


class Doap(rdfObject):
    rdf_type = doap.Project
    name = rdflibSingle(doap.name)
    created = rdflibSingle(doap.created)
    homepage = rdflibSingle(doap.homepage)
    shortdesc = rdflibMultiple(doap.shortdesc)
    releases = rdflibMultiple(doap.release)
    maintainer = rdflibSingle(doap.maintainer)

if __name__ == '__main__':
    from rdflib import ConjunctiveGraph
    rdfObject.db=ConjunctiveGraph()
    accs_uri="http://doapspace.org/doap/sf/accs.rdf"
    rdfObject.db.load(accs_uri)

    p = Doap.ClassInstances().next()
    print "Name is %s" % p.name
    print "created on %s" % p.created
    
    releases = p.releases
    releases[0][doap.revision]
    
    for release in p.releases:
        print "%s released on %s" % (release[doap.revision],release[doap.created])
    
    # A Place to gather more doap records
    pypirss="http://pypi.python.org/pypi?%3Aaction=rss"
