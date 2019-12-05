import os
PROVISIONING_SCRIPT = open(
    os.path.join(os.path.dirname(__file__), 'provision.sh')).read()
