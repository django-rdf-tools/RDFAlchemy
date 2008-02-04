#!/usr/bin/env python
# encoding: utf-8
"""
foaf.py

Created by Philip Cooper on 2007-11-23.
Copyright (c) 2007 Openvest. All rights reserved.
"""
from rdfalchemy import rdfSubject, rdflibSingle, rdflibMultiple
from rdflib import Namespace

FOAF=Namespace("http://xmlns.com/foaf/0.1/" )

class Agent(rdfSubject):
    rdf_type = FOAF.Agent
    name = rdflibSingle(FOAF.name)
    mbox = rdflibSingle(FOAF.mbox)
    openid = rdflibSingle(FOAF.openid)    

class Person(Agent):
    rdf_type = FOAF.Person
    first = rdflibSingle(FOAF.firstName,'first')
    last = rdflibSingle(FOAF.surname,'last')
    givenname = rdflibSingle(FOAF.givenname,'first')
    surname = rdflibSingle(FOAF.surname,'last')
    