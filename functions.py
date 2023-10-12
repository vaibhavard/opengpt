import re
import helpers.helper as helper
import base64
import requests
import json

import os


def mm(graph): 
    graph=graph.replace("mermaid","")
    graph=graph.replace("markdown","")

    pattern = r"```(.+?)```"
    match = re.search(pattern, graph, flags=re.DOTALL)
    if match: 
        graph = match.group(1)
        print(graph)
    else: 
        print("No match found")
        return "Error.Try Again."
    graphbytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    r = requests.get("https://mermaid.ink/img/" + base64_string)
    if "invalid encoded" in r.text or  "Not Found" in r.text:
       return "ERROR in encoding123" 
    else:
      return "![]"+"("+"https://mermaid.ink/img/" + base64_string+")"

def extract_links(text):
    # Regular expression pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Find all matches of the URL pattern in the text
    urls = re.findall(url_pattern, text)
    return urls

def allocate(messages,data,uploaded_image,processed_text,systemp,model):
    python_boolean_to_json = {
      "true": True,
    }


    helper.data['message']= messages[-1]['content']
    if "Knowledge cutoff" in messages[0]["content"]:   
      helper.data["systemMessage"]=helper.gpt4mod
    elif model!='gpt-4-local':
      helper.data["systemMessage"]=messages[0]["content"]
    else:
      helper.data["systemMessage"]=helper.nogpt 

        

    links = extract_links(data['message'])
    if links!= [] and "/image" in data['message']:
      print(links[0])
      helper.data["imageURL"]=links[0]
      print(helper.data["imageURL"])

    elif uploaded_image!="":
      helper.data["imageURL"]=uploaded_image
      print("-"*100)
      print(helper.data["imageURL"])

    elif processed_text !="":
      helper.data['jailbreakConversationId']: json.dumps(python_boolean_to_json['false'])
      try:
         del helper.data['jailbreakConversationId']
      except:
         pass
      helper.data["context"]=processed_text

    return helper.data

def check(api_endpoint):
    try:
        xx = requests.get(api_endpoint.replace("/conversation",""),timeout=15)
        return "" 
    except :
        return "gpt-3"
        pass

def ask(query,prompt,api_endpoint,output={}):
  if output=={}:
    python_boolean_to_json = {
      "true": True,
    }
    data = {
        'jailbreakConversationId': json.dumps(python_boolean_to_json['true']),
        "systemMessage":prompt,
        "message":query

    }
    resp=requests.post(api_endpoint, json=data) 
    return resp.json()["response"]
  else:
    resp=requests.post(api_endpoint, json=output) 
    return resp.json()

def clear():
  icon="()"
  del helper.data["systemMessage"]   


  try:
      del helper.data["message"]  
      icon=icon+"(history)"
  except:
      pass
  try:
      helper.processed_text=""
      del helper.data["context"]
      icon=icon+"(context)"
  except:
      pass
  try:
      os.environ['uploaded_image']=""
      del helper.data["imageBase64"]
      icon=icon+"(image)"

  except:
      pass
  try:
      del helper.data["imageURL"]
      icon=icon+"(imageurl)"
  except:
      pass
  return icon


