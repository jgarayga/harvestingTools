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
import subprocess

from subprocess import PIPE
from DBSUtilities import *
from Bookkeeping import *
from rfstat import *  ##not used at all, can be removed??
from CMSHarvesterHelpFormatter import *
from SetCMSSW import *
from CMSSWcfg import *
from CRAB import *

###########################################################################

## Based on previous code cmsHarvester.py by Jeroen Hegeman (jeroen.hegeman@cern.ch)

__version__ = "0.0"
__author__ = "Francesco Costanza (francesco.costanza@desy.de) and Ivan Asin (ivan.asin.cruz@desy.de)"

##Maybe in the cron job can be set up to run an specific shell type (bash) executing: bash. This way we will be
## safe against possible shell incompatibilities

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
	    
        self.dataset_name="/*/*/DQM"
        #self.dataset_name="/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12-PU_S7_START50_V15-v1/DQM"#"/*/*/DQM"
        
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
        
        #self.castor_basepath="/eos/cms/store/group/comm_dqm/harvesting_output"

    def parse_cmd_line_options(self):

        # Set up the command line parser. Note that we fix up the help
        # formatter so that we can add some text pointing people to
        # the Twiki etc.
        parser = optparse.OptionParser(version="%s %s" % \
                                      ("%prog", self.version),
                                      formatter=CMSHarvesterHelpFormatter())
        self.option_parser = parser

        # Option to specify the name (or a regexp) of the dataset(s) to be used.
        parser.add_option("", "--dataset",
                           help="Name (or regexp) of dataset(s) to process",
                           action="callback",
                           callback=self.option_handler_input_spec,
                           type="string",
                           metavar="DATASET")

        # Option to specify the name (or a regexp) of the dataset(s)
        #to be ignored.
        #parser.add_option("", "--dataset-ignore",
                          #help="Name (or regexp) of dataset(s) to ignore",
                          #action="callback",
                          #callback=self.option_handler_input_spec,
                          #type="string",
                          #metavar="DATASET-IGNORE")

        #Option to specify the name (or a regexp) of the run(s)
        #to be used.
        #parser.add_option("", "--runs",
                          #help="Run number(s) to process",
                          #action="callback",
                          #callback=self.option_handler_input_spec,
                          #type="string",
                          #metavar="RUNS")

        #Option to specify the name (or a regexp) of the run(s)
        #to be ignored.
        #parser.add_option("", "--runs-ignore",
                          #help="Run number(s) to ignore",
                          #action="callback",
                          #callback=self.option_handler_input_spec,
                          #type="string",
                          #metavar="RUNS-IGNORE")

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
                          help="path to a file containing the special request cmsDriver command. It must be placed in the same directory as 'harvester.py'. Please format the file so there is a SINGLE line",
                          action="store",
                          dest="SR_filepath",
                          default="",
                          type="str")
        # absolute path to the directory where the CMSSW release and where the CRAB jobs will be submitted from.
        parser.add_option("", "--CMSSWbasedir",
                          help="path to dir containing all CMSSW releases",
                          action="store",
                          dest="CMSSWbasedir",
                          default="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting",
                          type="str")
        #absolute path to the directory in EOS where the output ROOT files will be stored and
        #from where (later) the Upload will take the ROOT files from
        parser.add_option("", "--EOSbasedir",
                          help="absolute path to the storage directory in EOS",
                          action="store",
                          dest="EOSbasedir",
                          default="/eos/cms/store/group/comm_dqm/harvesting_output",
                          type="str")

        parser.set_defaults()
        (self.options, self.args) = parser.parse_args(self.cmd_line_opts)

        self.site=self.options.site
        self.SR_filepath=self.options.SR_filepath
        self.CMSSWbasedir=self.options.CMSSWbasedir
        self.castor_basepath=self.options.EOSbasedir

    #def dataset_veto(self):


    def option_handler_input_spec(self, option, opt_str, value, parser):
        self.dataset_name=value

    def option_handler_create_date(self, option, opt_str, value, parser):
        self.create_date=value

    def lock(self):
        if os.path.exists(sys.path[0]+'/harvester.lock'):
            return 1
        f = open(sys.path[0]+'/harvester.lock', 'w')
        f.close()

    def cleaning(self):
        print "Start cleaning "+self.CMSSWbasedir+"/CMSSW*/harvesting_area/*"
        subprocess.check_call("rm -rf "+self.CMSSWbasedir+"/CMSSW*/harvesting_area/*", shell=True)
        print "Cleaning done."

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
                query = "find file.numevents where dataset="+dic["dataset"][i]+" and file.numevents >0 and site="+self.site
                ds.nevents=self.dbs_api.send_query(query)["file.numevents"][0]

            DS.append(ds)
        return DS
    ## End of ds_list

    def bookkeep(self, DS):
        self.bookkeeping=Bookkeeping()
        self.bookkeeping.load()
        self.bookkeeping.compare(DS)
        self.bookkeeping.dump()

    def order_by_release(self, DSs):
        
        '''
            Order the datasets needed to harvest as a function of the CMSSW_X_Y_Z release
        '''
        orderedMap={}
        for ds in DSs:
            if not(ds.release in orderedMap.keys()):
                orderedMap[ds.release]=[]
            orderedMap[ds.release].append(ds)
        return orderedMap


    def mc_run_check(self, ds):

        '''
            Checks if the MC sample contains 1 or more runs.
            MC samples CAN only have 1 run, if nr. runs>1 something is wrong
        '''

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

        try:
            subprocess.check_call(cmsDriverQuery, shell=True);
        except BaseException, error:
            print "\nERROR! (in harvester.py/create_cmssw_cfg)"
            print error.__str__()

    def create_script(self, release):

        tmp = []

        tmp.append("#!/bin/zsh")
        tmp.append("")
        tmp.append("cd "+self.CMSSWbasedir+"/"+release+"/src")
        tmp.append("")
        tmp.append("eval `scramv1 runtime -sh`")
        tmp.append("cd "+self.CMSSWbasedir+"/"+release+"/harvesting_area")
        tmp.append("")
	tmp.append("source /afs/cern.ch/cms/ccs/wm/scripts/Crab/crab.sh")
	tmp.append("")
        tmp.append("crab -create -submit -cfg crab.cfg")

        script = "\n".join(tmp)

        return script


    def run(self):

        '''
            Main entry point of the CMS harvester.
        '''

        self.parse_cmd_line_options()

        CurrentWorkingDir = os.getcwd()

        starttime=datetime.datetime.today()
        print "\n\n==================================================================================="
        print starttime.strftime("Start Harvesting script at %Y-%m-%d %H:%M")
        print "===================================================================================\n\n"
        
        if self.lock():
            print "Harvester still running."
            print "Remove the lock file 'harvester.lock' if the job crashed"
            return
        self.cleaning()

        self.dbs_api=DBS()
        query = "find dataset, release, dataset.tag, datatype where dataset="+self.dataset_name
        query = query+" and file.numevents >0 and site="+self.site+" and dataset.createdate > "+self.create_date
        print "\nSending DBS query\n"
        print query
        dic=self.dbs_api.send_query(query)
        print "\nDBS query obtained\n"

        DSs=self.DS_list(dic)
        
        self.bookkeep(DSs)
        orderedDSs=self.order_by_release(DSs)
        self.setcmssw = SetEnv()
        self.setcmssw.basedir = self.CMSSWbasedir
        self.cmsswcfg = CMSSWcfg(str(CurrentWorkingDir))
        self.crab_cfg=crab_config(self.site, self.castor_basepath)
        for release in orderedDSs.keys():
            self.setcmssw.SetCMSSW(release)
            self.cmsswcfg.CMSSWbasedir = self.CMSSWbasedir+"/"+release

            script = open("script.sh","w")
            script.write(self.create_script(release))
            script.close()
            subprocess.check_call("chmod +x script.sh",shell=True)

            for ds in orderedDSs[release]:
                self.create_cmssw_cfg(self.cmsswcfg.create_cmsDriver_query(ds, self.SR_filepath))
                print "\nCMSSW cfg file created\n"
                self.crab_cfg.set_DS(ds)
                print "\nCRAB cfg file created\n"
                for run in ds.runs:
                    crab_file = open("crab.cfg","w")
                    crab_file.write(self.crab_cfg.create_crab_config(run))
                    crab_file.close()
                    print "CRAB creating and submitting for "+str(ds.name)+" and run "+str(run)
                    subprocess.check_call(self.CMSSWbasedir+"/"+release+"/harvesting_area/script.sh", stdout=sys.stdout, stderr=sys.stderr, shell=True);
        os.remove(sys.path[0]+"/harvester.lock")

        endtime=datetime.datetime.today()
        print "\n\n==================================================================================="
        print endtime.strftime("End Harvesting script at %Y-%m-%d %H:%M")
        print "===================================================================================\n\n"

###########################################################################
## Main entry point.
###########################################################################

if __name__ == "__main__":
    
    "Main entry point for harvesting."
    
    CMSHarvester().run()

    # Done.

###########################################################################
