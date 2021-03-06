# Set the path
from os.path import abspath, join as oPjoin, dirname
from sys import path as sys_path

sys_path.append(abspath(oPjoin(dirname(__file__), '..')))
from flask_script import Manager, Server, Shell
import DampeDataCatalog.core.models as DFCModels
from DampeDataCatalog.core import app, db

def _make_context():
    return dict(app=app, db=db, models=DFCModels)

manager = Manager(app)
# Turn on debugger by default and reloader
manager.add_command("runserver", Server(use_debugger=True,
                                        use_reloader=True,
                                        host="0.0.0.0",
                                        port="4000"))

manager.add_command("shell", Shell(make_context=_make_context))


def main():
    manager.run()

if __name__ == "__main__":
    main()
