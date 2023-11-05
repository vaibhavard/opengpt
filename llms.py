from functions import *
import helpers.helper as helper
import threading

def gpt4(messages,model="gpt-4"):
    print("GPT$ NO STREAM")

    if "gpt-3" in check(helper.api_endpoint):
        model="gpt-3"

    if "gpt-4" in model:

        try:
            json_body=ask("","",helper.api_endpoint,helper.data)
            helper.data['parentMessageId'] = json_body['messageId']
            return json_body['response']
        
        except Exception as e:
            model="gpt-3"

    if "gpt-3" in model:

        for provider in helper.providers:
            try:

                response = helper.g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    stream=False)
                print(response)
                return response
            except Exception as e:
                print(e)
                pass

            


def gpt4stream(messages,model):
    print(f"-------{model}--------")

    if "gpt-3" in check(helper.api_endpoint) and not "Bard" in model and not "llama" in model:
        model="gpt-3"
        #helper.q.put("> Falling back to gpt-3\n\n") 


    if "gpt-4" in model and not "gpt-4-alt" in model:
        try:
            print(helper.data["systemMessage"])
          
            with requests.post(helper.api_endpoint, json=helper.data, stream=True) as resp:
                for line in resp.iter_lines():
                    if helper.stopped:
                        helper.stopped=False
                        print("TERMINATING..")
                        break

                    if line and "result" not in line.decode() and "conversationId" not in line.decode() and "[DONE]" not in line.decode():
                        line=line.decode()
                        line=line.replace("://","ui34d")

                        try:
                            parsed_data = json.loads("{" + line.replace(":", ": ").replace("data", "\"data\"",1) + "}")
                        except Exception as e:
                            parsed_data={"data":""}
                            model="gpt-3"
                            print(e)
                            ee=str(e)
                        if parsed_data!={} and parsed_data.get("data") != None:
                            msg=parsed_data['data'].replace("ui34d","://")
                            
                            helper.q.put(msg) 

                    elif line and "conversationId"  in line.decode():

                        json_body = line.decode().replace("data: ","")
                        json_body = json.loads(json_body)
                        try:
                            ss = json_body["details"]["adaptiveCards"][0]["body"][1]["text"].replace(")","")
                            links = extract_links(ss)
                            para="\n\n"
                            x=0
                            for lnk in links:
                                x=x+1
                                para=para+f"""[^{x}^]: {lnk}
                                
"""
                            a="Links:"
                            for i in range(1,x+1):
                                a = a + f"""[^{i}^]"""
                            msg="\n\n\n"+a+para
                            helper.q.put(msg) 

                        except Exception as e:
                            print(e)
                            pass

                        try:
                            helper.data['parentMessageId'] = json_body['messageId']
                        except:
                            pass
                        
                            

                        print("Conversation history saved")
                        helper.time.sleep(2)
                        helper.q.put("END") # mark the task as done


        except:
            model="gpt-3"
            #helper.q.put("> Falling back to gpt-3\n\n")
    if "gpt-4-alt" in model:
        response = helper.g4f.ChatCompletion.create(
            model=helper.g4f.models.default,
            messages=messages,
            provider=helper.g4f.Provider.Bing,
            #cookies=g4f.get_cookies(".google.com"),
            # cookies={"cookie_name": "value", "cookie_name2": "value2"},
            stream=True
        )
        try:
            for message in response:
                helper.q.put(message)
        except Exception as e:
                helper.q.put("\nError:{e}")
        helper.q.put("END") # mark the task as done
        
    if "gpt-3" in model:

        for provider in helper.providers:
            try:
                print(f"Using {provider}")


                response = helper.g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",provider=provider ,
                    messages=messages,
                    stream=True,)
                for message in response:
                    helper.q.put(message)
                break
            except Exception as e:
                print(e)
                pass
        helper.q.put("END") # mark the task as done

    if "Bard" in model  :
            del messages[0]
            print("Bard")

            try:

                response = helper.g4f.ChatCompletion.create(
                    model=helper.g4f.models.default,provider=helper.g4f.Provider.Bard ,
                    messages=messages,
                    cookies=helper.google_cookies,
                    auth=True
                    )
                helper.q.put(response)
            except:
                pass
            helper.q.put("END") # mark the task as done
    elif "openchat" in model or "llama" in model:
            try:

                response = helper.g4f.ChatCompletion.create(
                    model=helper.g4f.models.default,provider=helper.g4f.Provider.HuggingChat ,
                    messages=messages,
                    cookies=helper.openchat_cookies,
                    auth=True
                    )
                helper.q.put(response)
            except:
                pass
            helper.q.put("END") # mark the task as done
