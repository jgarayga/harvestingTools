import commands
from rfstat import *

class DatasetInfo:
    def __init__(self):
        self.name=""
        self.type=""
        self.release=""
        self.tag=""
        self.runs=[]
        self.nevents=""
        self.castor_basepath=""
        
    def castor_check(self, run):
        path=self.create_path(run)
        try:
            size=rfstat_item(path, "Size") #rfstat_item: rfstat module function to get all properties of a certain CASTOR file
        except:
            print "Couldn't check the existence of the file in CASTOR because: server not responding, wrong path, ..."
            print "Exiting."
            return False
        if (size > 0):
            if (int(size)>0):
                return True
            else:
                return False
        else:
            return False
        
    def create_path(self, run):
        path=self.castor_basepath
        if (self.type == "mc"):
            path+="/mc/mc/"
        if (self.type == "data"):
            path+="/data/dqmoffline/"
        path+=self.release[6:]+"/"
        path+=self.name[1:].replace("/","__")+"/"
        path+="run_"+str(run)+"/"
        path+="nevents/"
        path+=self.name[1:].replace("/","__")+"_"+str(run).zfill(9)+"_site_01/"
        cmd="nsls "+path
        status, output= commands.getstatusoutput( cmd )
        if (status == 0):
            path+=output
        return path
