#! /bin/bash
sudo apt-get install collectd python-virtualenv python-dev git-core -y

cd /home/ec2-user
wget 192.168.186.182/tsstore/collectd.conf
sudo mv collectd.conf /etc/collectd/
sudo service collectd restart

if [ ! -d ws_tasks ]; then
  cd /home/ec2-user
  wget 192.168.186.182/api/id_rsa
  chmod 600 id_rsa
  mv id_rsa .ssh/
  mkdir ws_tasks
  cd ws_tasks
  virtualenv env
  . env/bin/activate
  pip install celery
  deactivate
  git clone ec2-user@192.168.186.182:/home/ec2-user/scripts/celery/ws_tasks
  cd /home/ec2-user
else
  cd /home/ec2-user/ws_tasks/ws_tasks
  git pull
fi


if [ ! -d supervisor ]; then
  cd /home/ec2-user
  mkdir supervisor
  cd supervisor
  mkdir log
  sudo pip install supervisor
  wget 192.168.186.182/celery/supervisord.conf
  supervisord -c supervisord.conf
else
  cd /home/ec2-user/supervisor
  rm supervisord.conf
  wget 192.168.186.182/celery/supervisord.conf
  supervisorctl -c supervisord.conf reload
fi

cd /home/ec2-user
rm celery.sh
