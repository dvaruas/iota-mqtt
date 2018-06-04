import configparser
from flask import Flask, render_template
import os
import sqlite3
import sys

from globals import CONFIG_FILE, DB_FILE, TABLE_NAME
from globals import VISUAL_HOST_DEFAULT, VISUAL_PORT_DEFAULT


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
    _c.execute("PRAGMA TABLE_INFO ({t_name})".format(t_name=TABLE_NAME))

    _heads = []
    try:
        _heads = [t[1] for t in _c.fetchall()]
    except:
        pass

    _c.close()

    # We don't want the msg_ids, remove them for now
    all_data = [_data[1:] for _data in all_data]

    # Get the Verifier names by ID
    fixed_entries = ['msg_id', 'timestamp', 'item_name', 'item_value']
    verifier_names = [id for id in _heads if id not in fixed_entries]

    if all_data:
        return render_template('show_data.html', data=all_data, verifier_names=verifier_names)
    else:
        return no_data_banner


if __name__ == '__main__':
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE):
        print("CONFIG PARSER ERROR -- Message : No Config File in location " \
              "\n\n ... Exiting ")
        sys.exit(0)

    if not config.has_section("VISUAL"):
        print("CONFIG PARSER ERROR -- Message : No Visualization configured. " \
              "Using %s:%d" %(VISUAL_HOST_DEFAULT, VISUAL_PORT_DEFAULT))
        v_host = VISUAL_HOST_DEFAULT
        v_port = VISUAL_PORT_DEFAULT
    else:
        if not config.has_option('VISUAL', 'host'):
            print("CONFIG PARSER ERROR -- Message : Visual host not configured," \
                  " falling to %s" %(VISUAL_HOST_DEFAULT,))
        v_host = config.get('VISUAL', 'host', fallback=VISUAL_HOST_DEFAULT)
        if not config.has_option('VISUAL', 'port'):
            print("CONFIG PARSER ERROR -- Message : Visual port not configured," \
                  " using port %d" %(VISUAL_PORT_DEFAULT,))
        v_port = config.getint('VISUAL', 'port', fallback=VISUAL_PORT_DEFAULT)

    app.run(host=v_host, port=v_port)
