from rdfalchemy import Literal,Namespace
from datetime import datetime
from decimal import Decimal
try:
    from rdflib.term import bind as bindLiteral
except ImportError:
    from rdflib.Literal import bind as bindLiteral  

import logging
log = logging.getLogger()
if not log.handlers:
    log.addHandler(logging.StreamHandler())
#log.setLevel(10)


XSD = Namespace(u'http://www.w3.org/2001/XMLSchema#')

def just_for_coverage_test():
    from rdfalchemy.Literal import _strToDateTime
    x = _strToDateTime('2008-02-09T10:46:29')
    assert type(x) == datetime

def toPython_decimal_test():
    """docstring for toPython"""
    # test a normal iso
    d = Literal('.1', datatype=XSD.decimal).toPython()
    assert isinstance(d, Decimal)
    payments = [Literal(s,datatype=XSD.decimal) for s in '.1 .1 .1 -.3'.split()]
    assert sum([payment.toPython() for payment in payments]) == 0


def toPython_datetime_test():
    """docstring for toPython"""
    # test a normal iso
    d = Literal('2008-02-09T10:46:29', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    d = Literal('2008-02-09T10:46:29Z', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    d = Literal('2008-02-09T10:46:29-07:00', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    
    d = Literal('2008-02-09T10:46:29.1', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    d = Literal('2008-02-09T10:46:29.123', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    d = Literal('2008-02-09T10:46:29.123456', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    # test a normal iso with fractional seconds 
    
    d = Literal('2008-02-09 10:46:29', datatype=XSD.dateTime).toPython()
    assert isinstance(d, datetime)
    # test an "almost" iso string

    