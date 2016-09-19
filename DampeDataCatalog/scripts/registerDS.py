"""
Created on Sep 19, 2016

@author: zimmer
@brief: script to register dataset to catalog
@note: url: http://dampevm6.unige.ch:4000 
@todo: integrate config setup
"""
from requests import post
from os.path import isfile
from argparse import ArgumentParser
URL = "dampevm6.unige.ch:4000"

def main(args=None):
    parser = ArgumentParser(usage="Usage: %(progs)s [options]",description="register new entry in DFC")
    parser.add_argument("-f","--file", dest="file", type=str, default=None, help="point to filename for bulk ingest")
    parser.add_argument("--dtype", dest="dtype", type=str, default=None, help="2A or MC")
    parser.add_argument("-r","--release", dest="release", type=str, default=None, help="release (relevant for 2A only)")
    opts = parser.parse_args(args)
    #res = post("%s/job/" % DAMPE_WORKFLOW_URL,
    #           data={"taskname": taskName, "t_type": t_type, "override_dict": str(override_dict),
    #                 "n_instances": n_instances, "site": site,
    #                 "depends": dependent_tasks},
    #           files={"file": open(xmlFile, "rb")})
    #res.raise_for_status()
    #if res.json().get("result", "nok") == "ok":
    #    print 'Added job %s with %i instances' % (taskName, n_instances)
    #else:
    #    print "Error message: %s" % res.json().get("error", "")

if __name__ == "__main__":
    main()
