import os


# ---------- Keep part enclosed identical with visualizer/globals.py --------

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                           'resources/config.ini'))
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                       'resources/values.db'))

TABLE_NAME = 'messages'

VISUAL_HOST_DEFAULT = 'localhost'
VISUAL_PORT_DEFAULT = 9797

#------------------------------------------------------------------------------

IOTA_DEPTH_VALUE = 3

BROKER_PORT_DEFAULT = 1883

VERIFIER_SERVER_HOST_DEFAULT = 'localhost'
VERIFIER_SERVER_PORT_DEFAULT = 9000
