"""
Created on Sep 19, 2016

@author: zimmer
@brief: script to register dataset to catalog
@note: url: http://dampevm6.unige.ch:4000 
@todo: integrate config setup
"""
from DampeDataCatalog import version as DV
from requests import post
from os.path import isfile
from argparse import ArgumentParser
URL = "http://dampevm6.unige.ch:4000"

def main(args=None):
    parser = ArgumentParser(usage="Usage: %(prog)s [options]",description="register new entry in DFC",epilog="This is DampeDataCatalog version %s"%DV)
    for key in ['chksum','prefix','target','release','size','dtype']:
        parser.add_argument("-%s"%key[0],"--%s"%key, dest=key, type=long if key == 'size' else str, default=None)
    parser.add_argument("-f","--file",dest="file",type=str,default=False,help="read input from text-file and attempt a bulk-register")
    parser.add_argument("-o","--is_original",dest="is_origin",action="store_true",default=False,help="use if this is the source")
    parser.add_argument("-F","--fullPath",dest="fullPath",type=str, default=None, help="full path to file")
    parser.add_argument("-S","--site",type=str, default=None, help="*deprecated* site where replica is registered")
    keys_to_remove_for_bulk = ['chksum','size','fullPath','file']
    opts = parser.parse_args(args)
    my_dict = vars(opts)
    bulk = False
    if opts.file is not None:
        if isfile(opts.file):
            print 'found file in list of supplied arguments, assuming bulk mode'
            infile=opts.file
            print 'found %i entries in %s'%(len(open(infile,'r').readlines()),infile)
            for key in keys_to_remove_for_bulk:
                my_dict.pop(key)
            bulk = True
    else:
        my_dict.pop("file")
    keys_to_remove = []
    for key,value in my_dict.iteritems():
        if value is None:
            keys_to_remove.append(key)
    for key in keys_to_remove: 
        my_dict.pop(key)
    # explicit bool conversion.
    if 'is_origin' in my_dict: my_dict['is_origin'] = bool(my_dict['is_origin'])
    res = None
    if bulk:
        res = post("%s/bregister"%URL, data = my_dict, files={"file":open(infile,"r")})
    else:
        res = post("%s/register"%URL, data = my_dict)
    res.raise_for_status()
    js = res.json()
    if js.get("result", "nok") == "ok":
        print 'added %i new entries to DB'%(js.get("nEntries",0))
    else:
        print 'error during POST'
        print js.get("error")

if __name__ == "__main__":
    main()
