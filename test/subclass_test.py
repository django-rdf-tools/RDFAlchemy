#!/usr/bin/env python
# encoding: utf-8
"""
subclass.py

Created by Philip Cooper on 2008-05-14.
Copyright (c) 2008 Openvest. All rights reserved.
"""

from rdfalchemy import rdfSubject, Namespace
from rdfalchemy.rdfsSubject import rdfsSubject

NS = Namespace('http://example.com/project123/')

class A(rdfSubject):
    rdf_type = NS.A

a1 = A()
a2 = A()

class B(rdfSubject):
    rdf_type = NS.B

b1 = B()
b2 = B()

class C(B):
    rdf_type = NS.C

c1 = C()

class D(C):
    rdf_type = NS.D

d1 = D()
d2 = D()
d3 = D()


class E(A,C):
    rdf_type = NS.D


def subclass_testLen1():
    assert len(list(A.ClassInstances())) == 2
    assert len(list(B.ClassInstances())) == 2    
    
def subclass_testLen2():
    assert len(list(C.ClassInstances())) == 1
    assert len(list(D.ClassInstances())) == 3    
    
class As(rdfsSubject):
    rdf_type = NS.As

a1 = As()
a2 = As()

class Bs(rdfsSubject):
    rdf_type = NS.Bs

b1 = Bs()
b2 = Bs()

class Cs(Bs):
    rdf_type = NS.Cs

c1 = Cs()

class Ds(Cs):
    rdf_type = NS.Ds

d1 = Ds()
d2 = Ds()
d3 = Ds()

def ssubclass_testLen1():
    assert len(list(As.ClassInstances())) == 2, len(list(As.ClassInstances()))
    assert len(list(Bs.ClassInstances())) == 6, len(list(Bs.ClassInstances()))    
    
def ssubclass_testLen2():
    assert len(list(Cs.ClassInstances())) == 4, len(list(Cs.ClassInstances()))
    assert len(list(Ds.ClassInstances())) == 3, len(list(Ds.ClassInstances()))    

