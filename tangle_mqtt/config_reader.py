from collections import namedtuple
import configparser

from globals import CONFIG_FILE
from globals import IOTA_DEPTH_VALUE, BROKER_PORT_DEFAULT
from globals import VERIFIER_SERVER_HOST_DEFAULT, VERIFIER_SERVER_PORT_DEFAULT


class ConfigurationMissing(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return("CONFIG PARSER ERROR -- Message : %s" %(self.msg))


class ConfigReader:
    def __init__(self):
        self.config = configparser.ConfigParser()
        if not self.config.read(CONFIG_FILE):
            raise ConfigurationMissing("No Config File in location")


    def sections(self):
        return self.config.sections()


    def get_iota_node_config(self):
        if not self.config.has_section('IOTA_NODE'):
            raise ConfigurationMissing("No configuration for IOTA Node provided")
        else:
            if not self.config.has_option('IOTA_NODE', 'node_address'):
                raise ConfigurationMissing("IOTA Node address not provided")
            else:
                iota_node_address = self.config.get('IOTA_NODE', 'node_address')

            iota_port = None
            if self.config.has_option('IOTA_NODE', 'port'):
                try:
                    iota_port = self.config.getint('IOTA_NODE', 'port')
                except ValueError:
                    print("IOTA NODE port value is not a number")
            if not iota_port:
                raise ConfigurationMissing("IOTA node port is not provided")

            if not self.config.has_option('IOTA_NODE', 'depth_value'):
                print("How much deep in Tangle to go to, to start random walk " \
                      "not specified.. Taking default value of %d" %(IOTA_DEPTH_VALUE,))
            try:
                depth_value = self.config.getint('IOTA_NODE', 'depth_value',
                                                 fallback=IOTA_DEPTH_VALUE)
            except ValueError:
                print("IOTA NODE depth value is not a number, defaulting to %d ... " \
                      %(IOTA_DEPTH_VALUE,))
                depth_value = IOTA_DEPTH_VALUE

        iota_node = namedtuple("iNode", ["addr", "port", "depth"])
        return iota_node(addr=iota_node_address, port=iota_port, depth=depth_value)


    def get_device_config(self):
        if not self.config.has_section('DEVICE'):
            raise ConfigurationMissing('Device identity to Tangle not specified')
        else:
            if not self.config.has_option('DEVICE', 'send_seed'):
                raise ConfigurationMissing("The Sender Seed of the device connected" \
                                           " to Tangle not specified")
            else:
                dev_seed = self.config.get('DEVICE', 'send_seed')

            if not self.config.has_option('DEVICE', 'recv_addr'):
                raise ConfigurationMissing("The Receiver Address to send the data to not specified")
            else:
                recv_addr = self.config.get('DEVICE', 'recv_addr')

        device = namedtuple("device", ["send_seed", "recv_addr"])
        return device(send_seed=dev_seed, recv_addr=recv_addr)


    def get_broker_config(self):
        if not self.config.has_section('BROKER'):
            raise ConfigurationMissing("A MQTT Broker needs to be specified to " \
                                       "listen to message topics. No Broker found.")
        else:
            if self.config.has_option('BROKER', 'topics'):
                topics = self.config.get('BROKER', 'topics')
                try:
                    intrstd_topics = [_t.strip() for _t in topics.split(',')]
                except Exception:
                    raise ConfigurationMissing("Topics specified are unparsable," \
                                               " not listening to anything.")
            else:
                raise ConfigurationMissing("No topics have been specified, Broker " \
                                           "won't be listening to anything.")

            if not self.config.has_option('BROKER', 'node_address'):
                raise ConfigurationMissing("MQTT Broker IP needs to be specified "\
                                           "in configuration")
            else:
                broker_address = self.config.get('BROKER', 'node_address')

            if not self.config.has_option('BROKER', 'port'):
                print("MQTT Broker Port not specified, defaulting to %d" %(BROKER_PORT_DEFAULT,))
            try:
                broker_port = self.config.getint('BROKER', 'port', fallback=BROKER_PORT_DEFAULT)
            except ValueError:
                print("Config Parser Error : BROKER port value is not a number, " \
                      "defaulting to %d ... " %(BROKER_PORT_DEFAULT,))
                broker_port = BROKER_PORT_DEFAULT

        broker = namedtuple("broker", ["topics", "mqtt_addr", "mqtt_port"])
        return broker(topics=intrstd_topics, mqtt_addr=broker_address, mqtt_port=broker_port)


    def get_verifier_server_config(self):
        verifier_server = namedtuple("verifier_server", ["serv_addr", "serv_port"])
        if not self.config.has_section('VERIFIER_SERVER'):
            print("ATTENTION : No Verifier servers specified, Nothing would be verified ...")
            return verifier_server(serv_addr=None, serv_port=None)
        else:
            if not self.config.has_option('VERIFIER_SERVER', 'server_address'):
                print("Verifier Server IP not specified, defaulting to %s ..." \
                      %(VERIFIER_SERVER_HOST_DEFAULT,))
            verifier_server_addr = self.config.get('VERIFIER_SERVER', 'server_address',
                                                   fallback=VERIFIER_SERVER_HOST_DEFAULT)

            if not self.config.has_option('VERIFIER_SERVER', 'server_port'):
                print("Verifier server port not specified, defaulting to %d ..." \
                      %(VERIFIER_SERVER_PORT_DEFAULT,))
            try:
                verifier_server_port = self.config.getint('VERIFIER_SERVER', 'server_port',
                                                          fallback=VERIFIER_SERVER_PORT_DEFAULT)
            except ValueError:
                print("Config Parser Error : Verifier Server port value is not a number," \
                      " defaulting to %d ... " %(VERIFIER_SERVER_PORT_DEFAULT,))
                verifier_server_port = VERIFIER_SERVER_PORT_DEFAULT
            return verifier_server(serv_addr=verifier_server_addr, serv_port=verifier_server_port)


    def get_verifiers_config(self, section_id):
        verifier_id = self.config.get(section_id, 'ID', fallback=None)
        if not self.config.has_option(section_id, 'class_name'):
            raise ConfigurationMissing("Define class_name in config file for your " \
                                       "Verifier %s. Skipping this verifier ..." %(section_id,))
        else:
            class_name = self.config.get(section_id, 'class_name', fallback=None)
        if not self.config.has_option(section_id, 'seed'):
            raise ConfigurationMissing("Define seed in config file for the Verifier " \
                                       "%s to connect to IOTA and fetch data ... " \
                                       "Skipping this verifier" %(section_id,))
        else:
            seed = self.config.get(section_id, 'seed', fallback=None)
        push_back = self.config.get(section_id, 'push_back', fallback=False)

        verifiers = namedtuple("verifiers", ["id", "class_name", "seed", "push_back"])
        return verifiers(id=verifier_id, class_name=class_name, seed=seed,
                               push_back=push_back)
