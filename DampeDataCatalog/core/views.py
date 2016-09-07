from flask import Blueprint, request, redirect, render_template, url_for
from flask_mongoengine.wtf import model_form
from datetime import datetime
from flask.views import MethodView
from DampeDataCatalog import version, start_time, hostName
from DampeDataCatalog.core.models import DampeFile, DataSet

files = Blueprint('files', __name__, template_folder='templates')

class InfoView(MethodView):
    def get(self):
        time = datetime.now()
        dtime = (time - start_time).seconds        
        d = divmod(dtime,86400)
        h = divmod(d[1],3600)
        m = divmod(h[1],60)
        s = m[1]        
        uptime = '%03d:%02d:%02d:%02d' %(d,h,m,s)
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
files.add_url_rule('/', view_func=DataSetView.as_view('dataset'),methods=["GET"])
files.add_url_rule('/<slug>/', view_func=ListView.as_view('list'))
files.add_url_rule('/<slug>/detail', view_func=DetailView.as_view('detail'))
files.add_url_rule('/info', view_func=InfoView.as_view('info'),methods=["GET"])

