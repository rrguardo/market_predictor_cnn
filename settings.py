
import logging

FORMAT = r'%(asctime)s %(levelname)s [%(pathname)s:%(lineno)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)

from sqlalchemy import create_engine
ENGINE = create_engine('mysql+mysqlconnector://root:1234567*@localhost/fx', echo=False)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)