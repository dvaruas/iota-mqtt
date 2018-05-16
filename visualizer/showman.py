import configparser
from flask import Flask, render_template
import os
import sqlite3
import sys


DB_FILE = os.path.relpath(os.path.join(os.pardir, 'resources/values.db'))
CONFIG_FILE = os.path.abspath(os.path.join(os.pardir, 'resources/config.ini'))
TABLE_NAME = 'messages'


app = Flask(__name__)

@app.route('/')
def show_data():
    no_data_banner = "<html><body><h1>No displayable data yet!</h1></body></html>"

    if not os.path.exists(DB_FILE):
        return no_data_banner

    # Fetch the Data from our DB
    _conn = sqlite3.connect(DB_FILE)
    _c = _conn.cursor()
    _c.execute("SELECT * FROM {t_name}".format(t_name=TABLE_NAME))
    all_data = _c.fetchall()
    verifier_count = 0
    _c.execute("PRAGMA TABLE_INFO ({t_name})".format(t_name=TABLE_NAME))

    _heads = []
    try:
        _heads = [t[1] for t in _c.fetchall()]
    except:
        pass

    _c.close()

    for i in range(len(_heads)):
        search_param = 'VERIFIER_{id}'.format(id=(verifier_count + 1))
        if search_param in _heads:
            verifier_count += 1

    # We probably don't want the msg_ids, remove them for now
    all_data = [_data[1:] for _data in all_data]

    if all_data:
        return render_template('show_data.html', data=all_data, verifier_count=verifier_count)
    else:
        return no_data_banner


if __name__ == '__main__':
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE):
        print("Configuration file non-existant, exiting ... \n")
        sys.exit(0)

    try:
        v_host = config.get('VISUAL', 'host')
        v_port = config.getint('VISUAL', 'port')
    except:
        print("Configuration file is corrupt, exiting ... \n")
        sys.exit(0)

    app.run(host=v_host, port=v_port)
