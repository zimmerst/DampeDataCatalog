from flask import Blueprint, request, redirect, render_template, url_for
from flask_mongoengine.wtf import model_form
from flask.views import MethodView
from DampeDataCatalog.core.models import DampeFile

files = Blueprint('files', __name__, template_folder='templates')

class ListView(MethodView):

    def get(self):
        files = DampeFile.objects.all()
        return render_template('files/list.html', files=files)

class DetailView(MethodView):

    def get(self,slug):
        dfile = DampeFile.objects.get_or_404(slug=slug)
        return render_template('files/detail.html', dampeFile=dfile, replicas=dfile.replicas)

# Register the urls
files.add_url_rule('/', view_func=ListView.as_view('list'),methods=["GET"])
files.add_url_rule('/<slug>/', view_func=DetailView.as_view('detail'))
