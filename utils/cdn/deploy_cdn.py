#!/usr/bin/python 

import docker 
import jsonpickle

# For each region specified in regions json/dict create one cdn server instance.
# Update regions json with the created server's ip and create cdn manager 
# with the updated json config. 
# Could not find soultion to handle build errors or stop the deploy process
# if error occur. docker_api.build(...) returns very odd stream_helper ...

regions =  {
		"eu": [
			{
				"ip":"session-cdn",
				"hls_port": 10000,
				"hc_port":10000,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		],
		"na": [
			{
				"ip":"session-cdn",
				"hls_port": 10000,
				"hc_port":10000,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		],
		"as": [
			{
				"ip":"session-cdn",
				"hls_port": 10000,
				"hc_port":10000,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		]
	}

regions =  {
		"eu": [
			{
				"ip":"session-cdn",
				"hls_port": 10000,
				"hc_port":10000,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		]
	}

NETWORK = "session-net"
# IP_SUBNET_PREFIX = "172.23.2."
BASE_RTMP_PORT = 11000
INNER_RTMP_PORT = 11000
BASE_HLS_PORT = 10000
INNER_HLS_PORT = 10000
# MEDIA_PATH = "live"

CDN_PREFIX = "session-cdn-"
CDN_LABEL = "cdn_instance"

# BUILD_CONTEXT = '../../'
CDN_IMAGE_TAG = 'session/cdn'
# CDN_DOCKERFILE = 'dockerfiles/cdn.Dockerfile'

MANAGER_IMAGE_TAG = 'session/cdn-manager'
# MANGER_DOCKERFILE = 'dockerfiles/cdn_manager.Dockerfile'
# MANAGER_CONFIG_PATH = '../../cdn_manager/src/app_config.json'
MANAGER_CONT_NAME = 'session-cdn-manager'
MANAGER_LABEL = 'cdn_manager'
MANAGER_API_PORT = 8004

# PRODUCTION_STAGE = 'prod'

dckr = docker.from_env()

old_cdns = dckr.containers.list(filters={"label": [CDN_LABEL, MANAGER_LABEL]}, all=True)

if len(old_cdns)>0:
	print("Some CDN instances are still running (or still not removed) ... ")
	print("Stop or remove them before proceeding  ... ")
	for c in old_cdns:
		print(f"{c.name} --> {c.status}")

	exit(1)

index=0
for region_key in regions:
	c_name = f"{CDN_PREFIX}{region_key}"
	out_hls_port = BASE_HLS_PORT + index
	out_rtmp_port = BASE_RTMP_PORT + index
	
	container = dckr.containers.run(image=CDN_IMAGE_TAG,
					   	detach=True,
						ports={
							INNER_HLS_PORT: ("0.0.0.0", out_hls_port),
							INNER_RTMP_PORT: ("0.0.0.0", out_rtmp_port)
						},
						network=NETWORK,
						name=c_name,
						labels=[CDN_LABEL],
						stop_signal="SIGINT")


	# Container obj returned from run() won't be populated with network attrs.
	container = dckr.containers.get(container.id)
	ip = container.attrs["NetworkSettings"]["Networks"][NETWORK]["IPAddress"]
	regions[region_key][0]["ip"] = ip
	# regions[region_key][0]["hls_port"] = BASE_HLS_PORT
	# regions[region_key][0]["hc_port"] = BASE_HLS_PORT
	# Tn this case hc server is hosted on the same http server as the hls server. 
	
	index = index+1

print("Deployed CDNs")
print(jsonpickle.encode(regions, unpicklable=False, indent=4))

config = jsonpickle.encode(regions,
						unpicklable=False, 
						separators=(",",":"))\
					.replace("\"","\\\"")

manager = dckr.containers.run(image=MANAGER_IMAGE_TAG,
					detach=True,
					ports={
						MANAGER_API_PORT: ("0.0.0.0", MANAGER_API_PORT)
					},
					network=NETWORK,
					name=MANAGER_CONT_NAME,
					labels=[MANAGER_LABEL],
					stop_signal='SIGINT',
					command=config)
# command represents cli arguments