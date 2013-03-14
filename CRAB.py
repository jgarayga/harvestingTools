from DatasetInfo import *

class crab_config():

    '''
    Class to create the crab cfg files.
    '''

    def __init__(self):
        self.site="srm-eoscms.cern.ch"
        self.EOSdir="/eos/cms/store/group/comm_dqm/harvesting_output"

    def __init__(self,site,EOSdir):
        self.site=site
        self.EOSdir=EOSdir

    def set_site(self,site):
        self.site=site

    def set_DS(self,DS):
        self.DS=DS

    def create_crab_config(self,DS,run):
        self.DS=DS
        return self.create_crab_config(run)

    def create_crab_config(self,run):

        """
        Create a CRAB configuration for a given job.
        """

        tmp = []

        ## CMSSW
        ##-------
        tmp.append("[CMSSW]")
        #tmp.append("# This reveals data hosted on T1 sites,")
        #tmp.append("# which is normally hidden by CRAB.")
        tmp.append("show_prod=1")
        tmp.append("output_file=DQM_V0001_R"+str(run).zfill(9)+self.DS.name.replace("/","__")+".root")
        if self.DS.type.lower() == "data":
            tmp.append("total_number_of_lumis=-1")
        else:
            tmp.append("total_number_of_events="+self.DS.nevents)
        #tmp.append("# Force everything to run in one job.")
        tmp.append("no_block_boundary=1")
        tmp.append("number_of_jobs=1")
        tmp.append("pset=harvesting_"+self.DS.name.replace("/","",1).replace("/","__")+".py")
        tmp.append("runselection="+str(run))
        tmp.append("datasetpath="+self.DS.name)
        tmp.append("")

        ## GRID
        ##------
        tmp.append("[GRID]")
        tmp.append("se_white_list="+self.site)
        #tmp.append("# This removes the default blacklisting of T1 sites.")
        tmp.append("remove_default_blacklist=1")
        tmp.append("virtual_organization=cms")
        tmp.append("rb=CERN")
        tmp.append("")

        ## USER
        ##------EOS
        tmp.append("[USER]")
        tmp.append("ui_working_dir="+ self.DS.name.replace("/","",1).replace("/","__")+"_R"+str(run))
        tmp.append("copy_data=1")
        tmp.append("check_user_remote_dir=0")
        tmp.append("storage_element=T2_CH_CERN")
        tmp.append("caf_lfn="+self.EOSdir[8:])
        tmp.append("user_remote_dir="+self.DS.create_path(run).replace(self.EOSdir, ""))
        tmp.append("")

        ## CRAB
        ##------
        tmp.append("[CRAB]")
        tmp.append("cfg=crab.cfg")
        tmp.append("scheduler=caf")
        tmp.append("jobtype=cmssw")
        tmp.append("")

        crab_config = "\n".join(tmp)

        # End of create_crab_config.
        return crab_config

##########
