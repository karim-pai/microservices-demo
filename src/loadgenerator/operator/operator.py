from kubernetes import client, config
import time
import asyncio
import random
import os

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "loadgenerator")
SEC_BETWEEN_CYCLES = os.getenv("SEC_BETWEEN_CYCLES", 3600)
SEC_CYCLE_MIN = os.getenv("SEC_CYCLE_MIN", 300)
SEC_CYCLE_MAX = os.getenv("SEC_CYCLE_MAX", 900)
SCALE = os.getenv("SCALE", 2)

def update_deployment(api, deployment, replicas):
    # Update container image
    print(f"Number of current replicas: {deployment.spec.replicas}")
    deployment.spec.replicas = replicas
    print(f"New number of replicas: {deployment.spec.replicas}")
    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )
    return resp

async def cycle(api):

    deployment = api.read_namespaced_deployment(name=DEPLOYMENT_NAME, namespace='default')
    replicas = deployment.spec.replicas
    update_deployment(api, deployment, replicas * SCALE)
    # time.sleep(random.randint(SEC_CYCLE_MIN,SEC_CYCLE_MAX))
    await asyncio.sleep(random.randint(SEC_CYCLE_MIN,SEC_CYCLE_MAX))
    deployment = api.read_namespaced_deployment(name=DEPLOYMENT_NAME, namespace='default')
    replicas = deployment.spec.replicas
    update_deployment(api, deployment, replicas // SCALE)



async def main():
    print("Get kube config")
    config.load_incluster_config()

    apps_v1 = client.AppsV1Api()

    sec_to_sleep = 60
    while True:
        await cycle(apps_v1)
        print(f"sleeping {sec_to_sleep} seconds")
        time.sleep(sec_to_sleep)

if __name__ == '__main__':
    asyncio.run(main())
