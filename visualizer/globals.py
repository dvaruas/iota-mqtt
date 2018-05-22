import os


# ---------- Keep part enclosed identical with tangle_mqtt/globals.py --------

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                           'resources/config.ini'))
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                       'resources/values.db'))

TABLE_NAME = 'messages'

VISUAL_HOST_DEFAULT = 'localhost'
VISUAL_PORT_DEFAULT = 9797

#------------------------------------------------------------------------------
