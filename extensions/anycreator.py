import random
import urllib.request
import requests
import time
import urllib.request
data={}
imgur=[]
def getimage(query):

    payload = {
        "model": "absolutereality_v181.safetensors [3d9d4d2b]",
        "prompt": str(query)
    }

    response = requests.post("https://api.prodia.com/v1/sd/generate", json=payload, headers={"accept": "application/json","content-type": "application/json","X-Prodia-Key": "da6053eb-c352-4374-a459-2a9a5eaaa64b"})
    jobid=response.json()["job"]
    while True:
        response = requests.get(f"https://api.prodia.com/v1/job/{jobid}", headers={"accept": "application/json","X-Prodia-Key": "da6053eb-c352-4374-a459-2a9a5eaaa64b"})
        if response.json()["status"]=="succeeded":
            image=response.json()["imageUrl"]
            break
        time.sleep(0.5)

    filename=f"static/image{random.randint(1,1000)}.png"

    urllib.request.urlretrieve(image, filename)

    return filename



