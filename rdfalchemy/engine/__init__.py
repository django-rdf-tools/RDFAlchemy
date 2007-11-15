from rdflib import ConjunctiveGraph
import os
import re
import urllib

def create_engine(url=''):
    """Takes a url string and returns an open
    rdflib ConjunctiveGraph
    e.g.:
       create_engine('mysql://myname@localhost/rdflibdb')
       create_engine('sleepycat://~/working/rdf_db')
       create_engine('zodb:///var/rdflib/Data.fs')
       create_engine('zodb://localhost:8672')
    for zodb:
       the key in the Zope database is hardcoded as 'rdflib'
       urls inding with .fs indicate FileStorage
       otherwise ClientStoreage is assumed which requires
       a ZEO Server to be running"""
    if url=='' or url.startswith('IOMemory'):
        db = ConjunctiveGraph('IOMemory')
    elif url.lower().startswith('mysql://'):
        schema,opts = _parse_rfc1738_args(url)
        openstr= 'db=%(database)s,host=%(host)s,user=%(username)s'%opts
        db = ConjunctiveGraph('MySQL')
        db.open(openstr)
    elif url.lower().startswith('sleepycat://'):
        openstr = os.path.abspath(os.path.expanduser(url[12:]))
        db = ConjunctiveGraph('Sleepycat')
        db.open(openstr)
    elif url.lower().startswith('zodb://'):
        import ZODB
        import transaction
        db = ConjunctiveGraph('ZODB')
        if url.endswith('.fs'):
            from ZODB.FileStorage import FileStorage
            openstr = os.path.abspath(os.path.expanduser(url[12:]))
            fs=FileStorage(openstr)
        else:
            from ZEO.ClientStorage import ClientStorage
            schema,opts = _parse_rfc1738_args(url)
            fs=ClientStorage((opts['host'],int(opts['port'])))
        # get the Zope Database
        zdb=ZODB.DB(fs)
        # open it
        conn=zdb.open()
        #get the root
        root=conn.root()
        # get the Conjunctive Graph
        db=root['rdflib']
    else:
        raise "Could not parse  string '%s'" % url
    return db
    
def _parse_rfc1738_args(name):
    """ parse url str into options
    code orig from sqlalchemy.engine.url """
    pattern = re.compile(r'''
            (\w+)://
            (?:
                ([^:/]*)
                (?::([^/]*))?
            @)?
            (?:
                ([^/:]*)
                (?::([^/]*))?
            )?
            (?:/(.*))?
            '''
            , re.X)

    m = pattern.match(name)
    if m is not None:
        (name, username, password, host, port, database) = m.group(1, 2, 3, 4, 5, 6)
        if database is not None:
            tokens = database.split(r"?", 2)
            database = tokens[0]
            query = (len(tokens) > 1 and dict( cgi.parse_qsl(tokens[1]) ) or None)
            if query is not None:
                query = dict([(k.encode('ascii'), query[k]) for k in query])
        else:
            query = None
        opts = {'username':username,'password':password,'host':host,'port':port,'database':database, 'query':query}
        if opts['password'] is not None:
            opts['password'] = urllib.unquote_plus(opts['password'])
        return (name, opts)
    else:
        raise exceptions.ArgumentError("Could not parse rfc1738 URL from string '%s'" % name)

