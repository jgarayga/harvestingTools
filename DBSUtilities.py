from DBSXMLHandler import *

class DBS:

    args = {} 
    query=""
    keys=[]
    APIoutput=None
    results={}

    def __init__(self, *args, **kwargs):
        
	self.args["url"] = "http://cmsdbsprod.cern.ch/cms_dbs_prod_global/servlet/DBSServlet"
        if "url" in kwargs:
            self.args["url"]=kwargs["url"]

        self.initializer(url=self.args["url"])
    ## End of __init__

    def initializer(self, *args, **kwargs):
        self.args={}
        self.args["url"]=kwargs["url"]
        self.api = DbsApi(self.args)
    ## End of initializer
    
    def send_query(self, query):
        self.query=query
        try:
            self.APIoutput = self.api.executeQuery(query)	
        except DBSAPI.dbsApiException.DbsApiException, ex:
            print "Caught DBS exception:",ex.getErrorMessage()
        self.keys=self.keys_from_query(query)
        return self.XMLHandler()
    ## End of send_query

    def keys_from_query(self,query):
        keys=self.query.split(",")
        keys[0]=keys[0].replace("find","")
        keys[-1]=keys[-1][:keys[-1].find("where")]
        for i in range(len(keys)):
            keys[i]=keys[i].strip()
        return keys
    ## End of keys_from_query
    
    def XMLHandler(self, *args, **kwargs):

        if "keys" in kwargs:
            self.keys=kwargs["keys"]
            
        if "APIoutput" in kwargs:
            self.APIoutput=kwargs["APIoutput"]

        self.results = {}
        for key in self.keys:
            handler = DBSXMLHandler([key])
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            
            # Parse
            try:
                xml.sax.parseString(self.APIoutput, handler)
            except SAXParseException:
                print "ERROR: Could not parse DBS server output"
            self.results[key]=handler.results.values()[0]
        return self.results
    ## End of XMLHandler
