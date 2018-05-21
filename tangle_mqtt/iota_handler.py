from iota import Iota, Address, ProposedTransaction, Tag, TryteString
import paho.mqtt.client as mqtt

import configparser
import json
import os
import socket
import sys


CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              os.pardir, 'resources/config.ini'))

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

    message_data = {'topic' : message_topic,
                    'data' : str(message.payload.decode()),}
    message_data_str = json.dumps(message_data)

    print('Received Message from MQTT - %s : %s' %(message_topic, message_data,))

    recv_addr = userdata.get('address_to_send').encode()
    iota_obj = userdata.get('iota_obj', None)
    depth_value = userdata.get('depth', 3)
    verify_server = userdata.get('verify_server', None)
    id_gen = userdata.get('msg_id_gen')

    message_id = str(id_gen())

    try:
        txn_1 = ProposedTransaction(address=Address(recv_addr,),
                                    value=0,
                                    tag=Tag(TryteString.from_unicode(message_id)),
                                    message=TryteString.from_unicode(message_data_str))
        _transactions = [txn_1, ]
        iota_obj.send_transfer(depth=depth_value, transfers=_transactions)
        print ("Saved Message with ID %s succesfully to the Tangle" %(message_id,))
    except Exception:
        print("Could not save to Tangle -- Message ID : {0}, Data : {1}".format(message_id, message_data))

    try:
        msg_to_send = "{id}/".format(id=message_id)
        print('Sent across to the verifier server : %s' %(msg_to_send,))
        verify_server.sendall(msg_to_send.encode('utf-8'))
    except Exception:
        print("Something went wrong! Couldn't ping our verify server")


def startup():
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE):
        print("No configuration file found! Exiting startUp!")
        sys.exit(0)

    iota_node_address = None
    iota_port = None
    depth_value = None
    dev_seed = None
    recv_addr = None
    broker_address = None
    broker_port = None
    intrstd_topics = []
    verifier_server = None
    verifier_server_port = None

    if not config.has_section('IOTA_NODE'):
        print("No configuration for IOTA Node provided, exiting ...")
        sys.exit(0)
    else:
        if not config.has_option('IOTA_NODE', 'node_address'):
            print("IOTA Node address not provided, exiting ...")
            sys.exit(0)
        else:
            iota_node_address = config.get('IOTA_NODE', 'node_address')

        iota_port = None
        if config.has_option('IOTA_NODE', 'port'):
            try:
                iota_port = config.getint('IOTA_NODE', 'port')
            except ValueError:
                print("CONFIG PARSING ERROR : IOTA NODE port value is not a number ... ")
                pass
        if not iota_port:
            print("IOTA node port is not provided, exiting ...")
            sys.exit(0)

        if not config.has_option('IOTA_NODE', 'depth_value'):
            print("How much deep in Tangle to go to, to start random walk not specified ...")
            print("Taking default value of 3") # TBD
        try:
            depth_value = config.getint('IOTA_NODE', 'depth_value', fallback=3)
        except ValueError:
            print("CONFIG PARSING ERROR : IOTA NODE depth value is not a number, defaulting to 3 ... ")
            depth_value = 3

    if not config.has_section('DEVICE'):
        print('Device identity to Tangle not specified, exiting ...')
        sys.exit(0)
    else:
        if not config.has_option('DEVICE', 'send_seed'):
            print('The Sender Seed of the device connected to Tangle and adding data, not specified, exiting ...')
            sys.exit(0)
        else:
            dev_seed = config.get('DEVICE', 'send_seed')

        if not config.has_option('DEVICE', 'recv_addr'):
            print('The Receiver Address to send the data to not specified, exiting ...')
            sys.exit(0)
        else:
            recv_addr = config.get('DEVICE', 'recv_addr')

    if not config.has_section('BROKER'):
        print('A MQTT Broker needs to be specified, to listen to message topics. No Broker found. Exiting ...')
        sys.exit(0)
    else:
        if config.has_option('BROKER', 'topics'):
            topics = config.get('BROKER', 'topics')
            try:
                intrstd_topics = [_t.strip() for _t in topics.split(',')]
            except Exception:
                print("CONFIG PARSING ERROR : Topics specified are unparsable, not listening to anything.. exiting")
                sys.exit(0)
        else:
            print("ATTENTION : No topics have been specified, Broker won't be listening to anything.. exiting")
            sys.exit(0)

        if not config.has_option('BROKER', 'node_address'):
            print("MQTT Broker IP needs to be specified, exiting ...")
            sys.exit(0)
        else:
            broker_address = config.get('BROKER', 'node_address')

        if not config.has_option('BROKER', 'port'):
            print("MQTT Broker Port not specified, defaulting to 1883")
        try:
            broker_port = config.getint('BROKER', 'port', fallback=1883)
        except ValueError:
            print("CONFIG PARSING ERROR : BROKER port value is not a number, defaulting to 1883 ... ")
            broker_port = 1883

    if not config.has_section('VERIFIER_SERVER'):
        print("ATTENTION : No Verifier servers specified, Nothing would be verified ...")
    else:
        if not config.has_option('VERIFIER_SERVER', 'server_address'):
            print("Verifier Server IP not specified, defaulting to localhost ...")
        verifier_server = config.get('VERIFIER_SERVER', 'server_address', fallback='localhost')

        if not config.has_option('VERIFIER_SERVER', 'server_port'):
            print("Verifier server port not specified, defaulting to 9000 ...")
        try:
            verifier_server_port = config.getint('VERIFIER_SERVER', 'server_port', fallback=9000)
        except ValueError:
            print("CONFIG PARSING ERROR : Verifier Server port value is not a number, defaulting to 9000 ... ")
            verifier_server_port = 9000

    iota_obj = Iota('http://{0}:{1}'.format(iota_node_address, iota_port), dev_seed)

    sock = None
    if verifier_server and verifier_server_port:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((verifier_server, verifier_server_port))
            print('Successfully connected to the verifier server ...')
        except:
            print('ATTENTION : Verifier server not up and running, nothing will be verified ...')

    msg_id_gen = msg_id_generator().__next__

    private_data = {'topics' : intrstd_topics,
                    'iota_obj' : iota_obj,
                    'msg_id_gen' : msg_id_gen,
                    'address_to_send' : recv_addr,
                    'depth' : depth_value,
                    'verify_server' : sock, }

    client = mqtt.Client(client_id='iota_mqtt', userdata=private_data)
    client.on_connect = on_connect
    client.on_message = on_data_received
    client.connect(host=broker_address, port=broker_port)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        if sock:
            sock.close()
        print('\n\n... No longer connected to Broker')



if __name__ == '__main__':
    startup()
