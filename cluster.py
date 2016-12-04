#! /usr/bin/python
import os, MySQLdb,subprocess,random,simplejson
import json, time
from mod_python import util,Cookie,apache
def index():
	return "hello"
def map_conf(new_conf_file, tmp_file, params):
	lines, contents = [], []
	with open(tmp_file) as inf:
		lines = inf.readlines()


        #raise Exception(tmp_file)
        #if tmp_file == "/var/www/mcgk/templates/config":
	#	params["recov_method"] = "#"+params["recov_method"]	
	for cont in lines:
		contents.append(cont.strip())
	
	contents = "\n".join(contents)

 	#raise Exception(contents)		
	newcontents = contents % params

	with open(new_conf_file, "w") as outf:
		outf.write(newcontents)	

def redirect(url,req):
	  util.redirect(req,  url)

def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

def execute(command, silent=False, wait=True, stdout=False):
	PIPE = subprocess.PIPE
	p = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
	if wait:
		p.wait()

	if(not silent):
		st = p.stderr.read()
		if(len(st) > 0):
		   raise Exception("ERR: " + st)
	
        if(stdout):
		return p.stdout.read()


def upload_file(file_object, filename, tmp_dir=""):
    #path="/var/www/mcgk/tmp/"
    path = "/tmp/"	 
    if tmp_dir != "" and os.path.exists(os.path.join(path, tmp_dir)):
        path = os.path.join(path, tmp_dir)
        fpath=os.path.join(path,filename)
        #raise Exception(file_object.file.read)
        f = open(fpath, 'wb', 10000)
        # Read the file in chunks
        for chunk in fbuffer(file_object.file):
        	f.write(chunk)
        f.close()
        
        return fpath
		
    while 1:  
	if tmp_dir == "":
		rand=random.randint(1,1000000000000)
	else:
		rand=tmp_dir	
	if not os.path.exists(path+"%s"%rand):
		path=path+str(rand)
		os.mkdir(path)
		#break
				
         #fname = os.path.basename(fileitem.filename)
        fpath=os.path.join(path,filename)
        #raise Exception(fpath)
        f = open(fpath, 'wb', 10000)
        # Read the file in chunks
        for chunk in fbuffer(file_object.file):
        	f.write(chunk)
        f.close()
        
	return fpath, str(rand)
        	
def readParamsFromFile(id):
	#info_path = "/var/www/mcgk/tmp/{0}/cluster.json".format(id)
	info_path = "/tmp/{0}/cluster.json".format(id)
	
	params = {}
	with open(info_path) as inf:
		params = json.load(inf)
	
	return params	
        	

def readparams(req):
	params = {}
	
	#raise Exception(req.form["aws_keypair"].file)
	params["cluster_name"] = req.form["cluster_name"]
	params["cluster_size"] = req.form["cluster_size"]
	params["node_instance_type"] = req.form["node_instance_type"]
	params["master_instance_type"] = req.form["master_instance_type"]
	params["node_image_id"] = req.form["node_image_id"]
	
	params["instance_type"] = req.form["instance_type"]
	if params["instance_type"] == "spot":
		params["spot_bid"] = "SPOT_BID = " + req.form["spot_bid"]
	else:
		params["spot_bid"] = "#SPOT_BID = "	+ "NA"
	
	params["aws_ak"] = req.form["aws_access_key"]
	params["aws_sk"] = req.form["aws_secret_key"]
	params["aws_uid"] = req.form["aws_uid"]


	#raise Exception(req.FILES["filename"])
	filename = req.form["filename"].split("\\")[-1]
	#raise Exception(filename)
	params["aws_keypair"], tmp_dir = upload_file(req.form["aws_keypair"], filename)
	params["keyname"] = filename.split('.')[0]
	
	file_object = params["aws_keypair"]
	params["gce_cluster_conf"] = upload_file(req.form["gce_cluster_conf"], "cluster.conf", tmp_dir)
        params["gce_oauth2"] = upload_file(req.form["gce_oauth2"], "oauth2.dat", tmp_dir)
	
	params["recovery"] = req.form["recov_method"]
	params["wfname"] = req.form["wfname"]
	
	params["input_src"] = req.form["input_src"]
	if params["input_src"] == "public":
		params["s3_link"] = req.form["s3_link"]
		params["s3_object"] = ""
		params["s3_in_bucket"] = ""
	else:
		params["s3_link"] = ""
		params["s3_object"] = req.form["s3_object"]
		params["s3_in_bucket"] = req.form["s3_in_bucket"]
	
	params["out_bucket"] = req.form["s3_out_bucket"]
	params["out_dir"] = req.form["out_dir"]

	return params


def launch_cosmos_web(id, domain):
	params = {}
	with open("/tmp/{0}/cluster.json".format(id)) as fh: 
		params = json.load(fh)

        #cmd = "ssh -i {0} -o StrictHostKeyChecking=no ehpcuser@{1} cd /home/ehpcuser/Cosmos-master && sudo python setup install".f
	os.system("chmod 600 {0}".format(params["aws_keypair"]))
	cosmos_cmd = "/home/ehpcuser/cosmos_script.sh"
	cmd = "ssh -i {0} -o StrictHostKeyChecking=no ehpcuser@{1} \"{2}\" &".format(params["aws_keypair"], domain, cosmos_cmd)
	#raise Exception(cmd)
	execute(cmd, silent=True, wait=False)

	#fix_cmd = "/home/ehpcuser/fix_script.sh"
	#execute("ssh -i {0} -o StrictHostKeyChecking=no ehpcuser@{1} \"{2}\" &".format(params["aws_keypair"], domain, cosmos_cmd), silent=True, wait=False)

	time.sleep(5)

def start(req):
    #raise Exception("haha")

    params = readparams(req)
    #raise Exception("haha")
    working_dir = os.path.dirname(params["aws_keypair"])
    rand = working_dir.split("/")[-1]
	
    os.chdir(os.path.join("/tmp", rand))    

    cluster_config_template = "/var/www/mcgk/templates/config"
    job_conf_template = "/var/www/mcgk/templates/job_conf.conf"
    
    map_conf(os.path.join(working_dir, "newconfig"), cluster_config_template, params)
    map_conf(os.path.join(working_dir, "job_conf.conf"), job_conf_template, params)        

    cluster_info = os.path.join(working_dir, "cluster.json")
    with open(cluster_info, "w") as info:
       json.dump(params, info)
	
    create_log = os.path.join(working_dir, "starcluster.log")
    open(create_log, 'a').close()

    new_config = os.path.join(working_dir, "newconfig")
    create_cluster = "starcluster --config={0} start {1} | tee -a {2}".format(new_config, params["cluster_name"], create_log)
    #raise Exception(create_cluster)
    #execute("sudo chmod -R 700 {0}".format(working_dir), wait=False, silent=True)
    execute(create_cluster, wait=False, silent=True, stdout=False)

    redirect("../../details.html?rand=%s"%rand, req)


def getStatus(id, file="starcluster.log"):
	st=""
	#return "INFO -- CLUSTER1 is Created Successfully: ec2-54-153-93-18.us-west-1.compute.amazonaws.com"
	#f=open("/var/www/mcgk/tmp/{0}/{1}".format(id, file))
	f=open("/tmp/{0}/{1}".format(id, file))
	for line in f.readlines():
		st=line+st
	f.close()
	return st
	#return f.readlines()

def get_ehpc_status(req):
	id = req.form["id"]
	#wd_dir = "/var/www/mcgk/tmp/{0}/status.log".format(id)
        wd_dir = "/tmp/{0}/status.log".format(id)
	if not os.path.exists(wd_dir):
		return "false"
	f=open(wd_dir)
	st = ""
	for line in f.readlines():
		st=line+st
	f.close()
	
	return st	
	
def get_mcgk_Status(id, file="mcgk.log"):
	st=getStatus(id)
	#raise Exception(st)
	#return "INFO -- CLUSTER1 is Created Successfully: ec2-54-153-93-18.us-west-1.compute.amazonaws.com"
	#f=open("/var/www/mcgk/tmp/{0}/{1}".format(id, file))
	if not os.path.exists("/tmp/{0}/{1}".format(id, file)):
		time.sleep(5)
	f=open("/tmp/{0}/{1}".format(id, file))
	for line in f.readlines():
		st=line+st
	f.close()
	return st	

def launch_mcgk(id):
	#raise Exception(id)
	mcgk_path = "/var/www/mcgk/mcGenomekey-0.1.1/mcgenomekey"
	params = readParamsFromFile(id)
	
	mcgk_cmd = "{0} start -d {1} --keypair {2} --job_conf {3} --tmp_dir {4} &".format(mcgk_path, params["aws_domain"], params["aws_keypair"], "job_conf.conf", "/tmp/{0}".format(id))
	
	#raise Exception(mcgk_cmd)
	#os.system("chmod -R 777 {0}".format(os.path.join("/tmp", id)))
	execute(mcgk_cmd, silent=True, stdout=False, wait=False)
	#raise Exception()

def hello(req):
	#raise Exception(req.form)
	gce_upload(req)

def gce_upload(req):
    #raise Exception(req.form)
    gce_conf = req.form["gce_conf"]
    gce_oauth = req.form["gce_oauth"]
    tmp_dir = req.form["hidden_param"]
	
    gce_conf_path = upload_file(gce_conf, "cluster.conf", tmp_dir)
    gce_oauth_path = upload_file(gce_oauth, "oauth2.dat", tmp_dir)

    if os.path.dirname(gce_conf_path) == os.path.dirname(gce_oauth_path):
       redirect("../../details.html?rand=%s"%tmp_dir, req)
    return 0

def check_gce_conf(req):
	tmp_dir = req.form["id"]
	#tmp_dir = os.path.join("/var/www/mcgk/tmp", tmp_dir)
	tmp_dir = os.path.join("/tmp", tmp_dir)	

	gce_conf = os.path.join(tmp_dir, "cluster.conf")
	gce_oauth = os.path.join(tmp_dir, "oauth2.dat")
	
	return os.path.exists(gce_conf) and os.path.exists(gce_oauth)

def saveCluster(tmp_dir_id, aws_domain, req):
	#raise Exception(tmp_dir_id)
	#tmp_dir_id = tmp_dir_id.split("aws_domain")
	#aws_domain = tmp_dir_id.split["aws_domain"][-1]
	#return True
	#working_dir = os.path.join("/var/www/mcgk/tmp", str(tmp_dir_id))
	working_dir = os.path.join("/tmp", str(tmp_dir_id))
	cluster_info_file = os.path.join(working_dir, 'cluster.json')
	
	with open(cluster_info_file) as info_file:
		params = json.load(info_file)
	
	params["aws_domain"] = aws_domain
	#raise Exception(params)
	with open(cluster_info_file, "w") as info:
		json.dump(params, info)

	return True
