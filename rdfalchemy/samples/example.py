from rdfAlchemy import rdfObject, rdflibSingle, rdflibMultiple
from rdflib import ConjunctiveGraph, Namespace, Literal

OV = Namespace('http://owl.openvest.org/2005/10/Portfolio#')
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

rdfObject.db = ConjunctiveGraph()
rdfObject.db.load('./example.n3', format='n3')

class Company(rdfObject):
    owlType = OV.Company
    symbol = rdflibSingle(OV.symbol,'symbol')
    cik = rdflibSingle(OV.secCik,'cik')
    companyName = rdflibSingle(OV.companyName)
    address = rdflibSingle(VCARD.adr)


# Above here would typically go in a model.py file and be imported
##########################################################################
# Below here goes in the file with business logic agnostic of persistance

c = Company.get_by(symbol='IBM')
## this will enable us to see that the reads are cached
import logging 
log=logging.getLogger('rdfAlchemy')
## comment out to quite debug messages
log.setLevel(logging.DEBUG)

## list Companies
for c in Company.ClassInstances():
    print "%s has an SEC symbol of %s" % (c.companyName, c.cik)
print ''

c = Company.get_by(symbol = 'IBM')

## Add a descriptor on the fly
Company.stockDescription = rdflibSingle(OV.stockDescription,'stockDescription')

print "%s: %s"%(c.companyName,c.stockDescription)
print " same as"
print "%s: %s"%(c[OV.companyName],c[OV.stockDescription])

print "## CHECK to see if multiple reads cause database reads"
print "%s: %s"%(c.companyName,c.stockDescription)
print "%s: %s"%(c.companyName,c.stockDescription)

## add another descriptor on the fly
Company.industry = rdflibSingle(OV.yindustry,'industry')

## add an attribute (from the database)
c = Company.get_by(symbol = 'Java')
c.industry = 'Computer stuff'

## delete an attribute (from the database)
c = Company.get_by(symbol = 'IBM')
del c.industry

# write out the new n3 file to see the changes 
c.db.serialize('example-out.n3',format='n3')
