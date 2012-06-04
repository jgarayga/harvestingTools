import json
from DatasetInfo import *

class Bookkeeping:

    filename="harvesting_bookkeeping.txt"
    json={}

    def __init__(self, *args, **kwargs):
        
        if "file" in kwargs:
            self.filename=kwargs["file"]

    def load(self, *args, **kwargs):
        
        if "file" in kwargs:
            self.filename=kwargs["file"]
        
        file=open(self.filename,"r")
        JSON=file.readlines()[0].split('\n')[0]
        file.close()
        print JSON
        self.json=json.loads(str(JSON))
               
    def compare(self, DSs):
        for ds in DSs:
            if ds.name in self.json:
                for run in ds.runs:
                    if run in self.json[ds.name]:
                        ds.runs.remove(run)
                    else:
                        if (ds.castor_check(run)):
                            ds.runs.remove( run)
                            self.append( ds.name, run)
            else:
                for run in ds.runs:
                    if (ds.castor_check(run)):
                        ds.runs.remove( run)
                        self.append( ds.name, run)
            if (len(ds.runs)==0):
                DSs.remove(ds)

    def append(self, ds, runs):
        if not (ds in self.json):
            self.json[ds]=[]
        if isinstance( runs, list ):
            for run in runs:
                if isinstance( run, int ):
                    self.json[ds].append(run)
        elif isinstance( runs, int ):
            self.json[ds].append(runs)
        else:
            print "error" ## add raise err

    def dump(self):
        print self.json
        file=open(self.filename,"w")
        file.write( ( json.dumps( self.json)))
        file.close()
