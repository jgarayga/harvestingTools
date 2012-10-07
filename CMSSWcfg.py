class cmsswCFG:
    
    ''' Class to create CMSSW config file using cmsDriver.py command '''

    def __init__(self):
        self.cmsDriverString= ""
        self.string         = ""
    
    def reference_histograms(self, dataset):
    
        '''
            Add 'reference histogram' option to cmsDriver.py customisations dependeing of data type
        '''
        
        string = ""
        if dataset.type == "data":
             string += "process.dqmSaver.referenceHandling = \\\"all\\\""

        elif dataset.type == "mc":
            string += "print \\\"Not using reference histograms\\\" \\n"
            string += "process.dqmSaver.referenceHandling = \\\"skip\\\" "
        
        return string
    
    def addCorrectHarvOptions(self, dataset):
        
        '''
            Customizations to be done for a correct Harvesting process
        '''
        
        string = " --customise_commands=\"process.GlobalTag.connect = \\\"frontier://FrontierProd/CMS_COND_31X_GLOBALTAG\\\"\\n"
        if dataset.type == "data":
            string += " process.dqmSaver.saveByLumiSection = 1 \\n"
        string += " process.dqmSaver.workflow = \\\"" + dataset.name+"\\\" \\n "
        string +=  self.reference_histograms(dataset)+ "\""
        
        return string

        
    def create_cmsDriver_query(self, datasets, SR_filepath):

         '''
            Create a cmsDriver.py command line string. Later run it via shell.
            For a Special Request, please give the path to the file containing the commands as 2nd parameter to this function.
         '''

         CMSSWcfgFileName = "harvesting_"+datasets.name.replace("/","",1).replace("/","__")+".py" 
        
         if cmp(SR_filepath, ""):
            
            cmsDriverString = create_cmsDriver_query_for_SpecialRequest(datasets, SR_filepath)
            
         elif not cmp(SR_filepath, ""):#standard cmsDriver command created for a DS
            cmsDriverString="cmsDriver.py harvesting --no_exec --filein=dummy_value --magField=38T"
            cmsDriverString+=" --conditions "+datasets.tag
            
            if datasets.type == "data":
                cmsDriverString+=" --data --step=HARVESTING:dqmHarvesting"
            elif datasets.type == "mc":
                cmsDriverString+=" --mc  --step=HARVESTING:validationprodHarvesting"
            else:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                print "Warning: "+datasets.name+" isn't DATA nor MC."
                print "Check that!!"
                print "Meanwhile EXITING!!"
                return 0
            
         cmsDriverString+=" --python_filename="+CMSSWcfgFileName
         
         #this command has to be added in any case
         cmsDriverString+=self.addCorrectHarvOptions(datasets)
         
         return cmsDriverString
         
     def create_cmsDriver_query_for_SpecialRequest(self, dataset, SR_filepath):
         
         '''
         Read the special request cmsDriver command from file for Speacial Requests
         '''
         
         try:
             cmsDriverCmnd = open(SR_filepath, "r") ## use expections handlers to avoid opening an unexisting file!!
         except IOError, error:
                print "You want to use a SpecialRequest but it doesn't exist the file"
                print SR_filepath.__str__()
                print "you want to use"
                return False
         cmsDriverString=cmsDriverCmnd.read()
         cmsDriverCmnd.close()
         
         print "\n\n Special Request\n\n"
         print cmsDriverString.__str__()
         cmsDriverString.replace("\\n", " ").replace("\\", "")
         return cmsDriverString