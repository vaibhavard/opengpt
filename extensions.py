import helpers.helper as helper
import threading,json
from functions import mm,ask
import time
import llms

async def run_graphs(messages):
    calls = [
        llms.run_provider(provider,messages) for provider in helper.provi
    ]
    for future in llms.asyncio.as_completed(calls):
        response = await future
        if response is not None and response != "" and "support@chatbase.co" not in response:
            collect=mm(response)
            if not  "ERROR in encoding123" in collect:
                helper.worded=collect
                break

def send_req(msg,model):

    if "/" not in msg:
        type_flow=llms.gpt4([{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": helper.type_flowchart.format(question=helper.data["message"])}],"gpt-3").lower()
        if "none" not in type_flow:
            if "mindmap" in type_flow or "mind map" in type_flow:
                msg ="/mindmap "+type_flow
            else:
                msg = "/branchchart "+type_flow
        else:
            helper.worded="."
            msg="none"
        print(type_flow)

    if "/mindmap" in msg:
        prompt=helper.mindprompt
        tmap="/mindmap"
    elif "/branchchart" in msg:
        prompt=helper.mermap
        tmap="/branchchart"
    elif "/timeline" in msg:
        prompt=helper.catmap
        tmap="/timeline"

    if "gpt-4" in model and msg!="none":
        for i in range(1,3):
            collect=mm(ask(msg.replace(tmap,''),helper.mermprompt.format(instructions=prompt),helper.api_endpoint))
            if "ERROR in encoding123" not in collect:
                helper.worded=collect
                break
            else:
                helper.worded=""
                print("invalid context")
            if i==3:
                time.sleep(2)
                helper.worded="Failed because max tries exceed!.Try rephrasing Your prompt."
                break
        print("GPT_4")
    elif msg!="none":
        collect=mm(llms.gpt4([{"role": "system", "content": f"{prompt}"},{"role": "user", "content": f"{msg.replace(tmap,'')}"}],"gpt-3"))
        llms.asyncio.run(run_graphs([{"role": "system", "content": f"{prompt}"},{"role": "user", "content": f"{msg.replace(tmap,'')}"}]))
        print("GPT_3")


def grapher(msg,model):
    import time
    t=time.time()
    print("Creating..")
    helper.worded=""
    yield 'data: %s\n\n' % json.dumps(helper.streamer(">Please wait."), separators=(',' ':'))

    t1 = threading.Thread(target=send_req,args=(msg,model,))
    t1.start()
    sent=False
    while helper.worded=="":
        if 10>time.time()-t>9 and not sent:
            yield 'data: %s\n\n' % json.dumps(helper.streamer(">Please wait."), separators=(',' ':'))
            sent=True
        if sent:
            yield 'data: %s\n\n' % json.dumps(helper.streamer("."), separators=(',' ':'))
            time.sleep(1)
        if time.time()-t>100:
            break

    yield 'data: %s\n\n' % json.dumps(helper.streamer(""), separators=(',' ':'))
    yield 'data: %s\n\n' % json.dumps(helper.streamer(helper.worded), separators=(',' ':'))

def grapher2():
    t=time.time()
    sent=False
    while helper.worded=="":
        if 4>time.time()-t>3 and not sent:
            yield 'data: %s\n\n' % json.dumps(helper.streamer("\n\n"), separators=(',' ':'))
            yield 'data: %s\n\n' % json.dumps(helper.streamer(">Please wait."), separators=(',' ':'))
            sent=True
        if sent:
            yield 'data: %s\n\n' % json.dumps(helper.streamer("."), separators=(',' ':'))
            time.sleep(1)    
        if 100<time.time():
            break

    yield 'data: %s\n\n' % json.dumps(helper.streamer("\n\n"), separators=(',' ':'))
    yield 'data: %s\n\n' % json.dumps(helper.streamer(helper.worded), separators=(',' ':'))
