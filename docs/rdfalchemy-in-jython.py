# Jena in Jython
from  com.hp.hpl.jena.rdf.model import *
from  com.hp.hpl.jena.vocabulary import *

personURI    = "http://somewhere/JohnSmith"
givenName    = "John"
familyName   = "Smith"
fullName     = givenName + " " + familyName
# create an empty model
model = ModelFactory.createDefaultModel()

# create the resource
#   and add the properties cascading style
johnSmith = model.createResource(personURI)
johnSmith.addProperty(VCARD.FN, fullName
        ).addProperty(VCARD.N, model.createResource(
                ).addProperty(VCARD.Given, givenName
                        ).addProperty(VCARD.Family, familyName))
        
# list the statements in the graph
iter_ = model.listStatements()
        
# print out the predicate, subject and object of each statement
while iter_.hasNext():
    stmt = iter_.nextStatement()    # get next statement
    sub  = stmt.getSubject()        # get the subject
    pred = stmt.getPredicate()      # get the predicate
    obj  = stmt.getObject()         # get the object
    
    print(sub.toString())
    print(" " + pred.toString() + " ")
    if isinstance(obj, Resource):
        print(obj.toString())
    else:
        # object is a literal
        print(" \"" + obj.toString() + "\"")
    print(" .")
