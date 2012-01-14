# encoding: utf-8
from rdfalchemy import *
from rdfalchemy.descriptors import rdfLocale
from rdfalchemy.samples.doap import *
import platform

if platform.system() == 'Java':
    from nose import SkipTest
    raise SkipTest("Skipping, Java - Python unicode conflict")

rdfSubject.db.parse('rdfalchemy/samples/schema/doap.rdf')
p=Project(DOAP.SVNRepository)

Project.ls  = rdfSingle(RDFS.label,cacheName='ls')
Project.lm  = rdfMultiple(RDFS.label,cacheName='lm')
Project.len = rdfLocale(RDFS.label,'en')
Project.les = rdfLocale(RDFS.label,'es')
Project.lfr = rdfLocale(RDFS.label,'fr')

def en_es_test():
    assert p.len == u'Subversion Repository'
    assert p.les == u'Repositorio Subversion'
    assert p.lfr == u'D\xe9p\xf4t Subversion'

# unkown resp
print(repr(p.ls))
print(repr(p.lm))
print(repr(p.len))
print(repr(p.les))
print(repr(p.lfr))

