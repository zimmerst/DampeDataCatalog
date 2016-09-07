import datetime
from mongoengine import CASCADE

from DampeDataCatalog.core import db
from DampeDataCatalog.utils.tools import random_string_generator

class DampeFile(db.Document):
    created_at      = db.DateTimeField(default=datetime.datetime.now, required=True)
    fileType        = db.StringField(verbose_name="file extension, root, fits etc.", max_length=16, required=True, default="root")
    source          = db.StringField(verbose_name="site where file was created", max_length=36, required=False)
    slug            = db.StringField(verbose_name="slug", required=True, default=random_string_generator)
    fileName        = db.StringField(verbose_name="full file name", max_length=1024, required=True)
    replicas        = db.ListField(db.ReferenceField("DampeFileReplica"))
    kind            = db.StringField(max_length=24, required=False)
    tstart          = db.LongField(verbose_name="TStart (ms) for orbit data", required=False)
    tstop           = db.LongField(verbose_name="TStop (ms) for orbit data", required=False)
    
    def addReplica(self,rep):
        if not isinstance(rep,DampeFileReplica): raise Exception("must be a DampeFileReplica")
        try: 
            replica = DampeFileReplica.objects(dampeFile=self,site=rep.site)
        except DampeFileReplica.DoesNotExist:
            replica = rep
            self.replicas.append(replica)
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
    