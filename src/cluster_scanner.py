import k8s_api
from deployments import get_deployments, uphold_auto_scale_logic
from src.policies import get_policy


def scan_cluster():

    # get deployments from k8s
    deployments = get_deployments()

    for deployment in deployments:
        # get the policy for this deployment
        if not 'policy' in deployment:
            # no policy for this deployment, nothing really to do and no point in saving the data
            print('no policy for this deployment: ', deployment['name'])
            continue
        else:
            uphold_auto_scale_logic(deployment)



