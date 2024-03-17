k8s_mock_url = "http://localhost:8080"
import requests


def get_namespaces():
    # get the list of namespaces from k8s
    get_namespaces_url = f"{k8s_mock_url}/api/v1/namespaces"
    response = requests.get(get_namespaces_url)
    return response.json()


def get_pods(namespace):
    # get the list of pods from k8s
    get_pods_url = f"{k8s_mock_url}/api/v1/namespaces/{namespace}/pods"
    response = requests.get(get_pods_url)
    return response.json()

def get_pod_ids_by_namespace_and_deployment(namespace, deployment):
    # get all the pods for this namespace
    pods_for_namespace = get_pods(namespace)

    # filter only the pods for this deployment
    pods_for_deployment = [pod for pod in pods_for_namespace['items'] if
                           pod['metadata']['name'].startswith(deployment)]
    # return the list of pod ids
    return [pod['metadata']['name'] for pod in pods_for_deployment]


def get_pod(namespace, pod_name):
    # get the pod from k8s
    get_pod_url = f"{k8s_mock_url}/apis/apps/v1/namespaces/{namespace}/pods/{pod_name}"
    response = requests.get(get_pod_url)
    return response.json()


def get_deployments(namespace):
    # get the list of deployments from k8s
    get_deployments_url = f"{k8s_mock_url}/apis/apps/v1/namespaces/{namespace}/deployments"
    response = requests.get(get_deployments_url)
    return response.json()


def get_deployment(namespace, deployment_name):
    # get the deployment from k8s
    get_deployment_url = f"{k8s_mock_url}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}"
    response = requests.get(get_deployment_url)
    return response.json()


def get_deployment_scale(namespace, deployment_name):
    # get the deployment scale from k8s
    get_deployment_scale_url = f"{k8s_mock_url}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}/scale"
    response = requests.get(get_deployment_scale_url)
    return response.json()


def put_deployment_scale(namespace, deployment_name, replicas):
    # scale the deployment
    deployment_scale_url = f"{k8s_mock_url}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}/scale"
    data = {
        "kind": "Scale",
        "apiVersion": "autoscaling/v1",
        "spec": {
            "replicas": replicas
        }
    }
    response = requests.put(deployment_scale_url, json=data)
    return response.json()

def get_pod_metric(namespace, pod_name):
    # get the pod metrics from k8s
    get_pod_metric_url = f"{k8s_mock_url}/apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods/{pod_name}"
    response = requests.get(get_pod_metric_url)
    return response.json()