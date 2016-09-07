'''
Created on Sep 6, 2016

@author: zimmer
'''
import logging
from socket import getfqdn
from datetime import datetime
# Define Version
import pkg_resources

version = pkg_resources.get_distribution(__package__).version
hostName= getfqdn()
start_time = datetime.now()

try:
#    from DmpWorkflow.config.defaults import DAMPE_LOGFILE
    from DampeDataCatalog.utils.logger import initLogger#
    initLogger("/tmp/dfc.log")
    from DampeDataCatalog.utils.logger import logger_batch, logger_script, logger_core
except Exception as err:
    logging.warning("Log service client was not initialized properly: %s", str(err))
