#!/usr/bin/env python
# encoding: utf-8
"""
foaf.py

Created by Philip Cooper on 2007-11-23.
Copyright (c) 2007 Openvest. All rights reserved.
"""
from rdfalchemy import rdfObject, rdflibSingle, rdflibMultiple
from rdflib import Namespace

FOAF=Namespace("http://xmlns.com/foaf/0.1/" )

class Agent(rdfObject):
    rdf_type = FOAF.Agent
    name = rdflibSingle(FOAF.name)
    mbox = rdflibSingle(FOAF.mbox)
    openid = rdflibSingle(FOAF.openid)    

class Person(Agent):
    rdf_type = FOAF.Person
    first = rdflibSingle(FOAF.firstName,'first')
    given = rdflibSingle(FOAF.givenname,'first')
    last = rdflibSingle(FOAF.surname,'last')
    family = rdflibSingle(FOAF.family_name,'last')
    