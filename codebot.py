from collections import deque
from utils import num_tokens_from_messages
from utils.cyclic_buffer import CyclicBuffer
import helpers.helper as helper
from llms import gpt4,gpt4stream
import threading
import re
import ast
import traceback
import time
import json
import random
import subprocess
import anycreator
from code_interpreter import CodeInterpreter
data = ""
prevdata=""
COLOR_GREEN = "\033[32m"
COLOR_ORANGE = "\033[33m"
COLOR_GRAY = "\033[90m"
COLOR_RESET = "\033[0m"
COLOR_BLUE='\033[0;34m'     
COLOR_RED='\033[0;31m'   

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class Codebot:
    def __init__(
        self,
        buffer_capacity=15,
        max_tokens: int = 10000,
    ):
        self.messages = CyclicBuffer[Message](buffer_capacity)
        self.initial_prompt = Message("system", helper.new_prompt)

        self.dep_prompt = helper.dep_prompt
        self.max_tokens = max_tokens
        self.error = False
        self.persist=False
        self.error_count = 0
        self.result=""
        self.sandbox = CodeInterpreter(api_key="e2b_0f97184b1b72484672948fe495b7c2d7226ac400")
        self.sandbox.cwd = "/code"  

    def code_exec(self,code):
        anycreator.data={}
        self.result=""
        print("EXECUTING")
        def get(query):
            self.result=self.result+str(query)

        try:
            process_cwd=self.sandbox.process.start(code,on_stdout=get,on_stderr=get,timeout=100)
            process_cwd.wait()
            anycreator.data={"output":self.result}

        except Exception :
            self.result="Timed out waiting for response.Please rewrite and modify the code to work efficently within shorter time."
            anycreator.data={"Error":self.result}


        


        print("DONE EXECUTION")

        return anycreator.data
    
    def execute_code(self, code: str):
        t1 = threading.Thread(target=self.code_exec, args=(code,))
        t1.start()
        t= time.time()
        helper.code_q.put("\n\n**Executing Code..**\n\n")

        while anycreator.data=={}:
            if time.time() -t >4:
                helper.code_q.put(".")
                t= time.time()

        return anycreator.data
    
    def chat_with_gpt(self) -> str:
        resp = ""
        messages = deque([m.to_dict() for m in self.messages])
        messages = deque([m.to_dict() for m in self.messages])
        while True:
            message_dicts = [self.initial_prompt.to_dict()] + list(messages)
            num_tokens = num_tokens_from_messages(message_dicts)
            if num_tokens < self.max_tokens:
                break
            if messages:
                # remove oldest message and try again
                messages.popleft()
            else:
                # no more messages
                self.messages.pop()
                return (
                    f"Too many tokens ({num_tokens}>{self.max_tokens}), "
                    f"please limit your message size!"
                )
                
        helper.data["systemMessage"]= "".join(
            f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#instructions)") + f"\n{message['content']}\n\n"
            for message in message_dicts
        )
        helper.data['message']= message_dicts[-1]['content']

        if  helper.stopped:
            helper.stopped = False
            print("No process to kill.")
        threading.Thread(target=gpt4stream,args=(messages,"gpt-4-dev")).start() # start the thread
        helper.code_q.put("\n\n**Writing Code ...**\n\n")

        while True:
            try:
                line = helper.q.get(block=False)
                print(line)
                if line == "END":
                    break
                else:
                    helper.code_q.put(line)
                    resp=resp+line
                helper.q.task_done() # mark the task as done
            except helper.queue.Empty: 
                    pass
            
        with open(f"CodeAI_LOG.txt", "w") as f:
            f.write(str(message_dicts))

        return resp

    def parse_response(self, input_string: str):
        global data
        helper.code_q.put("\n\n**Installing Dependencies..**\n\n")

        executer="No code blocks in code."

        regex = r'```text\n(.*?)\n```'
        matches = re.findall(regex, input_string, re.DOTALL)
        info_blocks = [match for match in matches]
        if info_blocks:
            info=ast.literal_eval(info_blocks[0])
            if "js" in info["language"]:
                regex2 = r'```js\n(.*?)\n```'
                self.sandbox.install_npm_packages(info["packages"])
            else:
                regex2 = r'```{info}\n(.*?)\n```'.format(info=info["language"].lower())
                if "python" in info["language"].lower():
                    if set(helper.installed_packages).issubset(info["packages"]) == False:
                        self.sandbox.install_python_packages(info["packages"])
            try:
                self.sandbox.install_system_packages(info["system_packages"])
            except:
                pass


            matches = re.findall(regex2, input_string, re.DOTALL)
            code_blocks = [match for match in matches]
            code_blocks=code_blocks[0]
            if info["code_filename"] !=[]:
                self.sandbox.filesystem.write(info["code_filename"], code_blocks)  
            if info["port"] == "":
                data=self.execute_code(info["start_cmd"])
            else:
                self.sandbox.process.start(info["start_cmd"])
                url = self.sandbox.get_hostname(info["port"])
                data={"output":f"Your Application is live [here](https://{url})"}

            if not "Error" in data:
                data={"output":data["output"]}
                if info["filename"] != "":
                    data["filename"] = str(info["filename"])

            try:
                if info['filename'] !=[]:

                    file_in_bytes = self.sandbox.download_file(f"/code/{info['filename']}")  

                    with open(f"static/{info['filename']}", "wb") as f:  
                        f.write(file_in_bytes)
            except Exception as e:
                print(e)
                data["warning"]="Unable to download File as it does not exist /empty/ malformed"
                pass

            executer=code_blocks  


        return executer,data




    def run(self):
        while True:
            global data
            global prevdata
            if not self.persist:
                self.persist=False

                if not self.error:
                    if helper.filen=="":
                        user_input=helper.task_query+"Please note that you have the capability to create anything . Avoid internet searches. Share the complete code."
                    else:
                        with open(helper.filen, "rb") as f:
                            self.sandbox.upload_file(f)  
                        user_input=helper.task_query+f"The file path is {helper.filen}.Please note that you have the capability to create anything .Avoid internet searches. Share the complete code."

                    if "--image" in user_input:
                        user_input.replace("--image","")
                        self.initial_prompt=Message("system", helper.initial_multi_image_prompt)

                else:
                    if  self.error_count<3 :
                        user_input="The code threw an error as mentioned .Please fix the error and output the corrected code."

                        if helper.filen=="":
                            user_input=gpt4([{"role": "system", "content": f"{helper.rephrase_prompt.format(rephrase=random.choice(helper.rephrase_list),sentence=helper.task_query)}"}],"gpt-3.5-turbo")+"Please note that you have the capability to create anything using Python. Avoid internet searches. Share the complete code."
                        else:
                            user_input=gpt4([{"role": "system", "content": f"{helper.rephrase_prompt.format(rephrase=random.choice(helper.rephrase_list),sentence=helper.task_query)}"}],"gpt-3.5-turbo")+f"The file path is {helper.filen}Please note that you have the capability to create anything using Python. Avoid internet searches. Share the complete code."



                    else:
                        helper.code_q.put(f"\n\nThe system was unable to fix the Error by itself.Please try rephrasing your prompt or using different method.\n\n")
                        helper.code_q.put(f"END")
                        self.error = False
                        self.persist=False
                        self.error_count = 0
                        return "error"



                user_cmd = user_input.strip().lower()

                if user_cmd == "reset" or user_cmd == "clear":
                    self.messages.clear()
                    return True
                elif user_cmd == "exit":
                    return False
                
                if user_input.strip() :
                    self.messages.push(Message("user",  user_input))

            gpt_response = self.chat_with_gpt()

            if gpt_response.strip():
                self.messages.push(Message("assistant", gpt_response))

            if "```" in gpt_response:

                gpt_code,data = self.parse_response(gpt_response)
                print(data)
                helper.code_q.put(f"\n\nSYSTEM:{data}\n\n")

            else:
                gpt_code=gpt_response




            # print(f"{COLOR_GREEN}{gpt_code}{COLOR_RESET}")

            if data!=prevdata:

                if "Error" not in data and data != "" :
                    prevdata=data
                    helper.code_q.put(f"\n\n> Task Completed Successfully\n\n")

                    print(f"{COLOR_ORANGE}Output: {data}{COLOR_RESET}")

                    self.messages.push(Message("system", f"Output of data variable: {data}"))
                    self.persist=True
                    try:
                        embed=f"""
You can view your *created files* [here]({helper.server}/static/{data["filename"]})
You can view all files on :
{helper.server}
"""
                        helper.code_q.put(f"\n{embed}\n")

                    except:
                        helper.code_q.put(f"\nNote:View files on {helper.server}\n")

                        pass
                elif data!="":
                    self.error = True
                    print(f"{COLOR_RED}Error: {data}{COLOR_RESET}")
                    self.error_count = self.error_count + 1
                    self.messages.push(Message("system", f"The code threw an exception {data}."))

                    if self.error_count==1:

                        helper.code_q.put(f"\n\n**Trying to fix the error...**\n\n")
                    else:
                        helper.code_q.put(f"\n\n**Uh Oh , An error occurred (again).. Trying again with plan {self.error_count}**.\n\n")



            else:
                self.persist=False
                helper.code_q.put(f"END")
                return "done"
            
