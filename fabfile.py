from __future__ import with_statement

from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import sudo

from fabric.operations import put

from fabric.contrib.files import exists

from inventory import INV

_BASEP = "/home/ubuntu/fabrica/"
BASEC = _BASEP + "conf/"

def get_basep(group):
    return _BASEP + group + "/"

def host_type():
    run('uname -s')

def install_pip():
    sudo("apt-get install python-pip -y")

def update_supervisor(group):
    BASEP = get_basep(group)
    put(BASEP + "supervisord.conf", "/home/ubuntu/supervisor/")
    put(BASEC + "upstart_supervisor.conf", "/etc/init/supervisor.conf", use_sudo=True)
    sudo("service supervisor restart")


def install_supervisor(group, update=True):
    if not exists("/home/ubuntu/supervisor"):
        install_pip()
        sudo("pip install supervisor")
        run("mkdir -p supervisor/log")
        update_supervisor(group)
    else:
        if update:
            update_supervisor(group)

def update_cassandra(group):
    BASEP = get_basep(group)
    put(BASEP+"cassandra.yaml", "/home/ubuntu/cassandra/conf/")
    put(BASEP+"log4j-server.properties", "/home/ubuntu/cassandra/conf/")
        


def install_cassandra(group, update=False):
    if not exists("/home/ubuntu/cassandra"):
        sudo("apt-get install openjdk-7-jre-headless -y")
        run("wget http://mirrors.fe.up.pt/pub/apache/cassandra/2.0.6/apache-cassandra-2.0.6-bin.tar.gz")
        run("tar xvf apache-cassandra-2.0.6-bin.tar.gz")
        run("mv apache-cassandra-2.0.6 cassandra")
        update_cassandra(group)
    else:
        if update:
            update_cassandra(group)

def update_collectd():
    put(BASEC + "collectd.conf")
    sudo("mv collectd.conf /etc/collectd.conf")
    sudo("service collectd restart")

def install_collectd(update=False):
    if not update:
        sudo("apt-get install collectd -y")
        update_collectd()
    else:
        update_collectd()


def install_base(group, update=False):
    configure_nameserver()
    install_collectd(update)


def install_rabbit():
    sudo("apt-get install erlang -y")
    sudo("apt-get install -f -y")
    run("wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.2.4/rabbitmq-server_3.2.4-1_all.deb")
    sudo("dpkg -i rabbitmq-server_3.2.4-1_all.deb")


def install_postgres(update):
    pass

def update_postgres(group, update=False):
    pass


def configure_nameserver():
    sudo("apt-get remove resolvconf -y")
    put(BASEC + "resolv.conf", "/etc/resolv.conf", use_sudo=True)
    

def tsstore(update=False):
    if update:
        print " ==== Will now update tsstore. ==== "
    group = "tsstore"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, update)
        install_cassandra(group, update)
        install_supervisor(group, update)

def rabbit(update=False):
    #TODO
    THIS_IS_INCOMPLETE
    if update:
        print " ==== Will now update rabbit. ==== "
    group = "rabbit"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, update)
        install_rabbit()

def opstore(update=False):
    #TODO
    THIS_IS_INCOMPLETE
    if update:
        print " ==== Will now update opstore. ==== "
    group = "opstore"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, update)
        install_postgres(group, update)

def install(group):
    print group
    env.hosts = INV[group]
