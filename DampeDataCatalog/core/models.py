import datetime
from mongoengine import CASCADE

from DampeDataCatalog.core import db
from DampeDataCatalog.utils.tools import random_string_generator

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
    fileType        = db.StringField(verbose_name="file extension, root, fits etc.", max_length=16, required=True, default="root")
    slug            = db.StringField(verbose_name="slug", required=True, default=random_string_generator)
    source          = db.StringField(verbose_name="site where file was created", max_length=36, required=False)
    dataset         = db.ReferenceField("DataSet",reverse_delete_rule=CASCADE)
    fileName        = db.StringField(verbose_name="full file name", max_length=1024, required=True)
    replicas        = db.ListField(db.ReferenceField("DampeFileReplica"))
    tstart          = db.LongField(verbose_name="TStart (ms) for orbit data", required=False)
    tstop           = db.LongField(verbose_name="TStop (ms) for orbit data", required=False)
    
    def addReplica(self,rep):
        if not isinstance(rep,DampeFileReplica): raise Exception("must be a DampeFileReplica")
        query = DampeFileReplica.objects.filter(dampeFile=self,site=rep.site)
        if query.count(): raise Exception("replica is already associated with this site & file")
        rep.save()
        self.replicas.append(rep)
        self.save()

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'fileName','slug'],
        'ordering': ['-created_at']
    }
    
    
class DampeFileReplica(db.Document):
    created_at      = db.DateTimeField(default=datetime.datetime.now, required=True)
    checksum        = db.StringField(verbose_name="checksum reported", max_length=64, required=True, default=None)
    path            = db.StringField(verbose_name="full path on site", max_length=1024, required=True)
    site            = db.StringField(verbose_name="site where replica is stored", max_length=12, required=False)
    status          = db.StringField(verbose_name="status of replica", max_length=64, required=True, default=None)
    dampeFile       = db.ReferenceField("DampeFile", reverse_delete_rule=CASCADE)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'status', 'site'],
        'ordering': ['-created_at']
    }
    