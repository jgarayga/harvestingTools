import os, commands

def _remove_prefix(filename,prefix):
    if filename.startswith(prefix): filename = filename[len(prefix):]
    return filename

def rfstat(filename):
    """Return tuple (status,output) of rfstat shell command. Output is a list of strings
    (one entry per line). Raises RFIOError if rfstat command is not found."""
    statcmd = 'rfstat'
    ##if not envutil.find_executable(statcmd):
    ##    raise RFIOError( '%s not found in PATH' % statcmd )
    cmd = '%s %s' % (statcmd,_remove_prefix(filename,'rfio:'))
    status,output = commands.getstatusoutput( cmd )
    status >>= 8

    return (status, output.split(os.linesep))

def rfstat_item(filename,item):
    """Return the contents of <item> in the rfstat output"""
    status,output = rfstat(filename)
    if status: return None
    for line in output:
        if line.startswith( item ):
            colon = line.index(':')
            return line[colon+1:].strip()

    # nothing found
    return None
