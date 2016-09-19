import logging
import datetime
from json import loads
from mongoengine import CASCADE
from os.path import splitext, join as pJoin, basename
from DampeDataCatalog.core import db
from DampeDataCatalog.utils.tools import random_string_generator
logger = logging.getLogger("core")

class DataSet(db.Document):
    created_at      = db.DateTimeField(default=datetime.datetime.now, required=True)
    slug            = db.StringField(verbose_name="slug", required=True, default=random_string_generator)
    name            = db.StringField(verbose_name="dataset name", max_length=128, required=True)
    kind            = db.StringField(max_length=24, required=False)
    files           = db.ListField(db.ReferenceField("DampeFile"))

    def addFile(self,df):
        if not isinstance(df,DampeFile): raise Exception("must be a DampeFile instance")
        query = DampeFile.objects.filter(dataset=self,fileName=df.fileName)
        if query.count(): raise Exception("replica is already associated with this site & file")
        df.save()
        self.files.append(df)
        self.save()

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'name','kind','slug'],
        'ordering': ['-created_at']
    }
    
class DampeFile(db.Document):
    created_at      = db.DateTimeField(default=datetime.datetime.now, required=True)
    fileType        = db.StringField(verbose_name="file extension, root, fits etc.", max_length=6, required=True, default="root")
    slug            = db.StringField(verbose_name="slug", required=True, default=random_string_generator)
    dataset         = db.ReferenceField("DataSet",reverse_delete_rule=CASCADE)
    fileName        = db.StringField(verbose_name="full file name", max_length=1024, required=True)
    replicas        = db.ListField(db.ReferenceField("DampeFileReplica"))
    tStart          = db.LongField(verbose_name="TStart (ms) for orbit data", required=False)
    tStop           = db.LongField(verbose_name="TStop (ms) for orbit data", required=False)
    tStartDT        = db.DateTimeField(verbose_name="TStart (human-format) for orbit data", required=False)
    tStopDT         = db.DateTimeField(verbose_name="TStop (human-format) for orbit data", required=False)
    nEvents         = db.LongField(verbose_name="number of events stored",required=False, default=0)
    fileSize        = db.LongField(verbose_name="file size in bytes",required=False,default=0)

    def addReplica(self,rep):
        if not isinstance(rep,DampeFileReplica): raise Exception("must be a DampeFileReplica")
        query = DampeFileReplica.objects.filter(dampeFile=self,site=rep.site)
        if query.count(): raise Exception("replica is already associated with this site & file")
        rep.save()
        self.replicas.append(rep)
        self.save()
    
    def getOrigin(self):
        try:
            return DampeFileReplica.objects.get(dampeFile=self,is_origin=True)
        except DampeFileReplica.DoesNotExist:
            return None
    
    def verifyCheckSums(self):
        """ returns True if all checksums are identical, False if error is encountered """
        verify=True
        origin = self.getOrigin()
        if origin:
            chk_raw = origin.checksum
            for rep in self.replicas:
                if not rep.is_origin and rep.status=="bad":
                    if rep.checksum != chk_raw:
                        rep.setStatus("bad",minor="bad checksum")
                        verify=False
        return verify

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'fileName','slug','tStart','tStop'],
        'ordering': ['-created_at']
    }
    
    
class DampeFileReplica(db.Document):
    created_at      = db.DateTimeField(default=datetime.datetime.now, required=True)
    checksum        = db.StringField(verbose_name="checksum reported", max_length=64, required=True, default=None)
    is_origin       = db.BooleanField(verbose_name="is true for original file", default=False, required=True)
    path            = db.StringField(verbose_name="full path on site", max_length=1024, required=True)
    site            = db.StringField(verbose_name="site where replica is stored", max_length=12, required=False)
    status          = db.StringField(verbose_name="status of replica", max_length=64, required=True, default=None)
    minor_status    = db.StringField(verbose_name="detailed status of replica", max_length=64, required=False, default=None)
    dampeFile       = db.ReferenceField("DampeFile", reverse_delete_rule=CASCADE)

    def setStatus(self,stat,minor_stat=None):
        q = DampeFileReplica.objects.filter(site=self.site,path=self.path,dampeFile=self.dampeFile)
        if minor_stat:
            q.update(minor_status=minor_stat)
        q.update(status=stat)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'status', 'site'],
        'ordering': ['-created_at']
    }

# this is a convenience method
def createNewDBEntry(**kwargs):
    """ convenience method, will figure out internal DC structure by itself. 
        variables:
        site = str
        is_origin = bool
        chksum = str
        size = long
        fullPath = str
        prefix = str
        target = str
        dtype = str
        release = str
        dtype can be: 2A, MC, might add additional types later.
        MC: dataset name is the base folder (after prefix)
        2A: dataset name is the base folder + 1 layer (after 1 prefix)            
    """
    # must separate a bit more from path
    fPath = kwargs.get("fullPath",None)
    # remove prefix
    fPath = fPath.replace(kwargs.get("prefix","/"),"")
    walker = fPath.split("/")
    dtype = kwargs.get("dtype","2A")
    # next, extract dataset name
    dsname = None
    if dtype == "2A":
        # extract date-stamp
        dsname = pJoin("2A",kwargs.get("release",""))
        for walk in walker:
            if walk.startswith("201"):
                dsname = pJoin(dsname,walk)
    else:
        dsname = walker[0]
    dsQuery = dfQuery = None
    try:
        dsQuery = DataSet.objects.get(name=dsname, kind=dtype)
    except DataSet.DoesNotExist:
        dsQuery = DataSet(name=pJoin(walker[0],walker[1]) if dtype == "2A" else walker[0], kind=dtype)
        logger.debug("created new DataSet object, saving.")
        dsQuery.save()
    try:
        dfQuery = DampeFile.objects.get(fileType=splitext(fPath)[-1],fileName=basename(fPath),dataset=dsQuery)
    except DampeFile.DoesNotExist:
        dfQuery = DampeFile(fileType=splitext(fPath)[-1],fileName=basename(fPath),dataset=dsQuery)
        dfQuery.save()
    dfQuery.update(size=long(kwargs.get("size")))
    
    for key in ['tStart','tStop','tStartDT','tStopDT','nEvents']:
        value = kwargs.get(key,None)
        if value is not None:
            if key in ['tStart','tStop','nEvents']:
                value = long(value)
            if key in ['tStartDT','tStopDT']:
                '"2016-09-19 14:52:49.862971"'
                str_value = loads(value)
                value = datetime.datetime.strptime(str_value,'%Y-%m-%d %H:%M:%S.%f')
            dfQuery.update(key=value)
                
    rep = DampeFileReplica(checksum=kwargs.get("chksum"),is_origin=bool(kwargs.get("is_origin",False)),
                           path=kwargs.get("target","/"),site=kwargs.get("site",""),status="New")
    rep.save()
    dfQuery.addReplica(rep)
    dsQuery.addFile(dfQuery)
