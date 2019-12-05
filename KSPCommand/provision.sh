#!/bin/bash
apt update;
apt upgrade;
apt install -y gpgkey2ssh open-ssh;
mkdir ~/.ssh/;
# I would rather have this done with keybase.io, but I don't think using a
# pgpkey for ssh is trivial
curl https://raw.githubusercontent.com/dmadisetti/KSPCommand/master/key.pub > ~/.ssh/authorized_keys;
wget -q -c -nc https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip;
unzip -qq -n ngrok-stable-linux-amd64.zip;
apt-get install -qq -o=Dpkg::Use-Pty=0 openssh-server pwgen > /dev/null;
mkdir -p /var/run/sshd;
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config;
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
