#! /bin/sh
#sudo apt-get update
sudo apt-get install postgresql collectd -y
cd /home/ec2-user
wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/
sudo service collectd restart
wget 192.168.186.182/triplestore/postgresql.conf
sudo mv postgresql.conf /etc/postgresql/9.1/main/
wget 192.168.186.182/triplestore/pg_hba.conf
sudo mv pg_hba.conf /etc/postgresql/9.1/main/
sudo service postgresql restart
wget 192.168.186.182/triplestore/create_db.sql
sudo -u postgres psql --file=create_db.sql
rm triplestore.sh

