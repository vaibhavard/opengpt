   

from collections import deque
from utils import num_tokens_from_messages
from utils.cyclic_buffer import CyclicBuffer
import helpers.helper as helper
from llms import gpt4,gpt4stream
import threading
import requests
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
        max_tokens: int = 3800,
    ):
        self.messages = CyclicBuffer[Message](buffer_capacity)
        self.initial_prompt = Message("system", helper.initial_multi_prompt)

        self.dep_prompt = helper.dep_prompt
        self.max_tokens = max_tokens
        self.error = False
        self.persist=False
        self.error_count = 0

    def execute_code(self, code: str):
        try:
            response = requests.post(
                f"{helper.server}/execute", data=code.encode("utf-8")
            )
            result = response.json()
        except Exception as e:
            result = {"Error":"The Local Code Server is currently down.Please ask the site admin to boot it!"}

        return result
    
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
            f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#additional_instructions)") + f"\n{message['content']}\n\n"
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
        input_list = input_string.split("```")



        if len(input_list) >= 2:
            executer = input_list[1]
            if executer.startswith("python"):
                executer = executer.replace("python","",1)

            if "import" in executer:

                print(f"{COLOR_RED }Installing Packages...{COLOR_RESET}")
                
                messages=[{'role': 'user', 'content': f"{self.dep_prompt}\n```{executer}```\nPlease output codeblock of subprocess.call with packages to install in above code."}]
                helper.data["systemMessage"]= "".join(
                    f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#additional_instructions)") + f"\n{message['content']}\n\n"
                    for message in messages
                )                
                helper.data['message']= f"Please output codeblock of subprocess.call with packages to install in above code."
                helper.code_q.put("\n\n**Detecting Packages to Install  ...**.\n\n")

                threading.Thread(target=gpt4stream,args=(messages,"gpt-4-dev")).start() # start the thread
                req_list=""

                while True:
                    try:
                        line = helper.q.get(block=False)
                        print(line)
                        if line == "END":
                            break
                        else:
                            helper.code_q.put(line)
                            req_list=req_list+line
                        helper.q.task_done() # mark the task as done
                    except helper.queue.Empty: 
                            pass
                print(req_list)
                req_list=req_list.split(("```"))

                if len(req_list) >= 2:
                    helper.code_q.put("\n\n**Installing packages  ...**.\n\n")
                    req = req_list[1]
                    if req.startswith("python"):
                        req = req.replace("python","",1)
                    print(req)
                    install=self.execute_code(req)
                    if "Error" in install:
                        print(install["Error"])
                        helper.code_q.put(f"\n\nInstallation Error (ignoring..): {install['Error']}\n\n")

            helper.code_q.put("\n\n**Running Script and retrieving output ...**\n\n")

            data=self.execute_code(executer)
            if "Error" in data:
                if "The Local Code Server is currently down" in data["Error"]:
                    helper.code_q.put(data["Error"])
                    helper.code_q.put(f"END")
                    return "done"


        return executer,data




    def run(self):
        while True:
            global data
            global prevdata
            if not self.persist:
                self.persist=False

                if not self.error:
                    self.messages.clear()
                    user_input=helper.task_query
                    if "--image" in user_input:
                        user_input.replace("--image","")
                        self.initial_prompt=Message("system", helper.initial_multi_image_prompt)

                else:
                    if self.error_count<3:
                        user_input = helper.error_prompt
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
                helper.code_q.put(f"\nSYSTEM:{data}\n")
            else:
                gpt_code=gpt_response




            # print(f"{COLOR_GREEN}{gpt_code}{COLOR_RESET}")

            if data!=prevdata:

                if "Error" not in data and data != "" :
                    prevdata=data
                    helper.code_q.put(f"\n\n> Task Completed Successfully\n\n")

                    print(f"{COLOR_ORANGE}Output: {data}{COLOR_RESET}")

                    self.messages.push(Message("system", f"Output: {data}"))
                    self.persist=True
                    try:
                        embed=f"""
You can view your *created file* on :
{helper.server}/static/{data["filename"]}
You can view all files on :
{helper.server}
"""
                        helper.code_q.put(f"\n{embed}\n")

                    except:
                        pass
                elif data!="":
                    self.error = True
                    print(f"{COLOR_RED}Error: {data}{COLOR_RESET}")
                    self.error_count = self.error_count + 1
                    self.messages.push(Message("system", f"The data variable output is : {data}."))

                    helper.code_q.put(f"\n\n**Uh Oh , An error occurred.. Trying again with plan {self.error_count+1}**.\n\n")


            else:
                self.persist=False
                helper.code_q.put(f"END")
                return "done"
            






