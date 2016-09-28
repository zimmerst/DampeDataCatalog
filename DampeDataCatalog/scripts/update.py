"""
Created on Sep 19, 2016

@author: zimmer
@brief: update replica, all that's needed is the filename along with meta-data
@note: url: http://dampevm6.unige.ch:4000 
@todo: integrate config setup
"""
from DampeDataCatalog import version as DV
from requests import post as rPost
from argparse import ArgumentParser
URL = "http://dampevm6.unige.ch:4000"

def main(args=None):
    parser = ArgumentParser(usage="Usage: %(prog)s [options]",description="update entries in DFC",epilog="This is DampeDataCatalog version %s"%DV)
    for key in ['site','fileName','nEvents','kind']:
        parser.add_argument("-%s"%key[0],"--%s"%key, dest=key, type=long if key == 'nEvents' else str, default=None)
    parser.add_argument("--fileType",dest='fileType', type=str, default="root", help="file extension to query (root/fits)")
    parser.add_argument("--status",dest='status', type=str, default="good", help="major status (of replica)")
    parser.add_argument("--minor_status",dest='minor_status', type=str, default=None, help="minor status of dataset, leave blank if not needed")
    parser.add_argument("--checksum",dest='checksum', type=str, default=None, help="update checksum (may happen?)")
    # time selection
    parser.add_argument("--tStart",dest='tStart', type=long, default=None, help="tStart MJD")
    parser.add_argument("--tStop",dest='tStop', type=long, default=None, help="tStart MJD")
    parser.add_argument("--tStartDT",dest='tStartDT', type=str, default=None, help="tStart in UTZ:, format is YYYY-mm-dd HH:MM:SS.f")
    parser.add_argument("--tStopDT",dest='tStopDT', type=str, default=None, help="tStart in UTZ:, format is YY-mm-dd HH:MM:SS.f")
    
    opts = parser.parse_args(args)
    my_dict = vars(opts)
    keys_to_remove = ['output']
    for k,v in my_dict.iteritems():
        if v is None:
            keys_to_remove.append(k)
    for key in keys_to_remove: my_dict.pop(key)
    res = rPost("%s/query"%URL, data = my_dict)
    res.raise_for_status()
    js = res.json()
    if js.get("result", "nok") == "ok":
        print 'successfully updated %i replicas'%js.get("nReplica",0)
    else:
        print 'error during POST, see below for details'
        print js.get("error")

if __name__ == "__main__":
    main()
