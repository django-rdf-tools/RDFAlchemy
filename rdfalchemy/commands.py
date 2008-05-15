from paste.script.command import Command, BadCommand
import sys
from rdfalchemy import rdfSubject, RDF, RDFS
from rdfalchemy.rdfsSubject import rdfsClass

class rdfSubjectCommand(Command):
    """Create an rdfSubject subclass with descriptors from an RDF Schema

    will set the rdf_type
    Descriptors will be created
    
      1.  rdfs:domain and rdfs:range are respected
      2.  rdfSingle is used for properties that are
            * owl:InverseFunctionalProperty
            * owl:FunctionalProperty   
      3.  rdfList or rdfContainer is used if the proper range is set
      4.  rdfMultiple is used for all others
      
    The resulting .py file is ment to be a skeleton for the developers confvience.  
    Do not expect to be able to use the raw results.
    """
    summary = __doc__.splitlines()[0]
    usage = '\npasteR %s\n%s' % (__name__, __doc__)

    min_args = 0
    max_args = 1
    group_name = 'rdfalchemy'
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('-s','--schema',help='file name or url of rdfSchema for this class')
    parser.add_option('-l','--list', action='store_true', help='list valid instances of `owl:Class` in the schema file')    
    parser.add_option('--no-write',
                      action='store_true',
                      help="Don't create the file; just copy to stdout")

    def command(self):
        """Main command to create controller"""
        try:
            if self.options.schema:
                rdfSubject.db.load(self.options.schema)
            else:
                raise NotImplemented('Need to pass in the schema No default yet')
                    
            choices = list(rdfSubject.db.subjects(RDF.type, RDFS.Class))
            choices.sort()
            
            print "qnames that you can import from this schema:"
            for i, n in enumerate(choices):
                print "\t[%i] %s" % (i+1,rdfSubject.db.qname(n))
                
            if self.options.list:
                return
            
            name = self.challenge('Enter (a)ll,(q)uit or the number ot build for','q')
            if name.startswith('q'):
                return
            elif name.startswith('a'):
                raise NotImplemented("(a)ll option not implented yet")
            else:
                try:
                    name = choices[int(name)-1]
                except Exception, e:
                    raise e
                    
            c=rdfsClass("<%s>"%name)
            print c._emit_rdfSubject()
                

            # Setup the controller
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)
