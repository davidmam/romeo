import paho.mqtt.client as mqtt
import json
import yaml
import os
import socket

def load_config(config_file="romeo.yaml"):
    """
    Load configuration from a YAML file.
    
    Args:
        config_file: Path to the config file (default: config.yaml)
    
    Returns:
        Dictionary with mqtt_url and topic configuration
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file '{config_file}' not found")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def get_ip_address():
    """
    Retrieve the current IP address of the machine.
    
    Returns:
        String containing the IP address
    """
    try:
        # Connect to a public DNS server (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error retrieving IP address: {e}")
        return "127.0.0.1"

class MQTTClient:
    def __init__(self, broker="localhost", port=1883, topic="topic/#", user=None, password=None, birdnetpi='LogieStreet', onmsg=None):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.user=user
        self.password=password
        self.birdnetpi= birdnetpi
        self.msg_method=onmsg
        self.subscribed=False
        self.remote_ip=None
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.topic)
        self.subscribed=True
    
    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        self.msg_method(self, msg)
    def set_remote(self, ip):
        self.remote_ip = ip 
           
    
    def publish(self, topic, payload, qos=0, retain=False):
        """
        Publish a message to the MQTT broker.
        
        Args:
            topic: The MQTT topic to publish to
            payload: The message payload (will be converted to JSON if dict)
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether to retain the message on the broker
        """
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        
        result = self.client.publish(topic, payload, qos, retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Failed to publish to {topic}: {mqtt.error_string(result.rc)}")
        return result
    
    def connect(self):
        """Connect to the MQTT broker."""
        self.client.tls_set()
        if self.user:
            self.client.username_pw_set(self.user, self.password)
        self.client.connect(self.broker, self.port, 60)
    
    def start(self):
        """Start the MQTT client loop."""
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
    def run_forever(self):
        self.client.loop_forever()

def message_callback(client, msg):
    txt=msg.payload.decode().split('=')
    if txt[0] == 'romeo' and len(txt)==2 and txt[1]==client.birdnetpi:
        client.publish('dundeebionet/romeo', {'juliet': client.birdnetpi,'ip': get_ip_address()})
if __name__=='__main__':        
    config=load_config()
    print(config)
    mqtt_client = MQTTClient(broker=config['mqtt_url'], topic=config['topic'], port=config['mqtt_port'], 
                             user=config.get('mqtt_user'), password=config.get('mqtt_password'), birdnetpi=config['birdnetpi'], onmsg=message_callback)
    mqtt_client.connect()
    mqtt_client.run_forever()


