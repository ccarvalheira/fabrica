
INV = {
	#"tsstore": ["ec2-user@192.168.186.191"],
	#"rabbit": ["ec2-user@192.168.186.189"],
	"metric_ip": "192.168.149.161",
	"seed_ips": "192.168.149.167", #csv ex: "10.0.3.54,10.0.3.55"
	
	#"opstore_subnet": "10.0.3.0/24",
	#"triplestore_subnet": "10.0.3.0/24",
	
	
	"opstore_master": "192.168.149.162",
	
	"opstore_slaves": ["192.168.149.163",],
	
	"triplestore_master": "192.168.149.164",
	
	"triplestore_slaves": ["192.168.149.165",],

	
	"cassandra_nodes": ["192.168.149.167","192.168.149.174"],
	
	"gearmanjob_nodes": ["192.168.149.166"],
	
	"api_nodes": ["192.168.149.168", "192.168.149.173", "192.168.149.175"],

}
