import json
from pathlib import Path


ROOT_DIR = Path(__file__).parent.absolute()
DB_PATH = Path.joinpath(ROOT_DIR, 'my_db.sqlite')

API_TOKEN = open(Path(ROOT_DIR, 'cert', 'token.txt'), 'r').read()
WEBHOOK_CONF = json.load(open(Path(ROOT_DIR, 'cert', 'webhook_conf.json'), 'r'))
WEBHOOK_HOST = WEBHOOK_CONF['host']
WEBHOOK_PORT = WEBHOOK_CONF['port']  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = WEBHOOK_CONF['listen']  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = Path(ROOT_DIR, 'cert', 'webhook_cert.pem')  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = Path(ROOT_DIR, 'cert', 'webhook_pkey.pem')  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)


PROXY = {'https': 'socks5h://127.0.0.1:9150'}


# tmp
USER_FILE = Path(ROOT_DIR, 'tmp', 'users.json')
TMP_FILE = Path(ROOT_DIR, 'tmp', 'tmp.json')


# bot core
SLEEP_AFTER_INFO = 3

# routing
CACHE_QUERIES = False

MY_TG = int(open(Path(ROOT_DIR, 'cert', 'tg_id.txt'), 'r').read())
MEDIA_FOLDER = Path(ROOT_DIR, 'Media')
