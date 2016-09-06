from DampeDataCatalog import version
from socket import getfqdn
kind = "server"
#kind = cfg.get("global", "installation")
db = None
app = None
if kind == 'server':    
    
    from flask import Flask
    from flask.ext.mongoengine import MongoEngine
    app = Flask(__name__)
    app.config.update(LOGGER_NAME="core")
    app.config['MONGODB_DB'] = "DampeFileCatalog"
    app.config['MONGODB_USERNAME'] = "dampe"
    app.config['MONGODB_PASSWORD'] = "dampe"
    app.config['MONGODB_HOST'] = "dampevm5.unige.ch"
    app.config['MONGODB_PORT'] = 25013
    app.config["SECRET_KEY"] = "KeepThisS3cr3t"
    db = MongoEngine(app)
    
    def register_blueprints(app):
        # Prevents circular imports
        from DampeDataCatalog.core.views import files
        app.register_blueprint(files)
    
    register_blueprints(app)
    
    def main():
        app.logger.info("started DAMPE Data Catalog Server Version: %s on %s",version,getfqdn())
        app.run()
else:
    def main():
        pass

if __name__ == '__main__':
    if kind == 'server':
        main()
