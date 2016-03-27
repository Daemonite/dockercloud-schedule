import functools
import schedule
import time
import dockercloud
import os

dockercloud.user = os.environ['DOCKERCLOUD_USER']
dockercloud.apikey = os.environ['DOCKERCLOUD_APIKEY']
nodecluster = os.environ['NODECLUSTER']

# format exceptions
def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
    return wrapper


"""
NODE CLUSTER JOBS
"""
@catch_exceptions
def start_cluster(uuid):
    nodecluster = dockercloud.NodeCluster.fetch(uuid)
    print("Starting %s...") % (nodecluster.name)
    waiting_for_start = 0
    # scale up cluster if its empty
    if nodecluster.state == "Empty cluster":
        nodecluster.target_num_nodes = 1
        nodecluster.save()
        # wait till cluster is deployed; give up after 15 minutes
        while nodecluster.state != "Deployed" and waiting_for_start < 900:
            time.sleep(30)
            waiting_for_start = waiting_for_start + 30
            nodecluster = dockercloud.NodeCluster.fetch(uuid)
            print("  waiting...%s") % (nodecluster.state)
        if nodecluster.state == "Deployed":
            # deploy cache-stage service; ~2mins
            redeploy_cache()
            time.sleep(120)
            # deploy stage stacks; ~3mins
            redeploy_stacks()
            time.sleep(180)
            # re-deploy haproxy-stage; ensures service endpoints registered
            redeploy_haproxy()
    else:
        print("  nothing to do...%s") % (nodecluster.state)


@catch_exceptions
def stop_cluster(uuid):
    nodecluster = dockercloud.NodeCluster.fetch(uuid)
    print("Stopping %s...") % (nodecluster.name)
    nodecluster.target_num_nodes = 0
    nodecluster.save()
    waiting_for_stop = 0
    # wait till cluster is deployed; give up after 15 minutes
    while nodecluster.state != "Empty cluster" and waiting_for_stop < 100:
        time.sleep(10)
        waiting_for_stop = waiting_for_stop + 10
        nodecluster = dockercloud.NodeCluster.fetch(uuid)
        print("  waiting...%s") % (nodecluster.state)


"""
NODE CLUSTER HELPERS
"""
@catch_exceptions
def redeploy_stacks():
    print("Re-deploying stage stacks...")
    stacks = dockercloud.Stack.list()
    # redeploy all stacks with stage in their name; eg. aoc-rio2016-stage
    for i in stacks:
        if "stage" in i.name:
            stack = dockercloud.Stack.fetch(i.uuid)
            stack.redeploy()
            print("  %s deployed") % (i.name)


@catch_exceptions
def redeploy_cache():
    print("Re-deploying cache-stage utilities...")
    services = dockercloud.Service.list()
    # redeploy cache-stage; memcached needs to be up first
    for i in services:
        if "cache-stage" in i.name:
            service = dockercloud.Service.fetch(i.uuid)
            service.redeploy()
            print("  %s deployed (%s)") % (i.name, i.stack)


@catch_exceptions
def redeploy_haproxy():
    print("Re-deploying haproxy-stage utilities...")
    services = dockercloud.Service.list()
    # redeploy haproxy-stage; ensures all services are registered
    for i in services:
        if "haproxy-stage" in i.name:
            service = dockercloud.Service.fetch(i.uuid)
            service.redeploy()
            print("  %s deployed (%s)") % (i.name, i.stack)


@catch_exceptions
def list_clusters():
    print("Getting node clusters...")
    nodeclusters = dockercloud.NodeCluster.list()
    for i in nodeclusters:
        print("  %s (%s)") % (i.name, i.state)
    return schedule.CancelJob


@catch_exceptions
def test_msg(msg):
    print("I'm working on %s with %s...") % (msg, nodecluster)
    

"""
NODE CLUSTER SCHEDULE
"""
# test runner
schedule.every(10).minutes.do(test_msg, "running")
# schedule.every(1).seconds.do(list_clusters)
# schedule.every(10).seconds.do(stop_cluster, nodecluster)
# schedule.every(10).seconds.do(start_cluster, nodecluster)

# start up cluster at 8am UTC
schedule.every().day.at("21:00").do(start_cluster, nodecluster)
schedule.every().day.at("21:15").do(redeploy_stacks)

# shut down cluster at 8pm UTC
schedule.every().day.at("9:00").do(stop_cluster, nodecluster)



"""
SCHEDULE DOES ITS THING
"""
while True:
    schedule.run_pending()
    time.sleep(1)