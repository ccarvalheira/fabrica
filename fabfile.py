from __future__ import with_statement

import random
import string
import StringIO

from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import sudo

from fabric.operations import put

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from inventory import INV

_BASEP = "/home/ubuntu/fabrica/fabrica/"
BASEC = _BASEP + "conf/"

def get_basep(group):
    return _BASEP + group + "/"


def install_pip():
    sudo("apt-get install python-pip -y")


#supervisor
def update_supervisor(group):
    BASEP = get_basep(group)
    put(BASEP + "supervisord.conf", "/home/ubuntu/supervisor/")
    put(BASEC + "upstart_supervisor.conf", "/etc/init/supervisor.conf", use_sudo=True)
    sudo("service supervisor restart")
    run("supervisorctl -c /home/ubuntu/supervisor/supervisord.conf reload")


def install_supervisor(group, update=True):
    if not exists("/home/ubuntu/supervisor"):
        install_pip()
        sudo("pip install supervisor")
        run("mkdir -p supervisor/log")
        update_supervisor(group)
    else:
        if update:
            update_supervisor(group)
###

#cassandra
def update_cassandra(group):
    BASEP = get_basep(group)
    con = {}
    con["listen_addr"] = env.hosts[0].split("@")[1]
    con["seed_ips"] = INV["seed_ips"]
    upload_template(filename=BASEP+"cassandra.yaml", destination="/home/ubuntu/cassandra/conf/cassandra.yaml", context=con, backup=False)
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
###



#collectd
def update_collectd():
    upload_template(filename=BASEC + "collectd.conf", destination="/etc/collectd.conf", context = INV, backup=False, use_sudo=True)
    sudo("service collectd restart")

def install_collectd(update=False):
    if not update:
        sudo("apt-get install collectd -y")
        update_collectd()
    else:
        update_collectd()
####

#base config
def install_base(group, update=False):
    #TODO
    #activate this in production
    #takes up too much space in dev
    #sudo("apt-get upgrade -y")
    install_collectd(update)
###



#opstore and triple store
def update_postgres(group, slave):
    BASEP = get_basep(group)
    put(BASEP+"postgresql.conf", "/etc/postgresql/9.1/main/", use_sudo=True)
    put(BASEP+"pg_hba.conf", "/etc/postgresql/9.1/main/", use_sudo=True)
    
    if not slave:
        put(BASEP+"create_db.sql", "/home/ubuntu/")
        with cd("/home/ubuntu/"):
            sudo("sudo -u postgres psql --file=create_db.sql")
        
    if slave:
        put(BASEP+"create_slave.sql", "/home/ubuntu/")
        with cd("/home/ubuntu/"):
            sudo("sudo -u postgres psql --file=create_slave.sql")
        
        sudo("service postgresql stop")
        
        master_ip = INV[group+"_master"]
        sudo("sudo -u postgres rm -rf /var/lib/postgresql/9.1/main")
        sudo("sudo -u postgres pg_basebackup -h %s -D /var/lib/postgresql/9.1/main -U repl -v -P" % (master_ip,))
        sudo("""sudo -u postgres bash -c "cat > /var/lib/postgresql/9.1/main/recovery.conf <<- _EOF1_
  standby_mode = 'on'
  primary_conninfo = 'host=%s port=5432 user=repl password=repl'
  trigger_file = '/tmp/postgresql.trigger'
_EOF1_"
""" % (master_ip,)) 

    sudo("service postgresql restart")

def install_postgres(group, slave):
    sudo("apt-get install postgresql -y")
    update_postgres(group, slave)
###


#haproxy
def generate_nodes(nodes):
    stri = ""
    for n in nodes:    
        stri += "\n\tserver %s %s check inter 10000" % ("s"+n,n)
    return stri
    
def generate_ha_cassandra_nodes(nodes):
    stri = "listen cassandra-nodes 0.0.0.0:9042\n\tmode tcp\n\toption tcplog\n\tbalance leastconn\n"
    return stri+generate_nodes(nodes)
    
def generate_ha_gearman_nodes(nodes):
    stri = "listen gearmanjob-nodes 0.0.0.0:4730\n\tmode tcp\n\toption tcplog\n\tbalance leastconn\n"
    return stri+generate_nodes(nodes)

def generate_ha_api_nodes(nodes):
    stri = "listen api-nodes 0.0.0.0:8001\n\tmode tcp\n\toption tcplog\n\tbalance leastconn\n"
    return stri+generate_nodes(nodes)

def create_ha_config(group):
    cassandra_nodes = INV["cassandra_nodes"]
    gearmanjob_nodes = INV["gearmanjob_nodes"]
    api_nodes = INV["api_nodes"]
    
    cassandra_conf = generate_ha_cassandra_nodes(cassandra_nodes)
    gearman_conf = generate_ha_gearman_nodes(gearmanjob_nodes)
    api_conf = generate_ha_api_nodes(api_nodes)
    
    f = open(BASEC+"haproxy.cfg", "r")
    text = f.read()
    f.close()
    if group == "api":
        text = text % {"cassandra_nodes_config": cassandra_conf, "gearmanjob_nodes_config":gearman_conf, "api_nodes_config":""}
    elif group == "workers":
        text = text % {"cassandra_nodes_config": cassandra_conf, "gearmanjob_nodes_config":"", "api_nodes_config": api_conf}
        
    return text

    
    
def update_haproxy(group):
    
    main_config = create_ha_config(group)
    
    config = StringIO.StringIO(main_config)
    
    put(config, "/etc/haproxy/haproxy.cfg", use_sudo=True)
    
    config.close()
    
    sudo("service haproxy restart")
    
    
    
def install_haproxy(group, update):
    sudo("apt-get install haproxy")
    put(BASEC+"default_haproxy.conf", "/etc/default/haproxy", use_sudo=True)
    update_haproxy(group)
###


#api
def update_api_config(group):
    BASEP = get_basep(group)
    put(BASEP+".env", "/home/ubuntu/wsep/wsep/.env")
    update_haproxy(group)
    

def install_api(group, update):
    if not update:
        sudo("apt-get install python-dev python-virtualenv build-essential git-core libpq-dev libxml2-dev libxslt1-dev -y")
        if not exists("wsep"):
            run("mkdir wsep")
        with cd("wsep"):
            if not exists("env"):
                run("virtualenv env")
            if not exists("wsep"):
                run("git clone https://ccarvalheira@bitbucket.org/ccarvalheira/wsep.git")
            run(". env/bin/activate && pip install -r wsep/requirements.txt")
        install_haproxy(group, update)
    else:
        with cd("/home/ubuntu/wsep/wsep/"):
            run("git pull")
            run(". ../env/bin/activate && pip install -r requirements.txt")
    update_haproxy(group)
    update_api_config(group)
###


#nginx
def update_nginx(group):
    BASEP = get_basep(group)
    if exists("/etc/nginx/sites-enabled/default"):
        sudo("rm /etc/nginx/sites-enabled/default")
    put(BASEP+"api.conf", "/etc/nginx/sites-enabled/api.conf", use_sudo=True)
    sudo("service nginx restart")

def install_nginx(group, update):
    if not update:
        sudo("apt-get install nginx -y")
    update_nginx(group)    
###


#blob
def update_blobstore(group):
    BASEP = get_basep(group)
    put(BASEP+"btsync_blobstore.conf", "/etc/btsync/btsync_blobstore.conf", use_sudo=True)
    sudo("service btsync restart")
        
def install_blobstore(group, update=False):
    BASEP = get_basep(group)
    if not update:
        put(BASEP+"add-btsync-repository.sh", "/home/ubuntu/add-btsync-repository.sh")
        run('sh add-btsync-repository.sh')
        if not exists("fileserver"):
            run("mkdir fileserver")
        sudo("apt-get install btsync -y")
        if exists("/etc/btsync/debconf-default.conf"):
            sudo("rm /etc/btsync/debconf-default.conf")
    update_blobstore(group)
###


#pgpool
#backend_hostname0 = '192.168.200.2'
#backend_port0 = 5432
#backend_weight0 = 0
#backend_data_directory0 = '/var/lib/postgresql/9.1/main'
#backend_flag0 = 'ALLOW_TO_FAILOVER'
def render_pgpool_node(ip, count):
    stri = "\nbackend_hostname%s = '%s'" % (str(count), ip)
    stri += "\nbackend_port%s = 5432" % (str(count),)
    stri += "\nbackend_weight%s = 0" % (str(count),)
    stri += "\nbackend_data_directory%s = '/var/lib/postgresql/9.1/main'" % (str(count),)
    stri += "\nbackend_flag%s = 'ALLOW_TO_FAILOVER'\n\n" % (str(count),)
    return stri

def generate_pgpool_context(store):
    stri = ""

    master = INV[store+"_master"]
    slaves = INV[store+"_slaves"]

    for i, node in enumerate([master]+slaves):
        stri += render_pgpool_node(node, i)
    
    con = {}
    con["hostnames"] = stri
    return con
    

def update_pgpool(group):
    BASEP = get_basep(group)
    upload_template(filename=BASEP+"pgpool_opstore.conf", destination="/home/ubuntu/pgpool/pgpool_opstore.conf", context=generate_pgpool_context("opstore"), backup=False)
    
    upload_template(filename=BASEP+"pgpool_triplestore.conf", destination="/home/ubuntu/pgpool/pgpool_triplestore.conf", context=generate_pgpool_context("triplestore"), backup=False)
    
    
def install_pgpool(group, update):
    if not update:
        run("wget http://www.pgpool.net/download.php?f=pgpool-II-3.3.3.tar.gz")
        run("tar xvf download.php?f=pgpool-II-3.3.3.tar.gz")
        with cd("pgpool-II-3.3.3"):
            run("./configure")
            run("make")
            sudo("make install")
        with cd("/home/ubuntu/"):
            if not exists("pgpool"):
                run("mkdir pgpool")
            with cd("pgpool"):
                if not exists("opdir"):
                    run("mkdir opdir")
                if not exists("tripledir"):
                    run("mkdir tripledir")
    update_pgpool(group)
###


#wsgear
def update_wsgear_config(group):
    BASEP = get_basep(group)
    con = {}
    con["server_list"] = INV["gearmanjob_nodes"]
    upload_template(filename=BASEP+"gearman_servers.py", destination="/home/ubuntu/ws_gear/ws_gear/gearman_servers.py", context=con, backup=False)


def install_wsgear(group, update):
    if not update:
        sudo("apt-get install python-dev python-virtualenv git-core -y")
        if not exists("ws_gear"):
            run("mkdir ws_gear")
        with cd("ws_gear"):
            if not exists("env"):
                run("virtualenv env")
            if not exists("ws_gear"):
                run("git clone https://ccarvalheira@bitbucket.org/ccarvalheira/ws_gear.git")
            run(". env/bin/activate && pip install -r ws_gear/requirements.txt")
        install_haproxy(group, update)
    else:
        with cd("/home/ubuntu/ws_gear/ws_gear/"):
            run("git pull")
            run(". ../env/bin/activate && pip install -r requirements.txt")
    update_haproxy(group)   
    update_wsgear_config(group)
###



#done
def tsstore(update=False):
    if update:
        print " ==== Will now update tsstore. ==== "
    else:
        print " ==== Will now install tsstore. ===="
    group = "tsstore"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, update)
        install_cassandra(group, update)
        install_supervisor(group, update)

#done
def opstore(slave=False, group="opstore"):
    if not slave:
        print " ==== Will now install %s master. ==== " % group
    else:
        print " ==== Will now install %s slave. ====" % group
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, False)
        install_postgres(group, slave)

#done
def triplestore(slave=False, group="triplestore"):
    opstore(slave, group)


#done
def gearmanjob(update=False):
    if not update:
        print " ==== Will now install gearman jobserver. ==== "
    else:
        print " ==== Will now update gearman jobserver. ===="
    group = "gearmanjobserver"
    with cd("/home/ubuntu/"):
        sudo("add-apt-repository ppa:gearman-developers/ppa")
        sudo("apt-get update")
        install_base(group, update)
        sudo("apt-get install gearman-job-server gearman-tools -y")
        sudo("service gearman-job-server stop")
        BASEP = get_basep(group)
        put(BASEP+"gearman-job-server", "/etc/init.d/gearman-job-server", use_sudo=True)
        sudo("chown root /etc/init.d/gearman-job-server")
        sudo("chmod +x /etc/init.d/gearman-job-server")
        sudo("sudo /etc/init.d/gearman-job-server start")



#TODO
#needs testing
def api(update=False):
    if update:
        print " ==== Will now update api. ==== "
    else:
        print " ==== Will now install api. ===="
    group = "api"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")
        install_base(group, update)
        install_api(group, update)
        install_haproxy(group, update)
        install_blobstore(group, update)
        install_nginx(group, update)
        
        install_pgpool(group, update)
        #goes here because supervisord.conf has pgpool-related config
        install_supervisor(group, update)

#TODO
#falta testar
def workers(update=False):
    if update:
        print " ==== Will now update api. ==== "
    else:
        print " ==== Will now install api. ===="
    group = "workers"
    with cd("/home/ubuntu/"):
        sudo("apt-get update")    
        install_base(group, update)
        install_wsgear(group, update)
        install_haproxy(group, update)
        install_supervisor(group, update)
        
        
        
        
        
        
        
        
        
        
        
        
