from functions import *
import helpers.helper as helper
import threading
import asyncio
from functions import check_content
from openpyxl import Workbook

async def run_provider(provider: helper.g4f.Provider.BaseProvider,messages):
    try:
        response = await helper.g4f.ChatCompletion.create_async(
            model=helper.g4f.models.default,
            messages=messages,
            provider=provider,
        )
        print(f"{provider.__name__}:", response)
        if response is not None and response != "" and "support@chatbase.co" not in response:
            helper.providers.append(provider)

            return response
        else:
            return None
    except Exception as e:
        return None
        
async def run_all():
    calls = [
        run_provider(provider,[{"role": "user", "content": "Hello!"}]) for provider in helper.provi
    ]
    for future in asyncio.as_completed(calls):
        response = await future
        if response is not None and response != "" and "support@chatbase.co" not in response:
            print("✅")
    
def get_providers():
    asyncio.run(run_all())
    return str(helper.providers)

def gpt4(messages,model="gpt-4"):
    print("GPT$ NO STREAM")

    if "gpt-3" in check(helper.api_endpoint):
        model="gpt-3"

    if "gpt-4" in model :

        try:
            helper.data["stream"]=False
            json_body=ask("","",helper.api_endpoint,helper.data)
            helper.data["stream"]=True
            if "gpt-4-dev" not in model:
                helper.data['parentMessageId'] = json_body['messageId']
            return json_body['response']
        
        except Exception as e:
            print(e)
            model="gpt-3"


    if "gpt-3" in model:

        for provider in helper.providers:
            try:

                response = helper.g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",provider=provider ,
                    messages=messages,
                    stream=False)
                print(response)
                return response
            except Exception as e:
                print(e)
                pass

            


def gpt4stream(messages,model):
    print(f"-------{model}--------")

    if "gpt-3" in check(helper.api_endpoint) and not "Bard" in model and not "llama" in model and not "gpt-4-alt" in model:
        model="gpt-3"
        helper.q.put("> Falling back to gpt-3\n\n") 


    if "gpt-4" in model :
        try:
            print(helper.data)
          
            with requests.post(helper.api_endpoint, json=helper.data, stream=True) as resp:
                for line in resp.iter_lines():
                    if helper.stopped:
                        helper.stopped=False
                        print("TERMINATING..")
                        helper.q.put("END") # mark the task as done

                        break

                    if line and "result" not in line.decode() and "conversationId" not in line.decode() and "[DONE]" not in line.decode():
                        line=line.decode()
                        line=line.replace("://","ui34d")

                        try:
                            parsed_data = json.loads("{" + line.replace(":", ": ").replace("data", "\"data\"",1) + "}")
                        except Exception as e:
                            parsed_data={"data":"."}
                            model="gpt-3"
                            print(e)
                            ee=str(e)
                        if parsed_data!={} and parsed_data.get("data") != None:
                            msg=parsed_data['data'].replace("ui34d","://")
                            
                            helper.q.put(msg) 

                    elif line and "conversationId"  in line.decode():
                        if "gpt-4-dev" not in model:

                            json_body = line.decode().replace("data: ","")
                            json_body = json.loads(json_body)
                            print(json_body)
                            try:
                                table = check_content(str(json_body["response"]), 'https://api.github.com', True, None, None, None)

                                if table!=None:
                                    wb = Workbook()
                                    ws = wb.active

                                    # Extract table headers
                                    header_row = table.find('tr')
                                    header_cells = header_row.find_all('th')
                                    header_values = [cell.get_text(strip=True) for cell in header_cells]

                                    # Write header values to worksheet
                                    ws.append(header_values)

                                    # Extract table rows
                                    body_rows = table.find_all('tr')[1:]  # Exclude the header row
                                    for body_row in body_rows:
                                        body_cells = body_row.find_all('td')
                                        body_values = [cell.get_text(strip=True) for cell in body_cells]
                                        ws.append(body_values)

                                    # Save the workbook to an Excel file
                                    wb.save('static/table.xlsx')
                                    helper.q.put(f"\n[View in excel]({helper.server}/static/table.xlsx)") 
                            except:
                                pass
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
                            if "gpt-4-dev" not in model:
                                helper.data['parentMessageId'] = json_body['messageId']
                                print("Conversation history saved")
                        except:
                            pass

                        helper.q.put("END") # mark the task as done


        except Exception as e:
            print(e)
            # model="gpt-3"
            helper.q.put("> Falling back to gpt-3\n\n")

    
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
