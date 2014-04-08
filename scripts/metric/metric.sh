#! /bin/sh
#sudo apt-get update
sudo apt-get install collectd python-virtualenv python-dev git-core libcairo2-dev python-cairo -y
cd /home/ubuntu
wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/collectd.conf
sudo service collectd restart
if [ ! -d bucky ]; then
  mkdir bucky
  cd bucky
  virtualenv env
  . env/bin/activate
  pip install bucky
  cd /home/ubuntu
  wget 192.168.186.182/metric/bucky.conf
  mv bucky.conf bucky/
  deactivate
fi
cd /home/ubuntu
if [ ! -d graphite-web ]; then
  git clone https://github.com/graphite-project/graphite-web.git
  cd graphite-web
  sudo pip install -r requirements.txt
  cd ..
fi
if [ ! -d carbon ]; then
  git clone https://github.com/graphite-project/carbon.git
  cd carbon
  sudo pip install -r requirements.txt
  cd..
fi
cd /home/ubuntu
sudo pip install django==1.4
#sudo pip install https://github.com/graphite-project/ceres/tarball/master
#sudo pip install carbon whisper graphite-web supervisor daemonize
wget 192.168.186.182/metric/carbon.conf.example
sudo cp carbon.conf.example /opt/graphite/conf/carbon.conf
wget 192.168.186.182/metric/storage-schemas.conf.example
sudo cp storage-schemas.conf.example /opt/graphite/conf/storage-schemas.conf
sudo /opt/graphite/bin/carbon-cache.py start

cd /home/ubuntu
wget 192.168.186.182/metric/local_settings.py.example
sudo cp local_settings.py.example /opt/graphite/webapp/graphite/local_settings.py

if [ ! -d supervisor ]; then
  cd /home/ubuntu
  mkdir supervisor
  cd supervisor
  mkdir log
  cd /home/ubuntu
  wget 192.168.186.182/metric/supervisord.conf
  mv supervisord.conf supervisor/supervisord.conf
  wget 192.168.186.182/tsstore/upstart_supervisor.conf
  sudo mv upstart_supervisor.conf /etc/init/supervisor.conf
  sudo service supervisor start
fi

sudo chown ubuntu -R /opt
chmod +x /opt/graphite/webapp/graphite/manage.py
/opt/graphite/webapp/graphite/manage.py syncdb
cd /home/ubuntu
rm *.example
rm *.conf
rm metric.sh
