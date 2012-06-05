import os

class SetEnv:

     ''' Class to set up the CMSSW, Crab and UI enviroments.
         Class to install, compile and build the CMSSW+DQM/Integration package necessary for the harvesting.
     '''
     
     
     def __init__(self):
         
	 self.cmsdir ="/afs/cern.ch/cms"
         #later on this 'basedir' should be rewrite to the corerct /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting/bin
	 self.basedir="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting/iasincru_TEST"
     
     
     def SourceFile(self, file):
     
         ''' Function to SourceFiles as it would be done via command line'''
     
         if (os.path.isfile(file) == True):
            os.system("source "+file)
	    return 1
         else:
	    print("\nFile "+file+" does NOT exist. Exiting!!")
	    return 0



     def setUI(self):
     
         cms   = self.cmsdir+"/cmsset_default.sh"
         crab  = self.cmsdir+"/ccs/wm/scripts/Crab/crab.sh"
	 cmsui = self.cmsdir+"/LCG/LCG-2/UI/cms_ui_env.sh"
#Ask Francesco if is necessary to setup DBS.
#	 dbssh   = self.cmsdir+'/sw/${SCRAM_ARCH}/cms/dbs-client/DBS_2_0_9_patch9_4-cms/lib/setup.sh"
         setup = self.cmsdir+"/caf/setup.sh"
	 
	 print('Setting up the UI, CRAB, DBS enviroments...')
	 
         self.SourceFile(cms)
	 #print("Sourced: "+cms)
	 self.SourceFile(crab)
	 #print("Sourced: "+crab)
	 self.SourceFile(cmsui) 
	 #print("Sourced: "+cmsui)
	 self.SourceFile(setup)
	 #print("Sourced: "+setup)
	 os.system('export X509_USER_PROXY=$HOME/x509up')
	 #print('Exported X509')
	 os.system('\n voms-proxy-info --all\n')


#########################################################################################
#
#    Next functions check if CMSSW_X_Y_Z  is installed, if DQM/Integration package
#    is installed. If it is not the installation is done. If it is, the code is compiled
#
#########################################################################################
	 
     def IsInstalled(self, thisdir, cmssw):
         
	 ''' Function that checks if CMSSW_X_Y_Z and the package DQM/Integration/ are installed in 'thisdir'.'''

	 if os.path.exists(thisdir+'/'+cmssw):
	    print(cmssw+" is installed in "+thisdir+"\n")
	    if os.path.exists(thisdir+'/'+cmssw+'/src/DQM/Integration'):
	        print("DQM/Integration is installed in "+thisdir+"\n")
	        return 1
	    elif not os.path.isdir(thisdir+"/"+cmssw+"/src/DQM/Integration"):
		print ("DQM/Integration is not installed in "+thisdir+"/"+cmssw+"/src/DQM/Integration\n")
		return 0
	 elif not os.path.isdir(thisdir+'/'+cmssw):
	    print(cmssw+" is not installed in "+thisdir+"\n")
	    return 0


	 
     def InstallCMSSW(self, cmssw):
         
	 ''' Install CMSSW_X_Y_Z release.
	     At the end, the working directory is the 'basedir' '''
	 
	 os.chdir(self.basedir)
         os.system("scramv1 project CMSSW "+cmssw)
	 os.chdir(self.basedir+"/"+cmssw+'/src')
	 os.system("eval `scramv1 runtime -sh`") ##REMEMBER: alias cmsenv='eval `scramv1 runtime -sh`'
	 os.system("cvs co DQM/Integration/scripts/harvesting_tools")
	 os.system("cvs co -r 1.303 Configuration/PyReleaseValidation")
	 os.system("scramv1 b")
	 harvesting_area=self.basedir+"/"+cmssw+"/src/harvesting_area"
	 os.makedirs(harvesting_area)
         os.chdir(harvesting_area)
	 #Maybe later on this two steps are outdated and must be replaced by new symlinks to new files
	 # Right now I keep them for consistency with old Harvesting code
	 os.symlink(self.basedir+"/"+cmssw+"/src/DQM/Integration/scripts/harvesting_tools/cmsHarvester.py", "cmsHarvester.py")
	 os.symlink(self.basedir+"/"+cmssw+"/src/DQM/Integration/scripts/harvesting_tools/check_harvesting.pl", "check_harvesting.pl")
	 os.chdir(self.basedir)




     def SetCMSSW(self, cmssw):
     
         ''' This function sets up the SCRAM_ARCH for a certain CMSSW_X_Y_Z release.
         Downloads the necessaary package from CVS and compiles it.
         '''
     
         if (int(cmssw[6])<5):
	    os.putenv("SCRAM_ARCH", "slc5_amd64_gcc434")
         elif (int(cmssw[6])>=5):
	    os.putenv("SCRAM_ARCH", "slc5_amd64_gcc462")

         if (self.IsInstalled(self.basedir, cmssw) == False):
	    print("Installing "+cmssw+" in "+self.basedir+"\n")
	    self.InstallCMSSW(cmssw)
	 
	 os.chdir(self.basedir+"/"+cmssw+"/src")
	 os.system("eval `scramv1 runtime -sh`")  ##REMEMBER: alias cmsenv='eval `scramv1 runtime -sh`'
	 os.system("scramv1 b")
	 os.system("export VO_CMS_SW_DIR="+self.cmsdir+"/sw")
	 os.system("eval `scramv1 runtime -sh` ")
	 os.chdir(self.basedir+"/"+cmssw+"/src/harvesting_area")

