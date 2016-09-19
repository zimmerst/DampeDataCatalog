import logging
from json import dumps
from flask import Blueprint, request, redirect, render_template
#from flask_mongoengine.wtf import model_form
from datetime import datetime
from flask.views import MethodView
from DampeDataCatalog import version, start_time, hostName
from DampeDataCatalog.core.models import DampeFile, DataSet, createNewDBEntry
files = Blueprint('files', __name__, template_folder='templates')
logger = logging.getLogger("core")

class Register(MethodView):
    def get(self):
        return 
        
    def post(self):
        """ form args 
            site = str
            is_origin = bool
            chksum = str
            size = long
            fullPath = str
            prefix = str
            target = str
            dtype = str
            
            dtype can be: 2A, MC, might add additional types later.
            MC: dataset name is the base folder (after prefix)
            2A: dataset name is the base folder + 1 layer (after 1 prefix)                
        """
        logger.debug("Register:POST: request form %s", str(request.form))
        try:
            createNewDBEntry(request.form)
            return dumps({"result":"ok"})
            ## done.
        except Exception as err:
            logger.error("request dict: %s", str(request.form))
            logger.exception("Register:POST: %s",err)
            return dumps({"result": "nok", "jobID": "None", "error": str(err)})

class BulkRegister(MethodView):
    def get(self):
        return 
    
        
    def post(self):
        """ form args 
            site : required, if not supplied, will throw exception
            file : must be a text file with 3 columns: checksum, size (bytes), full path
            is_origin : optional (will default to False)
            prefix : optional, defaults to /, remove first occurrence
            dtype : optional, defaults to 2A, other allowed value is MC
            targetdir: optional, defaults to /; used as path for replica registration.
        """
        logger.debug("BulkRegister:POST: request form %s", str(request.form))
        site = str(request.form.get("site", "None"))
        bulk = request.files.get("file", None)
        try:
            if bulk is None: 
                raise Exception("bulk request is emtpy") 
            if site == "None":
                raise Exception("site is not set")
            ## handle the read-out of file here ##
            # move to beginning of file.
            bulk.seek(0)
            newEntries = 0
            for i,line in enumerate(bulk.readlines()):
                chksum = size = fullPath = None
                try:
                    chksum, size, fullPath = line.split()
                except ValueError:
                    logger.error("error processing line %i: %s",i,line)
                    continue
                ## else create entry.
                createNewDBEntry(site=site,is_origin=bool(request.form.get("is_origin",False)),chksum=chksum,
                                 size=size,fullPath=fullPath,prefix=str(request.form.get("prefix","PMU_cluster/")),
                                 target=str(request.form.get("targetdir","/")),dtype=str(request.form.get("dtype","2A")))
                newEntries+=1
            logger.info("added %i new entries",newEntries)
            bulk.close()
            return dumps({"result":"ok","nEntries":newEntries})
            ## done.
        except Exception as err:
            logger.error("request dict: %s", str(request.form))
            logger.exception("BulkRegister:POST: %s",err)
            return dumps({"result": "nok", "jobID": "None", "error": str(err)})

# the views below are all for rendering templates
class InfoView(MethodView):
    def get(self):
        time = datetime.now()
        dtime = (time - start_time).seconds        
        d = divmod(dtime,86400)
        h = divmod(d[1],3600)
        m = divmod(h[1],60)
        s = m[1]        
        uptime = '%03d:%02d:%02d:%02d'%(d[0],h[0],m[0],s)
        return render_template("files/info.html", 
                               server_version=version, uptime=uptime, 
                               start_time=start_time, host=hostName)

class DataSetView(MethodView):
    def get(self):
        ds = DataSet.objects.all()
        return render_template("files/dataset.html", datasets = ds)

class ListView(MethodView):
    def get(self,slug):
        ds = DataSet.objects.get_or_404(slug=slug)
        files = DampeFile.objects.filter(dataset=ds)
        return render_template('files/list.html', files=files, dataset=ds)

class DetailView(MethodView):
    def get(self,slug):
        dfile = DampeFile.objects.get_or_404(slug=slug)
        return render_template('files/detail.html', dampeFile=dfile, replicas=dfile.replicas)

# Register the urls

# below are all rules for the template renderings.
files.add_url_rule('/', view_func=DataSetView.as_view('dataset'),methods=["GET"])
files.add_url_rule('/<slug>/', view_func=ListView.as_view('list'))
files.add_url_rule('/<slug>/detail', view_func=DetailView.as_view('detail'))
files.add_url_rule('/info', view_func=InfoView.as_view('info'),methods=["GET"])
files.add_url_rule('/bregister', view_func=BulkRegister.as_view("bregister"),methods=["GET","POST"])
files.add_url_rule('/register', view_func=Register.as_view("register"),methods=["GET","POST"])

