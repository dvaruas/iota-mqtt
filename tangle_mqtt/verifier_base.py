import json
import os
import sqlite3
import time

from iota import Iota, Transaction, Tag, TryteString

from globals import DB_FILE, TABLE_NAME


class Verifier:
    def __init__(self, id, iota_host, seed, push):
        self._id = id
        self._iota_obj = Iota(iota_host, seed)
        self._conn = None
        self._push_data = push
        self._initial_setup()


    def _initial_setup(self):
        _create_table_reqd = not os.path.exists(DB_FILE)
        self._conn = sqlite3.connect(DB_FILE)
        c = self._conn.cursor()

        if _create_table_reqd:
            cmd_ = "CREATE TABLE {t_name} (msg_id INTEGER PRIMARY KEY, timestamp TEXT, " \
                   "item_name TEXT, item_value TEXT)".format(t_name=TABLE_NAME)
            c.execute(cmd_)

        c.execute("PRAGMA TABLE_INFO ({t_name})".format(t_name=TABLE_NAME))
        column_names = [t[1] for t in c.fetchall()]
        if self._id not in column_names:
            c.execute("ALTER TABLE {t_name} ADD COLUMN '{c_name}' TEXT DEFAULT 'False'"\
                      .format(t_name=TABLE_NAME, c_name=self._id))
        self._conn.commit()


    def fetch_data_from_tangle(self, msg_id):
        txns = self._iota_obj.find_transactions(tags=[Tag(TryteString.from_unicode(msg_id))])
        _trytes = self._iota_obj.get_trytes(txns['hashes']).get('trytes', [])
        _values = []
        for _t in _trytes:
            _txn = Transaction.from_tryte_string(_t)
            _value = json.loads(_txn.signature_message_fragment.decode())
            _msg_value = _value.get('data', None)
            _msg_topic = _value.get('topic', None)
            _time = _txn.timestamp
            print('Message ID : %s, Message Topic: %s, Value found : %s' \
                  %(msg_id, _msg_topic, _msg_value,))

            if self._push_data:
                # TBD : Push back to MQTT
                pass

            _tmp = (_msg_topic, _msg_value, _time)
            _values.append(_tmp)
        return _values


    def verification(self, topic, value):
        print('Please overload this method in your class ... ')
        return 'False'


    def save_to_db(self, msg_id, timestamp, item_name, item_value, verification_ans):
        c = self._conn.cursor()
        _msg_id = int(msg_id)
        _time_val = str(timestamp)
        try:
            _time_val = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(timestamp))
        except:
            pass
        try:
            _cmd = "INSERT INTO {t_name} (msg_id, timestamp, item_name, item_value, {v_name}) "\
                      "VALUES ('{m_id}', '{t}', '{i_name}', '{i_val}', '{v_val}') "\
                      .format(t_name=TABLE_NAME, v_name=self._id, m_id=_msg_id, t=_time_val,
                              i_name=item_name, i_val=item_value, v_val=verification_ans)
            c.execute(_cmd)
        except sqlite3.IntegrityError:
            # Row was already present, just update it with our verification answer
            c.execute("UPDATE {t_name} SET {c_name}='{c_val}' WHERE msg_id={m_id}"\
                      .format(t_name=TABLE_NAME, c_name=self._id, c_val=verification_ans, m_id=_msg_id))

        self._conn.commit()


    def run(self, msg_id):
        values = self.fetch_data_from_tangle(msg_id)
        # For each msg_id there should be only one value
        if len(values) == 0:
            return
        elif len(values) > 1:
            raise Exception

        value = values[0]
        msg_topic = value[0]
        msg_value = value[1]
        msg_time = value[2]

        verification_ans = self.verification(msg_topic, msg_value)
        self.save_to_db(msg_id=msg_id, timestamp=msg_time, item_name=msg_topic,
                        item_value=msg_value, verification_ans=verification_ans)


    def __del__(self):
        self._conn.close()
