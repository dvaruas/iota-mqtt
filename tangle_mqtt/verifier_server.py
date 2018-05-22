import socket
import sys

from config_reader import ConfigReader, ConfigurationMissing
import verifiers
from globals import CONFIG_FILE


def start_verify_server():

    count = input("Enter number of verifiers to run " \
                  "(press enter for all configured in ini file): ")
    try:
        count = int(count)
        if count == 0:
            print('Verifier Server quitting, since number of verifiers is zero..!!')
            sys.exit(0)
    except ValueError:
        count = None

    try:
        conf_reader = ConfigReader()
        iNode = conf_reader.get_iota_node_config()
        device = conf_reader.get_device_config()
        verifier = conf_reader.get_verifier_server_config()
    except ConfigurationMissing as e:
        print("%s \n\n ... Exiting " %(str(e),))
        sys.exit(0)

    iota_node_address = iNode.addr
    iota_port = iNode.port
    recv_addr = device.recv_addr
    verifier_server = verifier.serv_addr
    verifier_server_port = verifier.serv_port

    iota_host = 'http://{0}:{1}'.format(iota_node_address, iota_port)

    verifier_names = [item for item in conf_reader.sections() if item.startswith('V_')]
    if count == None:
        count = len(verifier_names)

    verifier_iota = {}
    for i in range(count):
        _ver = verifier_names[i]

        try:
            verifier = conf_reader.get_verifiers_config(_ver)
        except ConfigurationMissing as e:
            print(str(e))
            continue

        verifier_id = verifier.id if verifier.id else 'Verifier-{id}'.format(id=i)
        class_name = verifier.class_name
        _seed = verifier.seed
        push_back = verifier.push_back

        verify_server = eval('verifiers.{cls_name}'.format(cls_name=class_name)) # TBD
        _obj = verify_server(verifier_id, iota_host, _seed, push_back)
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
