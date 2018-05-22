import configparser
import socket
import sys

import verifiers
from globals import CONFIG_FILE


def start_verify_server():
    count = input('Enter number of verifiers to run (press enter for all configured in ini file): ')
    try:
        count = int(count)
        if count == 0:
            print('Verifier Server quitting, since number of verifiers is zero..!!')
            sys.exit(0)
    except ValueError:
        count = None

    iota_node_address = None
    iota_port = None
    recv_addr = None
    verifier_server = None
    verifier_server_port = None

    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE):
        print("Configuration file non-existant, exiting ... \n")
        sys.exit(0)

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

    if not config.has_section('DEVICE'):
        print('Device identity to Tangle not specified, exiting ...')
        sys.exit(0)
    else:
        if not config.has_option('DEVICE', 'recv_addr'):
            print('The Receiver Address to send the data to not specified, exiting ...')
            sys.exit(0)
        else:
            recv_addr = config.get('DEVICE', 'recv_addr')

    if not config.has_section('VERIFIER_SERVER'):
        print("ATTENTION : No Verifier servers specified explicitly, defaulting to localhost:9000 ...")
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

    iota_host = 'http://{0}:{1}'.format(iota_node_address, iota_port)

    verifier_names = [item for item in config.sections() if item.startswith('V_')]
    if count == None:
        count = len(verifier_names)

    verifier_iota = {}
    for i in range(count):
        _ver = verifier_names[i]
        verifier_id = config.get(_ver, 'ID', fallback='Verifier{id}'.format(id=i))

        if not config.has_option(_ver, 'class_name'):
            print("Define class_name in config file for your Verifier %s. Skipping this verifier ..." %(_ver,))
        elif not config.has_option(_ver, 'seed'):
            print("Define seed in config file for the Verifier %s to connect to IOTA and fetch data ... Skipping this verifier" %(_ver,))
        else:
            class_name = config.get(_ver, 'class_name')
            _seed = config.get(_ver, 'seed')
            verify_server = eval('verifiers.{cls_name}'.format(cls_name=class_name)) # TBD
            _obj = verify_server(verifier_id, iota_host, _seed)
            verifier_iota[verifier_id] = _obj

    # Start our server for listening to verifier calls
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((verifier_server, verifier_server_port))
    sock.listen()
    try:
        while True:
            print("Waiting for new connections ..")
            connection, client_address = sock.accept()
            print("Received New Connection from : %s" %(str(client_address),))
            while True:
                _b_msg = connection.recv(14)
                curr_msg = _b_msg.decode('utf-8')
                print("Received from the IOTA subscriber : %s" %(curr_msg,))
                if curr_msg:
                    all_msgs = curr_msg.split('/')
                    print("All msgs : " + str(all_msgs))
                    for one_msg in all_msgs:
                        if not one_msg:
                            continue
                        message_id = one_msg
                        for (i,o) in verifier_iota.items():
                            print("Called verifier %s Run" %(i,))
                            o.run(msg_id=message_id)
                    print("Done with one sequence")
                else:
                    break


    except KeyboardInterrupt:
        sock.close()
        print('\n\n... Verifier server not running anymore')



if __name__ == '__main__':
    start_verify_server()
