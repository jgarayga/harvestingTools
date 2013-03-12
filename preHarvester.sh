#!/bin/zsh

## This small script is needed to be able to run the harvester.
## 1st: CRAB to be able to submit crab jobs
source /afs/cern.ch/cms/ccs/wm/scripts/Crab/crab.sh ;

## 2nd: CMSSW to be able to run python, and different DBS and json modules
## unfortunatelly one CMSSW version must be selected, and must be installed in the indicated path
## To be able to run the harvester, please be aware that ONLY the 
cwd=$PWD ;
cd /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/harvesting ;
scram project CMSSW CMSSW_5_3_8 ;
cd CMSSW_5_3_8/src ;
eval `scramv1 runtime -sh` ;
cd $cwd ;
export X509_USER_PROXY=$HOME/x509up ;