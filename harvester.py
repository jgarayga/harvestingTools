
#!/usr/bin/env python

import os
import sys
import commands
import re
import logging
import optparse
import datetime
import copy
from inspect import getargspec
from random import choice

from DBSUtilities import *
from Bookkeeping import *
from rfstat import *
from CMSHarvesterHelpFormatter import *
from SetCMSSW import *
from Configuration.PyReleaseValidation.cmsDriverOptions import OptionsFromCommand
from CMSSWcfg import *

###########################################################################

## Based on previous code cmsHarvester.py by Jeroen Hegeman (jeroen.hegeman@cern.ch)

__version__ = "0.0"
__author__ = "Francesco Costanza (francesco.costanza@desy.de)"

twiki_url = "https://twiki.cern.ch/twiki/bin/view/CMS/CmsHarvester"

###########################################################################


class CMSHarvester(object):
    """Class to perform CMS harvesting.
	
    More documentation `obviously' to follow.
    
    """

    def __init__(self):

	self.version=__version__
	
	cmd_line_opts = sys.argv[1:]
	#print cmd_line_opts
	self.cmd_line_opts = cmd_line_opts

        #default value command-line options
	    
        self.dataset_name="/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12-PU_S7_START50_V15-v1/DQM"#"/*/*/DQM"
        #self.dataset_name="/DYToEE_M_20_TuneZ2star_8TeV_pythia6/Summer12-PU_S7_START50_V15-v1/DQM"#"/*/*/DQM"
        
        today=datetime.datetime.today()
        delta=datetime.timedelta(30)
        self.create_date=(today-delta).strftime("%Y-%m-%d")

        self.dbs_api=0

        self.dataset_ignore_patterns=["RelVal",
                                      "HLT",
                                      "BUNNIES",
                                      "StreamExpress",
                                      "preprod"]
        
        self.bookkeeping_file="harvesting_bookkeeping.txt"
        
        self.castor_basepath="/castor/cern.ch/cms/store/temp/dqm/offline/harvesting_output/TEST"

    def parse_cmd_line_options(self):

        # Set up the command line parser. Note that we fix up the help
	# formatter so that we can add some text pointing people to
	# the Twiki etc.
	parser = optparse.OptionParser(version="%s %s" % \
				       ("%prog", self.version),
				       formatter=CMSHarvesterHelpFormatter())
	self.option_parser = parser

	# Option to specify the name (or a regexp) of the dataset(s)
	# to be used.
	parser.add_option("", "--dataset",
			  help="Name (or regexp) of dataset(s) to process",
			  action="callback",
			  callback=self.option_handler_input_spec,
			  type="string",
			  metavar="DATASET")
	
        '''       # Option to specify the name (or a regexp) of the dataset(s)
        # to be ignored.
        parser.add_option("", "--dataset-ignore",
                          help="Name (or regexp) of dataset(s) to ignore",
                          action="callback",
                          callback=self.option_handler_input_spec,
                          type="string",
                          metavar="DATASET-IGNORE")

        # Option to specify the name (or a regexp) of the run(s)
        # to be used.
        parser.add_option("", "--runs",
                          help="Run number(s) to process",
                          action="callback",
                          callback=self.option_handler_input_spec,
                          type="string",
                          metavar="RUNS")                   
	
        # Option to specify the name (or a regexp) of the run(s)
        # to be ignored.
        parser.add_option("", "--runs-ignore",
                          help="Run number(s) to ignore",
                          action="callback",
                          callback=self.option_handler_input_spec,
                          type="string",
                          metavar="RUNS-IGNORE")'''

        # Option to specify the creation date of dataset of the dataset(s)
	# to be used.
	parser.add_option("", "--create_date",
			  help="creation date of dataset(s) to process YYYY-MM-DD",
                          action="callback",
			  callback=self.option_handler_create_date,
                          type="string" )

        # Option to specify the site to be used.
	parser.add_option("", "--site",
			  help="site where the harvesting has to be run",
                          action="store",
			  dest="site",
			  default="srm-eoscms.cern.ch",
                          type="string" )

        # Options to specify special request input file.
        # In case any special request is requested, save the cmsDriver.py command in a file and give the path
        # as input to the harvseter.py
        parser.add_option("", "--special_request",
                          help="path to a file containing the special request cmsDriver command. Please format the file so there is a SINGLE line",
                          action="store",
                          dest="SR_filepath",
                          default="",
                          type="str")
                          
	parser.set_defaults()
	(self.options, self.args) = parser.parse_args(self.cmd_line_opts)
        
        self.site=self.options.site
        self.SR_filepath=self.options.SR_filepath
	
    #def dataset_veto(self):
        

    def option_handler_input_spec(self, option, opt_str, value, parser):
        self.dataset_name=value

    def option_handler_create_date(self, option, opt_str, value, parser):
        self.create_date=value

    def dbs_skim( self, dic):
        for i in range(len(dic["dataset"])-1, -1, -1):
            for ignore_pattern in self.dataset_ignore_patterns:
                if (dic["dataset"][i].find(ignore_pattern) > 0):
                    dic["dataset"].pop(i)
                    dic["datatype"].pop(i)
                    dic["release"].pop(i)
                    dic["dataset.tag"].pop(i)
                    continue             
        return dic
    ## End of dbs_skim
    
    def DS_list( self, dic):
        dic=self.dbs_skim(dic)
        DS=[]
        for i in range(len(dic["dataset"])):
            ds=DatasetInfo()
            ds.name=dic["dataset"][i]
            ds.type=dic["datatype"][i]
            ds.release=dic["release"][i]
            ds.tag=dic["dataset.tag"][i]
            ds.runs=[]
            ds.castor_basepath=self.castor_basepath
            if (ds.type == "data"):
                query = "find run where dataset="+dic["dataset"][i]+" and file.numevents >0 and site="+self.site
                for run in self.dbs_api.send_query(query)["run"]:
                    ds.runs.append(int(run))
            else:
                ds.runs=[1]
                
            DS.append(ds)
        return DS
    ## End of ds_list

    def bookkeep(self, DS):
        self.bookkeeping=Bookkeeping()
        self.bookkeeping.load()
        self.bookkeeping.compare(DS)
        self.bookkeeping.dump()
    
    def mc_run_check(self, ds):
        query = "find run where dataset="+ds.name+" and file.numevents >0"
        dbs_result = dbs_query(self.dbs_api,query)
        keys=["run"]
        dic=dbs_XMLhandler(dbs_result,keys)
        if (len(dic["run"]) > 1):
            return False
        else:
            ds.run=dic["run"][0]
            return True

    def create_cmssw_cfg(self, cmsDriverQuery):
        
        '''
           Create the CMSSW configuration file using cmsDriver.py command.
           Takes as input the cmsDriver.py command, including the possible customizations.
        '''
        
        print cmsDriverQuery
        subprocess.check_call(cmsDriverQuery, shell=True);
        

    def run(self):
        "Main entry point of the CMS harvester."
        
        self.parse_cmd_line_options()
	
	self.setcmssw = SetEnv()

        self.dbs_api=DBS()
        query = "find dataset, release, dataset.tag, datatype where dataset="+self.dataset_name
        query = query+" and file.numevents >0 and site="+self.site+" and dataset.createdate > "+self.create_date
        print query
        dic=self.dbs_api.send_query(query)

        DSs=self.DS_list(dic)
        
        self.bookkeep(DSs)
        self.cmsswcfg = cmsswCFG()
        
        for DataSetRelease in range(len(DSs)):
            self.setcmssw.SetCMSSW(DataSetRelease)
            for DataName in range(len(DSs)):
                self.create_cmssw_cfg(self.cmsswcfg.create_cmsDriver_query(DSs[DataName], self.SR_filepath))
                #for RunNumber in range(len(DSs)):
                #add here the crab CFG creator and submitter!!
                #self.create_crab_cfg(DS)
	
	#self.create_batch_script(DS)
        #self.execute()
    
###########################################################################
## Main entry point.
###########################################################################

if __name__ == "__main__":
    "Main entry point for harvesting."

    CMSHarvester().run()

    # Done.

###########################################################################
