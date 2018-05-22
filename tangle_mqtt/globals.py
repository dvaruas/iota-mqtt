import os


CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                           'resources/config.ini'))
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                       'resources/values.db'))

TABLE_NAME = 'messages'
