#!/usr/bin/python3
import argparse
import configparser
from dataclasses import dataclass
import hashlib
import json
import subprocess
import time
import uuid
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import logging
import ssl

@dataclass
class CloudConfig:
    device_key: str
    device_union_id: str
    cert_path: str
    mqtt_broker: str

    def from_section(cloud_config: configparser.SectionProxy):
        return CloudConfig(
            cloud_config['deviceKey'],
            cloud_config['deviceUnionid'],
            cloud_config['certPath'],
            cloud_config["mqttBroker"]
        )

def get_cloud_config(configFile: str) -> CloudConfig:
    config = configparser.ConfigParser()
    config.read(configFile)

    environment = config['device']['env']
    zone = config['device']['zone']

    if zone == 'cn':
        section_name = f'cloud_{environment}'
    else:
        section_name = f'cloud_{zone}_{environment}'

    cloud_config = config[section_name]
    return CloudConfig(
        cloud_config['deviceKey'],
        cloud_config['deviceUnionid'],
        cloud_config['certPath'],
        cloud_config["mqttBroker"]
    )

def get_model_id() -> str:
    with open('/userdata/app/gk/config/api.cfg', 'r') as f:
        config = json.loads(f.read())
        return config['cloud']['modelId']

def get_firmware_version() -> str:
    with open('/useremain/dev/version', 'r') as f:
        return f.read().strip()

def get_encrypted_device_key(cert_path: str, device_key: str) -> str:
    command = f'printf "{device_key}" | openssl rsautl -encrypt -inkey {cert_path}/caCrt -certin -pkcs -in /dev/stdin 2> /dev/null | base64 -w 0'
    output = subprocess.check_output(['sh', '-c', command])
    return output.decode('utf-8').strip()

# # Alternative Python implementation, requires cryptography module
# from cryptography import x509
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
# import base64
# def get_encrypted_device_key_py(certPath: str, deviceKey: str) -> str:
#     with open(f'{certPath}/caCrt', "rb") as fp:
#             pem_data = fp.read()
#     cert: x509.Certificate = x509.load_pem_x509_certificate(pem_data)
#     public_key = cert.public_key()
#     token_bytes = deviceKey.encode('utf-8')
#     encrypted_token = public_key.encrypt(
#         token_bytes,
#         padding.PKCS1v15(),
#     )
#     encrypted_token_b64 = base64.b64encode(encrypted_token)
#     return encrypted_token_b64.decode('utf-8')

def md5_hex(input: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(input.encode('utf-8'))
    return md5_hash.hexdigest()

def get_mqtt_login(union_id: str, enc_device_key: str) -> tuple[str, str]:
    md5_taco = md5_hex(f'{union_id}{enc_device_key}{union_id}')
    username = f'dev|fdm|20024|{md5_taco}'
    password = enc_device_key
    return (username, password)

def get_ssl_context(cert_path: str) -> ssl.SSLContext:
    cert_file = f'{cert_path}/deviceCrt'
    key_file = f'{cert_path}/devicePk'
    ca_file = f'{cert_path}/caCrt'
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers(('ALL:@SECLEVEL=0'),)
    ssl_context.load_cert_chain(cert_file, key_file, None)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_verify_locations(ca_file)
    return ssl_context

class CloudUpdateClient:
    def __init__(
            self,
            model_id: str,
            firmware_version: str,
            cloud_config: CloudConfig,
            timeout: int,
        ):
        self.model_id = model_id
        self.firmware_version = firmware_version
        self.device_key = cloud_config.device_key
        self.device_union_id = cloud_config.device_union_id
        self.cert_path = cloud_config.cert_path
        self.broker_url = urlparse(cloud_config.mqtt_broker)
        self.timeout = timeout
        self.update_info = None

    def get_update_info(self):
        enc_device_key = get_encrypted_device_key(self.cert_path, self.device_key)
        username, password = get_mqtt_login(self.device_union_id, enc_device_key)

        # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.device_union_id, clean_session=True)
        client = mqtt.Client(protocol=mqtt.MQTTv5, client_id=self.device_union_id)
        client.enable_logger()
        client.username_pw_set(username, password)

        if self.broker_url.scheme == 'ssl':
            ssl_context = get_ssl_context(self.cert_path)
            client.tls_set_context(ssl_context)
            client.tls_insecure_set(True)

        client.on_connect = self._on_connect
        client.on_connect_fail = self._on_connect_fail
        client.on_message = self._on_message

        client.connect(self.broker_url.hostname, self.broker_url.port or 1883, keepalive=self.timeout)

        end = time.time() + self.timeout
        while time.time() < end:
            client.loop()
            if self.update_info:
                return self.update_info

        return { "status": "timed_out" }


    def _on_connect(self, client: mqtt.Client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            client.disconnect()
            raise Exception(f'Failed to connect: {reason_code}')
        else:
            self._subscribe_to_ota(client)

    def _subscribe_to_ota(self, client):
        client.subscribe(f'anycubic/anycubicCloud/v1/+/printer/{self.model_id}/{self.device_union_id}/ota')

        payload = {
            'type': 'ota',
            'action': 'reportVersion',
            'timestamp': round(time.time() * 1000),
            'msgid': str(uuid.uuid4()),
            'state': 'done',
            'code': 200,
            'msg': 'done',
            'data': {
                'device_unionid': self.device_union_id,
                'machine_version': '1.1.0',
                'peripheral_version': '',
                'firmware_version': self.firmware_version,
                'model_id': self.model_id
            }
        }
        client.publish(f'anycubic/anycubicCloud/v1/printer/public/{self.model_id}/{self.device_union_id}/ota/report', json.dumps(payload))

    def _on_connect_fail(self, client, userdata):
        client.disconnect()
        raise Exception(f'Failed to connect: {userdata}')

    def _on_message(self, client, userdata, msg):
        ota = msg.payload.decode("utf-8")
        client.disconnect()
        ota = json.loads(ota)
        self.update_info = ota.get('data')
        if not self.update_info:
            self.update_info = { "status": "up_to_date" }

if __name__ == "__main__":
    # Ignore warning about TLS v1.2
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    MODEL_ID_MAP = {
        "K2P": 20021,
        "K3": 20024,
        "KS1": 20025,
    }

    parser = argparse.ArgumentParser(description="Report firmware update information.")
    parser.add_argument(
        "-m", "--model",
        choices=MODEL_ID_MAP.keys(),
        help="Printer model. Default: auto"
    )
    parser.add_argument(
        "-v", "--version",
        type=str,
        help="Current firmware version. Default: auto"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="/userdata/app/gk/config/device.ini",
        help="Device configuration file. Default: /userdata/app/gk/config/device.ini"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=25,
        help="Time in seconds to wait for a response. Default: 25"
    )
    parser.add_argument(
        "-d", "--debug",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enables debug logging."
    )
    args = parser.parse_args()

    if not args.model:
        model_id = get_model_id()
    else:
        model_id = MODEL_ID_MAP[args.model]
        if not args.version:
            args.version = "0" # Response will be latest firmware

    if not args.version:
        args.version = get_firmware_version()

    firmware_version = args.version

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    cloud_config = get_cloud_config(args.config)

    update_client = CloudUpdateClient(model_id, firmware_version, cloud_config, args.timeout)
    data = update_client.get_update_info()

    print(json.dumps(data))
