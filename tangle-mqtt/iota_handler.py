from iota import Iota, Address, ProposedTransaction, Tag, TryteString
import paho.mqtt.client as mqtt

import configparser
import os
import socket
import sys


CONFIG_FILE = os.path.relpath(os.path.join(os.pardir, 'resources/config.ini'))


def msg_id_generator():
    msg_id = 0
    while True:
        msg_id += 1
        yield msg_id


def on_connect(client, userdata, flags, rc):
    topics = userdata.get('topics', [])
    for _t in topics:
        client.subscribe(_t)


def on_data_received(client, userdata, message):
    full_message_topic = str(message.topic).rstrip('/')
    find_last_dir = full_message_topic.rfind('/') + 1
    message_topic = full_message_topic[find_last_dir:]
    if not message_topic:
        message_topic = full_message_topic

    message_data = str(message.payload.decode())

    print('Received Message from MQTT - %s : %s' %(message_topic, message_data,))

    recv_addr = userdata.get('address_to_send').encode()
    iota_obj = userdata.get('iota_obj', None)
    depth_value = userdata.get('depth', 1)
    verify_server = userdata.get('verify_server', None)
    id_gen = userdata.get('msg_id_gen')

    message_id = str(id_gen())

    try:
        txn_1 = ProposedTransaction(address=Address(recv_addr,),
                                    value=0,
                                    tag=Tag(TryteString.from_unicode(message_id)),
                                    message=TryteString.from_unicode(message_data))
        _transactions = [txn_1, ]
        iota_obj.send_transfer(depth=depth_value, transfers=_transactions)
        print ("Sent Message with ID %s succesfully to the Tangle" %(message_id,))

    except:
        print("Could not save to Tangle -- Message ID : {0}, Data : {1}".format(message_id, message_data))

    try:
        msg_to_send = "{id}-{topic}/".format(id=message_id, topic=message_topic)
        print('Sent across to the verifier server : %s' %(msg_to_send,))
        verify_server.sendall(msg_to_send.encode('utf-8'))
    except:
        print("Something went wrong! Couldn't ping our verify server")


def startup():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    iota_node_address = config.get('IOTA_NODE', 'node_address')
    iota_port = config.getint('IOTA_NODE', 'port')
    depth_value = config.getint('IOTA_NODE', 'depth_value')
    dev_seed = config.get('DEVICE', 'send_seed')
    recv_addr = config.get('DEVICE', 'recv_addr')
    broker_address = config.get('BROKER', 'node_address')
    broker_port = config.getint('BROKER', 'port')
    topics = config.get('BROKER', 'topics')
    verifier_server = config.get('VERIFIER_SERVER', 'server_address')
    verifier_server_port = config.getint('VERIFIER_SERVER', 'server_port')

    intrstd_topics = [_t.strip() for _t in topics.split(',')]
    iota_obj = Iota('http://{0}:{1}'.format(iota_node_address, iota_port), dev_seed)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((verifier_server, verifier_server_port))
        print('Successfully connected to the verifier server ...')
    except:
        print('Verifier server not running ...')
        sys.exit(0)

    msg_id_gen = msg_id_generator().__next__

    private_data = {'topics' : intrstd_topics,
                    'iota_obj' : iota_obj,
                    'msg_id_gen' : msg_id_gen,
                    'address_to_send' : recv_addr,
                    'depth' : depth_value,
                    'recv_addr' : recv_addr,
                    'verify_server' : sock, }

    client = mqtt.Client(client_id='iota_mqtt', userdata=private_data)
    client.on_connect = on_connect
    client.on_message = on_data_received
    client.connect(host=broker_address, port=broker_port)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        sock.close()
        print('\n\n... No longer connected to Broker')



if __name__ == '__main__':
    startup()
