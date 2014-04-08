#! /bin/sh
sudo apt-get install collectd python-dev python-virtualenv git-core libpq-dev -y

wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/
sudo service collectd restart

cd /home/ubuntu

if [ ! -d ws_scalable ]; then
  cd /home/ubuntu
  wget 192.168.186.182/api/id_rsa
  chmod 600 id_rsa
  mv id_rsa .ssh/
  mkdir ws_scalable
  cd ws_scalable
  git clone ubuntu@192.168.186.182:/home/ubuntu/scripts/api/ws_scalable
  virtualenv env
  . env/bin/activate
  pip install -r ws_scalable/requirements.txt
  deactivate
  cd /home/ubuntu
else
  cd /home/ubuntu/ws_scalable/ws_scalable
  git pull
  cd ..
  . env/bin/activate
  pip install -r ws_scalable/requirements.txt
  deactivate
fi
cd /home/ubuntu
rm api.sh
