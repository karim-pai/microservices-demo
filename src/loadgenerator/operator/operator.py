from kubernetes import client, config
import time
import asyncio
import random
import os
import logging

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "loadgenerator")
SEC_BETWEEN_CYCLES = os.getenv("SEC_BETWEEN_CYCLES", 3600)
SEC_CYCLE_MIN = os.getenv("SEC_CYCLE_MIN", 300)
SEC_CYCLE_MAX = os.getenv("SEC_CYCLE_MAX", 900)
SCALE = os.getenv("SCALE", 5)

def update_deployment(api, deployment, replicas):
    # Update container image
    logging.info(f"Number of current replicas: {deployment.spec.replicas}")
    deployment.spec.replicas = replicas
    logging.info(f"New number of replicas: {deployment.spec.replicas}")
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
    duration = random.randint(SEC_CYCLE_MIN,SEC_CYCLE_MAX)
    logging.info(f"Abnormal step will last {duration} seconds")
    await asyncio.sleep(duration)
    deployment = api.read_namespaced_deployment(name=DEPLOYMENT_NAME, namespace='default')
    replicas = deployment.spec.replicas
    # update_deployment(api, deployment, max(1, replicas // SCALE))
    update_deployment(api, deployment, 1)



async def main():
    logging.info("Get kube config")
    config.load_incluster_config()

    apps_v1 = client.AppsV1Api()

    while True:
        logging.info(f"New cycle starts")
        await cycle(apps_v1)
        logging.info(f"sleeping {SEC_BETWEEN_CYCLES} seconds")
        time.sleep(SEC_BETWEEN_CYCLES)

if __name__ == '__main__':
    asyncio.run(main())
