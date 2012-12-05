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
        size=0
        try:
            size=rfstat_item(path, "Size")
        except BaseException, error:
            print "\n ERORR in DatasetInfo.py"
            print "Couldn't check the existence of the file in EOS for "+path
            print "Exiting!. With error: "+error.__str__()
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

        return str(path)
