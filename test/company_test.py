from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple
from rdflib import ConjunctiveGraph, Namespace, Literal, BNode, URIRef

from StringIO import StringIO

n3data = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix ov:    <http://owl.openvest.org/2005/10/Portfolio#>.
@prefix vcard: <http://www.w3.org/2006/vcard/ns#>.
@prefix iso3166: <http://www.daml.org/2001/09/countries/iso-3166-ont#>.

ov:C_US_SUNW a ov:Company;
     ov:GICS_2 ov:GICS_2_45;
     ov:companyName "Sun Microsystems";
     ov:country iso3166:US;
     ov:nasdaqSymbol "SUNW";
     ov:secCik "0000709519";
     ov:symbol "JAVA". 
     
ov:C_US_IBM a ov:Company;
     ov:GICS_2 ov:GICS_2_45;
     ov:companyName "International Business Machines Corp.";
     ov:country iso3166:US;
     ov:nyseSymbol "IBM";
     ov:secCik "0000051143";
     ov:symbol "IBM";
     ov:yindustry "Diversified Computer Systems";
     ov:ysector "Technology";
     vcard:tel "914-499-1900";
     vcard:url "http://www.ibm.com"^^<http://www.w3.org/2001/XMLSchema#anyURI>; 
     ov:stockDescription "International Business Machines Corporation (IBM) operates as an information technology (IT) company worldwide. It has .....".
"""

OV = Namespace('http://owl.openvest.org/2005/10/Portfolio#')
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

rdfSubject.db = ConjunctiveGraph()
rdfSubject.db.parse(StringIO(n3data), format='n3')

class Company(rdfSubject):
    rdf_type = OV.Company
    symbol = rdfSingle(OV.symbol,'symbol')
    cik = rdfSingle(OV.secCik,'cik')
    companyName = rdfSingle(OV.companyName)
    address = rdfSingle(VCARD.adr)


# Above here would typically go in a model.py file and be imported
##########################################################################
# Below here goes in the file with business logic agnostic of persistance

c = Company.get_by(symbol='IBM')
## this will enable us to see that the reads are cached
import logging 
log=logging.getLogger('rdfAlchemy')
## comment out to quite debug messages
log.setLevel(logging.DEBUG)

def test_1():
    c=Company.get_by(cik="0000051143")
    assert c.symbol == "IBM"

## list Companies
for c in Company.ClassInstances():
    print "%s has an SEC symbol of %s" % (c.companyName, c.cik)
print ''


def test_2():
    ## Add a descriptor on the fly
    Company.stockDescription = rdfSingle(OV.stockDescription,'stockDescription')

    assert  c.companyName == c[OV.companyName]
    
    
## add another descriptor on the fly
Company.industry = rdfSingle(OV.yindustry,'industry')

## add an attribute (from the database)
c = Company.get_by(symbol = 'JAVA')
c.industry = 'Computer stuff'

def test_3():
    ## delete an attribute (from the database)
    c = Company.get_by(symbol = 'IBM')
    assert c.industry == "Diversified Computer Systems"
    del c.industry
    assert c.industry <> "Diversified Computer Systems"
    c = Company.get_by(symbol = 'IBM')
    assert not c.industry
    
def test_creating():
    c1=Company()
    c2=Company(OV.A)
    c3=Company('<http://owl.openvest.org/2005/10/Portfolio#A>')
    c4=Company('_:xyz123')
    #assert c2==c3
    assert c2.resUri == c3.resUri
    assert c4.resUri == BNode('xyz123')

# write out the new n3 file to see the changes 
c.db.serialize('example-out.n3',format='n3')
