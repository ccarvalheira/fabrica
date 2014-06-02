#! /bin/bash
cd /home/ec2-user
if [ ! -f apache-cassandra-2.0.6-bin.tar.gz ]; then
  wget http://mirrors.fe.up.pt/pub/apache/cassandra/2.0.6/apache-cassandra-2.0.6-bin.tar.gz
  tar xvf apache-cassandra-2.0.6-bin.tar.gz
  mv apache-cassandra-2.0.6 cassandra
fi
sudo apt-get install openjdk-7-jre-headless python-pip collectd -y
if [ ! -d supervisor ]; then
  sudo pip install supervisor
  mkdir supervisor
  cd supervisor
  mkdir log
  wget 192.168.186.182/tsstore/supervisord.conf
  cd /home/ec2-user
  wget 192.168.186.182/tsstore/upstart_supervisor.conf
  sudo mv upstart_supervisor.conf /etc/init/supervisor.conf
  sudo service supervisor start
fi
cd /home/ec2-user
wget 192.168.186.182/tsstore/cassandra.yaml
mv cassandra.yaml cassandra/conf/cassandra.yaml
wget 192.168.186.182/tsstore/log4j-server.properties
mv log4j-server.properties cassandra/conf/log4j-server.properties
wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/
sudo service collectd restart
rm tsstore.sh
