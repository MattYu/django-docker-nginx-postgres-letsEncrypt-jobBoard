import logging, logging.handlers

logger = logging.getLogger("djangosyslog")
hdlr = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
formatter = logging.Formatter('%(filename)s: %(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)