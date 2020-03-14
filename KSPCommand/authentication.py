import requests
import os
import getpass
import urllib
import json
import warnings
from .utils import PROVISIONING_SCRIPT
from .exception import KSPCommandException


def authenticate(token=None, github=None, debug=False):
    if not token:
        raise KSPCommandException(("Provide token from "
                                      "https://dashboard.ngrok.com/auth"))

    password="no"
    key_url = ""
    if not github:
        warnings.warn(("No github provided. Will use password based "
                "authentication."))
        github = ""
        password="yes"
    else:
        key_url = f"github.com/{github}.keys"

    result = os.popen(PROVISIONING_SCRIPT.format(token=token, KEY_URL=key_url,
        USE_PASSWORD=password)).read()

    # Output authentication results
    print(open(os.path.join(os.path.dirname(__file__), '.passwd')).read())

    if debug:
        print(result)

    # Start daemon services. Need ipython so it can hang.
    get_ipython().system_raw('/usr/sbin/sshd -D &')
    get_ipython().system_raw(
        './ngrok start --config=/content/ngrok.yml --authtoken=$token --all &')
    get_ipython().system_raw('sleep 1')

    # Get ngrok url
    with urllib.request.urlopen('http://localhost:4040/api/tunnels/second') as response:
      data = json.loads(response.read().decode())
      endpoint = data['public_url']
      print(f'endpoint: {endpoint}')

    #Get public address and print connect command
    with urllib.request.urlopen('http://localhost:4040/api/tunnels/first') as response:
      data = json.loads(response.read().decode())
      [host, port] = data['public_url'][6:].split(':')
      print(f'SSH command: ssh -R 50000:localhost:50000 -R 50001:localhost:50001 -p{port} root@{host}')

    return endpoint
