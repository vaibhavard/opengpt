import re
import helpers.helper as helper
import base64
import requests
import json
from bs4 import BeautifulSoup
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

def allocate(messages,data,uploaded_image,processed_text,api_keys,model):
    python_boolean_to_json = {
      "true": True,
    }
    helper.data["plugins"]= {"search":False}
    helper.data["modelVersion"]=""
    helper.data['message']= messages[-1]['content']

    if model == "gpt-4-turbo-unstable":
      helper.data["modelVersion"]="gpt-4 turbo"
      helper.data["systemMessage"]="You are renamed to chatgpt , developed by openai"
      helper.data["message"]=""
      for message in messages:
            helper.data["message"]=helper.data["message"]+f"{message['content']}\n"

    if model == "gpt-4-turbo" :
      helper.data["modelVersion"]="gpt-4 turbo"

      try:
        cid=helper.m.get_data(str(api_keys))[f"{str(model)}_{messages[1]['content']}"]
        helper.data['parentMessageId'] = cid
      except:
        updated={**helper.m.get_data(str(api_keys)),**{f"{str(model)}_{messages[1]['content']}":""}}
        helper.m.update_data(str(api_keys),updated)
        helper.m.save()
        helper.data['parentMessageId'] = ""
    if model=="gpt-4-old":
      if "Knowledge cutoff" in messages[0]["content"]:
        helper.data["systemMessage"]=helper.gpt4mod
      else:
        helper.data["systemMessage"]=messages[0]["content"]

      try:
        cid=helper.m.get_data(str(api_keys))[f"{str(model)}_{messages[1]['content']}"]
        helper.data['parentMessageId'] = cid
      except:
        updated={**helper.m.get_data(str(api_keys)),**{f"{str(model)}_{messages[1]['content']}":""}}
        helper.m.update_data(str(api_keys),updated)
        helper.m.save()
        helper.data['parentMessageId'] = ""
    if model == "gpt-4-turbo-web":
      helper.data["modelVersion"]="gpt-4 turbo"
      helper.data["systemMessage"]="You are renamed to chatgpt , developed by openai"
      try:
        cid=helper.m.get_data(str(api_keys))[f"{str(model)}_{messages[1]['content']}"]
        helper.data['parentMessageId'] = cid
      except:
        updated={**helper.m.get_data(str(api_keys)),**{f"{str(model)}_{messages[1]['content']}":""}}
        helper.m.update_data(str(api_keys),updated)
        helper.m.save()
        helper.data['parentMessageId'] = ""
      helper.data["plugins"]= {"search":True}

    if model=="gpt-4-16k":
            
      helper.data["systemMessage"]= "".join(
            f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#additional_instructions)") + f"\n{message['content']}\n\n"
            for message in messages
        )
    if  model == "gpt-4-web" :   
      helper.data["systemMessage"]= "".join(
            f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#additional_instructions)") + f"\n{message['content']}\n\n"
            for message in messages
        )
      helper.data["plugins"]= {"search":True}


    if uploaded_image!="":
      helper.data["imageURL"]=uploaded_image
      print("-"*100)
      print(helper.data["imageURL"])

    if processed_text !="":
      try:
         del helper.data['jailbreakConversationId']
      except:
         pass
      helper.data["context"]=processed_text
    else:
      helper.data['jailbreakConversationId']= json.dumps(python_boolean_to_json['true'])


    return helper.data

def check(api_endpoint):
    try:
        requests.get(api_endpoint.replace("/conversation",""),timeout=15)
        return "" 
    except :
        return "gpt-3"

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
    print(resp)
    return resp.json()["response"]
  else:
    resp=requests.post(api_endpoint, json=output) 
    return resp.json()


def check_content(text, api_url, gfm=False, context=None,
				username=None, password=None):
	"""
	Renders the specified markup using the GitHub API.
	"""
	if gfm:
		url = '{}/markdown'.format(api_url)
		data = {'text': text, 'mode': 'gfm'}
		if context:
			data['context'] = context
		data = json.dumps(data, ensure_ascii=False).encode('utf-8')
		headers = {'content-type': 'application/json; charset=UTF-8'}
	else:
		url = '{}/markdown/raw'.format(api_url)
		data = text.encode('utf-8')
		headers = {'content-type': 'text/x-markdown; charset=UTF-8'}
	auth = (username, password) if username or password else None
	r = helper.requests.post(url, headers=headers, data=data, auth=auth)
	# Relay HTTP errors
	if r.status_code != 200:
		try:
			message = r.json()['message']
		except Exception:
			message = r.text
			return None
		
	soup = BeautifulSoup(r.text, "html.parser")  # parse HTML
	return soup.table

def clear():
  icon="()"
  del helper.data["systemMessage"]   

  helper.filen=[]
  try:
      del helper.data["parentMessageId"]  
      icon=icon+"(history)"
  except:
      pass
  try:
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

def clear2():
  icon="()"
  del helper.data["systemMessage"]   

  try:
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


