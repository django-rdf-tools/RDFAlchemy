from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple
from rdfalchemy.orm import mapper
from rdflib import Namespace


DOAP=Namespace("http://usefulinc.com/ns/doap#")
FOAF=Namespace("http://xmlns.com/foaf/0.1/" )


class Project(rdfSubject):
    rdf_type = DOAP.Project
    name       = rdfSingle(DOAP.name)
    created    = rdfSingle(DOAP.created)
    homepage   = rdfSingle(DOAP.homepage)
    shortdesc  = rdfMultiple(DOAP.shortdesc)
    releases   = rdfMultiple(DOAP.release)
    language   = rdfSingle(DOAP['programming-language']) # because of the hyphen, we can't use DOAP.programming-language
    maintainer = rdfSingle(DOAP.maintainer,range_type=FOAF.Person)

class Release(rdfSubject):
    rdf_type = DOAP.Version
    name = rdfSingle(DOAP.revision)
    created = rdfSingle(DOAP.created)
    shortdesc = rdfMultiple(DOAP.shortdesc)
    fileUri = rdfSingle(DOAP['file-release'])

mapper(Project,Release)

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
