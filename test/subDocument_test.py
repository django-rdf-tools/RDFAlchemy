import sys
if sys.version_info[0] > 2:
    from nose import SkipTest
    raise SkipTest('Skipping, _nodetype assumptions violated in Python 3')

from rdfalchemy import Namespace,rdfSingle,rdfMultiple
from rdfalchemy.rdfsSubject import rdfsSubject

DC = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

class Document(rdfsSubject):
    rdf_type = BIBO.Document
    title = rdfSingle(DC['title'])
    alt_titles = rdfMultiple(DC.alt)
    date = rdfSingle(DC.date)
    issued = rdfSingle(DC.issued)
    modified = rdfSingle(DC.modified)
    creators = rdfMultiple(DC.creator)
    authorList = rdfMultiple(BIBO.authorList)
    subjects = rdfMultiple(DC.subject, range_type=SKOS.Concept)

class Book(Document):
    rdf_type = BIBO.Book
    publisher = rdfSingle(DC.publisher,range_type=FOAF.Organization)
    series = rdfSingle(DC.isPartOf, range_type=BIBO.Series)


x = Book(title="Some Title")
y = Document(title="Another Title")

def len_test():
    assert len(list(Document.ClassInstances())) == 2, "wanted 2 ... one book and one document"

for document in Document.ClassInstances():
    print document.title

