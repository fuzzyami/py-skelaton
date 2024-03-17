from datetime import datetime

import k8s_api
from src.policies import get_policy
import pymongo
from utils import parse_json

client = pymongo.MongoClient('localhost', 27017, username='root', password='example')
db = client['autoscaler']
collection = db['deployments']


def calc_average_cpu_for_deployment(namespace, deployment_name):
    # get all the pods for this deployment
    pod_ids_by_namespace_and_deployment = k8s_api.get_pod_ids_by_namespace_and_deployment(namespace, deployment_name)

    total_cpu = 0
    for pod_id in pod_ids_by_namespace_and_deployment:
        pod = k8s_api.get_pod_metric(namespace, pod_id)
        total_cpu_raw = pod['containers'][0]['usage']['cpu']
        # get rid of the 'n' at the end
        total_cpu += int(total_cpu_raw[:-1])
    return total_cpu / len(pod_ids_by_namespace_and_deployment)


def get_deployments():
    # get the list of namespaces from k8s
    namespaces_items = k8s_api.get_namespaces()['items']
    raw_deployments_items = []
    api_deployments_items = []
    for item in namespaces_items:
        namespace = item['metadata']['name']
        raw_deployments_items.append(k8s_api.get_deployments(namespace))

    for deployments in raw_deployments_items:
        for deployment in deployments['items']:
            deployment_name = deployment['metadata']['name']
            namespace = deployment['metadata']['namespace']
            replicas = deployment['spec']['replicas']

            # get the average cpu for this deployment
            average_cpu = calc_average_cpu_for_deployment(namespace, deployment_name)
            api_deployments_item = {"name": deployment_name, "namespace": namespace, "replicas": replicas,
                                    "average_cpu": average_cpu}

            # get the policy for this deployment
            # there can be only one, at most, policy for a deployment
            policy = get_policy(namespace, deployment_name)
            if policy:
                if '_id' in policy:
                    policy.pop('_id', None)
                api_deployments_item['policy'] = policy

            api_deployments_items.append(api_deployments_item)

    return api_deployments_items


def should_trigger_scale_up(deployment_data, scale_up_data, stabilization_window_seconds, curr_replicas, max_replicas):
    # if inside stabilization window, don't scale
    if (datetime.now() - deployment_data['last_scale_event_ts']).seconds < stabilization_window_seconds:
        print('scale up: inside stabilization window, deployment:{}'.format(deployment_data['name']))
        return False
    # if we're already at max replicas, don't scale
    if curr_replicas >= max_replicas:
        print('scale up: max replicas reached, deployment:{}'.format(deployment_data['name']))
        return False

    if deployment_data['secs_above_up_threshold'] >= scale_up_data['periodSeconds']:
        print('scale up: period seconds reached, deployment:{}'.format(deployment_data['name']))
        return True
    else:
        print('scale up: period seconds not reached, deployment:{}'.format(deployment_data['name']))
        return False


def should_trigger_scale_down(deployment_data, scale_down_data, stabilization_window_seconds, curr_replicas,
                              min_replicas):
    # if inside stabilization window, don't scale
    if (datetime.now() - deployment_data['last_scale_event_ts']).seconds < stabilization_window_seconds:
        print('scale up: inside stabilization window, deployment:{}'.format(deployment_data['name']))
        return False
    # if we're already at min replicas, don't scale
    if curr_replicas <= min_replicas:
        print('scale down: min replicas reached, deployment:{}'.format(deployment_data['name']))
        return False

    if deployment_data['secs_below_down_threshold'] >= scale_down_data['periodSeconds']:
        print('scale down: period seconds reached, deployment:{}'.format(deployment_data['name']))
        return True
    else:
        print('scale down: period seconds not reached, deployment:{}'.format(deployment_data['name']))
        return False


def uphold_auto_scale_logic(deployment_object):
    # current data
    average_cpu = deployment_object['average_cpu']
    curr_replicas = deployment_object['replicas']
    namespace = deployment_object['namespace']
    deployment_name = deployment_object['name']
    stabilization_period_seconds = deployment_object['policy']['stabilizationPeriodSeconds']

    # get previous data for this deployment
    previous_data = collection.find_one({"name": deployment_name, "namespace": namespace})
    if not previous_data:
        previous_data = {"name": deployment_name,
                         "namespace": namespace,
                         # new deployment starts at stabilization window
                         "last_scale_event_ts": datetime.now(),
                         "secs_above_up_threshold": 0,
                         "secs_below_up_threshold": 0,
                         "secs_above_down_threshold": 0,
                         "secs_below_down_threshold": 0}

    # get the policy fields
    scale_up_data = deployment_object['policy']['scaleUp']
    scale_down_data = deployment_object['policy']['scaleDown']
    max_replicas = deployment_object['policy']['maxReplicas']
    min_replicas = deployment_object['policy']['minReplicas']

    if average_cpu >= scale_up_data['cpuPercentage']:
        previous_data['secs_above_up_threshold'] += 1
        previous_data['secs_below_up_threshold'] = 0

    if average_cpu < scale_down_data['cpuPercentage']:
        previous_data['secs_below_down_threshold'] += 1
        previous_data['secs_above_down_threshold'] = 0

    triggered_auto_scaling = False

    if should_trigger_scale_up(previous_data, scale_up_data, stabilization_period_seconds, curr_replicas, max_replicas):
        print('triggering scale up! (deployment:{} was: {})'.format(deployment_name,curr_replicas))
        k8s_api.put_deployment_scale(namespace, deployment_name, curr_replicas + 1)
        triggered_auto_scaling = True


    elif should_trigger_scale_down(previous_data, scale_down_data, stabilization_period_seconds, curr_replicas,
                                   min_replicas):
        print('triggering scale down! (deployment:{} was: {})'.format(deployment_name, curr_replicas))
        # check that we're not already at the min replicas
        k8s_api.put_deployment_scale(namespace, deployment_name, curr_replicas - 1)

    if triggered_auto_scaling:
        # reset the thresholds
        previous_data['secs_above_up_threshold'] = 0
        previous_data['secs_below_up_threshold'] = 0
        previous_data['secs_below_down_threshold'] = 0
        previous_data['secs_above_down_threshold'] = 0
        previous_data['last_scale_event_ts'] = datetime.now()

    # save the data to the db
    collection.replace_one({"name": deployment_name, "namespace": namespace}, previous_data, upsert=True)
