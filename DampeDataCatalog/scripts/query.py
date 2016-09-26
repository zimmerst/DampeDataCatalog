"""
Created on Sep 19, 2016

@author: zimmer
@brief: script to query the catalog, will return list of file(replicas) that satisfy query conditions
@note: url: http://dampevm6.unige.ch:4000 
@todo: integrate config setup
"""
from requests import get as rGet
from argparse import ArgumentParser
URL = "http://dampevm6.unige.ch:4000"
            
def main(args=None):
    parser = ArgumentParser(usage="Usage: %(prog)s [options]",description="query entries in DFC")
    for key in ['site','fileName','dataset','kind']:
        parser.add_argument("-%s"%key[0],"--%s"%key, dest=key, type=str, default=None)
    parser.add_argument("--fileType",dest='fileType', type=str, default=None, help="file extension to query (root/fits)")
    parser.add_argument("--status",dest='status', type=str, default="good", help="return files matching this status")
    # time selection
    parser.add_argument("--tStart",dest='tStart', type=long, default=None, help="tStart MJD")
    parser.add_argument("--tStop",dest='tStop', type=long, default=None, help="tStart MJD")
    parser.add_argument("--tStartDT",dest='tStartDT', type=str, default=None, help="tStart in UTZ:, format is %Y-%m-%d %H:%M:%S.%f")
    parser.add_argument("--tStopDT",dest='tStopDT', type=str, default=None, help="tStart in UTZ:, format is %Y-%m-%d %H:%M:%S.%f")
    parser.add_argument("-o","--output",dest='output',type=str,default=None,help='use this option to redirect output to file')
    opts = parser.parse_args(args)
    my_dict = vars(opts)
    keys_to_remove = ['output']
    for k,v in my_dict.iteritems():
        if v is None:
            keys_to_remove.append(k)
    for key in keys_to_remove: my_dict.pop(key)
    res = rGet("%s/query"%URL, data = my_dict)
    res.raise_for_status()
    js = res.json()
    if js.get("result", "nok") == "ok":
        fo = "\n".join(js.get("urls",[]))
        if opts.output is not None:
            fout = open(opts.output,'w')
            fout.write(fo)
            fout.close()
            print 'wrote output to %s'%opts.output
        else:
            print fo
    else:
        print 'error during GET, see below for details'
        print js.get("error")

if __name__ == "__main__":
    main()
