from subprocess import PIPE
import os, commands, subprocess

def rfstat(dirname):

    '''
        Return a list from Popen command. Later on to be used via rfstat_item to get the ROOT file size in EOS
    '''

    try:
        output=subprocess.Popen(["/afs/cern.ch/project/eos/installation/0.2.5/bin/eos.select", "ls","-l",dirname], stdout=PIPE)
    except BaseException, error:
        print "ERROR (in rfstat.py/rfstat)!!"
        print "Cannot check the file existence\n"
        print "Error "+error.__str__()
        print "Returning dummy\n"
        return 0

    return output

def rfstat_item(dirname,item):

    '''
        Return the file size of filename stored in EOS
    '''

    if(item=="Size"):
        element = -5  #file size
    elif(item=="File"):
        element = -1  #file name
    else:
        print "Option not valid. Please use: 'Size' or 'File'"
        return 0

    try:
        eosContent = rfstat(dirname)
    except BaseException, error:
        print error.__str__()

    try:
        RootFileSize = eosContent.communicate()[0].split(" ")[element]
    except IndexError, error:
        print "ERROR (in rfstat/rfstat_item)"
        print "File/Directory was not found"
        print "Error"+error.__str__()
        return 0
    except BaseException, error:
        print "ERROR (in rfstat/rfstat_item)!!!"
        print "Unexpected error: "+error.__str__()
        return -1

    return RootFileSize