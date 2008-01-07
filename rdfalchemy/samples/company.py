
from rdflib import Literal, BNode, Namespace, URIRef

# this has the rdfObject stuff and the Fresnel stuff
from rdfalchemy import *


ov = Namespace("http://owl.openvest.org/2005/10/Portfolio#")
edgarns = Namespace('http://www.sec.gov/Archives/edgar')

class Company(rdfObject):
    rdf_type = ov.Company
    symbol = rdflibSingle(ov.symbol,)
    cik = rdflibSingle(ov.secCik,'cik')
    companyName = rdflibSingle(ov.companyName,'companyName')
    stockDescription = rdflibSingle(ov.stockDescription,'stockDescription')
    stock = rdflibMultiple(ov.hasIssue)
        
                                                                                                                                        

class EdgarFiling(rdfObject):
    rdf_type = edgarns.xbrlFiling
    accessionNumber = rdflibSingle(edgarns.accessionNumber)
    companyName = rdflibSingle(edgarns.companyName)
    filingDate = rdflibSingle(edgarns.filingDate)
    formType = rdflibSingle(edgarns.formType)
                                                                                                                                                                                                                                                                                                                                                                   
