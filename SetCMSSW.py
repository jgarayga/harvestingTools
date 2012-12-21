import os
import subprocess

class SetEnv:

    ''' 
        Class to set up the CMSSW, Crab and UI enviroments.
        Class to install, compile and build the CMSSW_X_Y_Z necessary for the harvesting.
    '''

    def __init__(self):

        self.cmsdir ="/afs/cern.ch/cms"
        #later on, this 'basedir' should be rewrite to the corerct /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting/bin
        self.basedir="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting/iasincru_TEST"


    def SourceFile(self, file):

        '''
            Function to SourceFiles as it would be done via command line
        '''

        if (os.path.isfile(file) == True):
            subprocess.check_call("source "+file,shell=True)
            return 1
        else:
            print("\nFile "+file+" does NOT exist. Exiting!!")
            return 0



    def setUI(self):

        #cms   = self.cmsdir+"/cmsset_default.sh"
        cmsui = self.cmsdir+"/LCG/LCG-2/UI/cms_ui_env.sh"
        crab  = self.cmsdir+"/ccs/wm/scripts/Crab/crab.sh"
        setup = self.cmsdir+"/caf/setup.sh"

        print('Setting up the UI, CRAB, DBS enviroments...')

        self.SourceFile(crab)
        self.SourceFile(cmsui)
        self.SourceFile(setup)

        os.system('export X509_USER_PROXY=$HOME/x509up')
        os.system('\n voms-proxy-info --all\n')

#########################################################################################
#    Next functions check if CMSSW_X_Y_Z  is installed. If it is not, it is installed.
#    After the code is compiled
#########################################################################################

    def IsInstalled(self, thisdir, cmssw):

        '''
            Function that checks if CMSSW_X_Y_Z 'cmssw' is installed in 'thisdir'.
            And if 'CMSSW_X_Y_Z/harvesting_area' exists in 'thisdir'
        '''

        WorkDir = thisdir+"/"+cmssw
        if os.path.exists(WorkDir) and os.path.exists(WorkDir+"/harvesting_area"):
            print(cmssw+" is installed in "+thisdir+"\n")
            return 1
        elif not os.path.isdir(WorkDir):
            print(cmssw+" is not installed in "+thisdir+"\n")
            return 0


    def InstallCMSSW(self, cmssw):

        '''
            Install 'cmssw' CMSSW_X_Y_Z release.
            At the end, the working directory is the 'basedir'
        '''

        os.chdir(self.basedir)
        subprocess.check_call("scramv1 project CMSSW "+cmssw, shell=True)
        os.chdir(self.basedir+"/"+cmssw+'/src')
        subprocess.check_call("eval `scramv1 runtime -sh`", shell=True) ##REMEMBER: alias cmsenv='eval `scramv1 runtime -sh`'
        subprocess.check_call("scramv1 b", shell=True)
        harvesting_area=self.basedir+"/"+cmssw+"/harvesting_area"
        os.makedirs(harvesting_area)
        os.chdir(harvesting_area)
        os.chdir(self.basedir)


    def SetCMSSW(self, cmssw):

        '''
            Set up the necessary SCRAM_ARCH for a certain 'cmssw' CMSSW_X_Y_Z release.
            Install and compile the corresponding 'cmssw' CMSSW_X_Y_Z version in 'basedir'
        '''

        if (int(cmssw[6])<5):
            os.putenv("SCRAM_ARCH", "slc5_amd64_gcc434")
        elif (int(cmssw[6])>=5):
            if (int(cmssw[8])==0):
                os.putenv("SCRAM_ARCH", "slc5_amd64_gcc434")   #for CMSSW_5_0_X
            elif (int(cmssw[8])>0):
                os.putenv("SCRAM_ARCH", "slc5_amd64_gcc462")   #for CMSSW_5_1_X or later

        if not self.IsInstalled(self.basedir, cmssw):
            print("Installing "+cmssw+" in "+self.basedir+"\n")
            self.InstallCMSSW(cmssw)

        os.chdir(self.basedir+"/"+cmssw+"/src")
        subprocess.check_call("eval `scramv1 runtime -sh`", shell=True) ##REMEMBER: alias cmsenv='eval `scramv1 runtime -sh`'
        os.system("scramv1 b")
        os.putenv("VO_CMS_SW_DIR", self.cmsdir+"/sw")
        subprocess.check_call("eval `scramv1 runtime -sh`", shell=True) ##REMEMBER: alias cmsenv='eval `scramv1 runtime -sh`'
        os.chdir(self.basedir+"/"+cmssw+"/harvesting_area")