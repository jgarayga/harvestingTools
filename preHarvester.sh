#!/bin/zsh

. /afs/cern.ch/cms/cmsset_default.sh ;

## This small script is needed to be able to run the harvester.
## 1st: CRAB to be able to submit crab jobs
source /afs/cern.ch/cms/ccs/wm/scripts/Crab/crab.sh ;

## 2nd: export DBS libraries
export PYTHONPATH=/afs/cern.ch/cms/slc5_amd64_gcc462/cms/dbs-client/DBS_2_1_1_patch1_1/lib/ ;
export X509_USER_PROXY=$HOME/x509up ;
