import json
import socket
import sys
import threading

from iota import Iota, Address, ProposedTransaction, Tag, TryteString
import paho.mqtt.client as mqtt

from config_reader import ConfigReader, ConfigurationMissing


def msg_id_generator():
    msg_id = 0
    while True:
        msg_id += 1
        yield msg_id


def on_connect(client, userdata, flags, rc):
    topics = userdata.get('topics', [])
    for _t in topics:
        client.subscribe(_t)


def tangle_and_verify(message_id, userdata, message_data):
    if not userdata or not message_id:
        return

    recv_addr = userdata.get('address_to_send', '').encode()
    iota_obj = userdata.get('iota_obj', None)
    depth_value = userdata.get('depth', 3)
    verify_server = userdata.get('verify_server', None)

    try:
        txn_1 = ProposedTransaction(address=Address(recv_addr,),
                                    value=0,
                                    tag=Tag(TryteString.from_unicode(message_id)),
                                    message=TryteString.from_unicode(message_data))
        _transactions = [txn_1, ]
        iota_obj.send_transfer(depth=depth_value, transfers=_transactions)
        print("Saved Message with ID %s succesfully to the Tangle" %(message_id,))
    except Exception:
        print("Could not save to Tangle -- Message ID : {0}, Data : {1}".format(message_id, message_data))
        return

    try:
        msg_to_send = "{id}/".format(id=message_id)
        print('Sent across to the verifier server : %s' %(msg_to_send,))
        verify_server.sendall(msg_to_send.encode('utf-8'))
    except Exception:
        print("Something went wrong! Couldn't send data for Msg ID = %s to our verify server" %(message_id,))


def on_data_received(client, userdata, message):
    full_message_topic = str(message.topic).rstrip('/')
    find_last_dir = full_message_topic.rfind('/') + 1
    message_topic = full_message_topic[find_last_dir:]
    if not message_topic:
        message_topic = full_message_topic

    message_data = {'topic' : message_topic,
                    'data' : str(message.payload.decode()),}
    message_data_str = json.dumps(message_data)

    print('Received Message from MQTT - %s : %s' %(message_topic, message_data_str,))

    id_gen = userdata.get('msg_id_gen')
    message_id = str(id_gen())

    new_thread = threading.Thread(target=tangle_and_verify, kwargs=dict(message_id=message_id,
                                                                        message_data=message_data_str,
                                                                        userdata=userdata))
    new_thread.start()


def startup():

    try:
        conf_reader = ConfigReader()
        iNode = conf_reader.get_iota_node_config()
        device = conf_reader.get_device_config()
        broker = conf_reader.get_broker_config()
        verifier = conf_reader.get_verifier_server_config()
    except ConfigurationMissing as e:
        print("%s \n\n ... Exiting " %(str(e),))
        sys.exit(0)

    iota_node_address = iNode.addr
    iota_port = iNode.port
    depth_value = iNode.depth
    dev_seed = device.send_seed
    recv_addr = device.recv_addr
    broker_address = broker.mqtt_addr
    broker_port = broker.mqtt_port
    intrstd_topics = broker.topics
    verifier_server = verifier.serv_addr
    verifier_server_port = verifier.serv_port

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
