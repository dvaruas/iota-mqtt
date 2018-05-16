import configparser

import os
import socket
import sys

import verifier

CONFIG_FILE = os.path.abspath(os.path.join(os.pardir, 'resources/config.ini'))


def start_verify_server():
    count = input('Enter number of verifiers to run (default 1): ')
    try:
        count = int(count)
        if count == 0:
            sys.exit(0)
    except ValueError:
        count = 1

    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE):
        print("Configuration file non-existant, exiting ... \n")
        sys.exit(0)

    try:
        iota_node_address = config.get('IOTA_NODE', 'node_address')
        iota_port = config.getint('IOTA_NODE', 'port')
        recv_addr = config.get('DEVICE', 'recv_addr')
        verifier_server = config.get('VERIFIER_SERVER', 'server_address')
        verifier_server_port = config.getint('VERIFIER_SERVER', 'server_port')
    except:
        print("Configuration file is corrupt, exiting ... \n")
        sys.exit(0)

    iota_host = 'http://{0}:{1}'.format(iota_node_address, iota_port)
    verifier_iota = {}
    for i in range(1, count + 1):
        verifier_id = 'VERIFIER_{0}'.format(i,)
        try:
            verify_server = eval('verifier.Verifier{0}'.format(i,))
            _seed = config.get(verifier_id, 'seed')
            _obj = verify_server(verifier_id, iota_host, _seed)
            verifier_iota[verifier_id] = _obj
        except KeyError:
            print("Configuration file is incomplete, exiting ... \n")
            sys.exit(0)

    # Start our server for listening to verifier calls
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((verifier_server, verifier_server_port))
    sock.listen()
    try:
        while True:
            print("Waiting for new connections ..")
            connection, client_address = sock.accept()
            while True:
                _b_msg = connection.recv(100)
                curr_msg = _b_msg.decode('utf-8')
                print("Received from the IOTA subscriber : %s" %(curr_msg,))
                if curr_msg:
                    all_msgs = curr_msg.split('/')
                    print("All msgs : " + str(all_msgs))
                    for one_msg in all_msgs:
                        if not one_msg:
                            continue
                        one_msg_split = one_msg.split('-')
                        print ('One message split : ' + str(one_msg_split))
                        message_id = one_msg_split[0]
                        message_topic = one_msg_split[1]
                        for (i,o) in verifier_iota.items():
                            print("Called verifier Run")
                            o.run(msg_id=message_id, item_name=message_topic)
                    print("Done with one sequence")
                else:
                    break


    except KeyboardInterrupt:
        sock.close()
        print('\n\n... Verifier server not running anymore')



if __name__ == '__main__':
    start_verify_server()
