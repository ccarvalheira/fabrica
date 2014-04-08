#! /bin/sh
sudo apt-get install collectd erlang -y
sudo apt-get install -f -y
cd /home/ubuntu
wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/
sudo service collectd restart
wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.2.4/rabbitmq-server_3.2.4-1_all.deb
sudo dpkg -i rabbitmq-server_3.2.4-1_all.deb
#config rabbit
rm rabbit.sh
