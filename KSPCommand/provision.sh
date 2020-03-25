#!/bin/bash -x
apt update;
apt upgrade;
apt install -y gpgkey2ssh open-ssh;
mkdir ~/.ssh/;
wget -q -c -nc https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip;
unzip -qq -n ngrok-stable-linux-amd64.zip;
apt-get install -qq -o=Dpkg::Use-Pty=0 openssh-server pwgen > /dev/null;
mkdir -p /var/run/sshd;
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config;
echo "PasswordAuthentication {USE_PASSWORD}" >> /etc/ssh/sshd_config
echo "LD_LIBRARY_PATH=/usr/lib64-nvidia" >> /root/.bashrc;
echo "export LD_LIBRARY_PATH" >> /root/.bashrc;
echo "
remote_management: null
tunnels:
  first:
    addr: 22
    proto: tcp
  second:
    addr: 8050
    proto: http
" > ngrok.yml;

PASSWORD=`pwgen -1 16`;
if [ "{USE_PASSWORD}" = "yes" ]; then
  echo root:$PASSWORD | chpasswd
  echo "Use password $PASSWORD" > /content/.passwd;
else
  curl -L "{KEY_URL}" > ~/.ssh/authorized_keys;
  echo "Use a ssh key validated on github." > /content/.passwd;
fi
