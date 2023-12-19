import threading
from flask import Flask, url_for, redirect
from flask import request as req
from flask_cors import CORS
import helpers.helper as helper
from helpers.provider import *
from memory.memory import Memory
m = Memory()
from transformers import AutoTokenizer
import extensions
from base64 import b64encode
from llms import gpt4,gpt4stream,get_providers
import pyimgur
app = Flask(__name__)
CORS(app)
import queue
from functions import allocate,clear,clear2
from codebot import Codebot
from werkzeug.utils import secure_filename
import subprocess
import os
UPLOAD_FOLDER = 'static'
 
codebot=Codebot()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/v1/chat/completions", methods=['POST'])
def chat_completions2():
    global codebot
    helper.stopped=True

    streaming = req.json.get('stream', False)
    model = req.json.get('model', 'gpt-4-web')
    messages = req.json.get('messages')
    print(messages)
    print("-"*100)
    functions = req.json.get('functions')

    
    allocate(messages,helper.data, m.get_data('uploaded_image'),m.get_data('context'),helper.systemp,model)

    t = time.time()

    def stream_response(messages,model):
        helper.q = queue.Queue() # create a queue to store the response lines

        if  helper.stopped:
            helper.stopped = False
            print("No process to kill.")

        threading.Thread(target=gpt4stream,args=(messages,model)).start() # start the thread
        
        started=False
        while True: # loop until the queue is empty
            try:
                if 11>time.time()-t>10 and not started and  m.get_data('uploaded_image')!="":
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("> Analysing this Image🖼️"), separators=(',' ':'))
                    time.sleep(2)
                elif 11>time.time()-t>10 and not started :
                    yield "WAIT"
                    time.sleep(1)  
                elif 11>time.time()-t>10 and not started :
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("> Please wait"), separators=(',' ':'))
                    time.sleep(2)
                elif time.time()-t>11 and not started :
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("."), separators=(',' ':'))
                    time.sleep(1)
                if time.time()-t>100 and not started:
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("Timed out"), separators=(',' ':'))
                    break

                line = helper.q.get(block=False)
                if line == "END":
                    break
                if not started:
                    started = True
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("\n\n"), separators=(',' ':'))

                yield 'data: %s\n\n' % json.dumps(helper.streamer(line), separators=(',' ':'))

                helper.q.task_done() # mark the task as done


            except helper.queue.Empty: 
                pass
            except Exception as e:
                print(e)


    def aigen(model):
        helper.code_q = queue.Queue() # create a queue to store the response lines


        threading.Thread(target=codebot.run).start() # start the thread
        
        started=False
        while True: # loop until the queue is empty
            try:
                if 11>time.time()-t>10 and not started :
                    yield "WAIT"
                    time.sleep(1)  
                if 11>time.time()-t>10 and not started :
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("> Your task is being processed"), separators=(',' ':'))
                    time.sleep(2)
                elif time.time()-t>11 and not started :
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("."), separators=(',' ':'))
                    time.sleep(1)
                if time.time()-t>100 and not started:
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("Timed out"), separators=(',' ':'))
                    break

                line = helper.code_q.get(block=False)
                if line == "END":
                    break
                if not started:
                    started = True
                    yield 'data: %s\n\n' % json.dumps(helper.streamer("\n\n"), separators=(',' ':'))

                yield 'data: %s\n\n' % json.dumps(helper.streamer(line), separators=(',' ':'))

                helper.code_q.task_done() # mark the task as done


            except helper.queue.Empty: 
                pass
            except Exception as e:
                print(e)


    if "/clear" in helper.data["message"]  :
        m.update_data('uploaded_image', "")
        m.update_data('context', "")
        m.save() 
        return 'data: %s\n\n' % json.dumps(helper.streamer('Cleared✅ '+clear()), separators=(',' ':'))
    
    elif "/log" in helper.data["message"]  :
        return 'data: %s\n\n' % json.dumps(helper.streamer(str(data)), separators=(',' ':'))


    elif "/fileserver" in helper.data["message"]  :
        return 'data: %s\n\n' % json.dumps(helper.streamer(f"You can browse/upload file on {helper.server}"), separators=(',' ':'))


    elif "/prompt" in helper.data["message"]  :

        if helper.systemp == False:
            helper.systemp=True
        else:
            helper.systemp=False
        return 'data: %s\n\n' % json.dumps(helper.streamer(f"helper.Systemprompt is  {helper.systemp}"), separators=(',' ':'))

    elif "/help" in helper.data["message"]  :
        return 'data: %s\n\n' % json.dumps(helper.streamer(helper.about), separators=(',' ':'))
    
    
    if "/getproviders" in helper.data["message"] :
        return 'data: %s\n\n' % json.dumps(helper.streamer(get_providers()), separators=(',' ':'))
    
    if "/mindmap" in helper.data["message"] or "/branchchart" in helper.data["message"] or "/timeline" in helper.data["message"] :
        return app.response_class(extensions.grapher(helper.data["message"],model), mimetype='text/event-stream')
    
    elif "/flowchart" in helper.data["message"] or "/complexchart" in helper.data["message"] or  "/linechart" in helper.data["message"] :
        if "gpt-3" in model:
            if "/flowchart" in  helper.data["message"]:
                return app.response_class(stream_response([{"role": "system", "content": f"{flowchat}"},{"role": "user", "content": f"{data['message'].replace('/flowchart','')}"}],"gpt-3"), mimetype='text/event-stream')
            if "/complexchart" in  helper.data["message"]:
                return app.response_class(stream_response([{"role": "system", "content": f"{complexchat}"},{"role": "user", "content": f"{data['message'].replace('/complexchart','')}"}],"gpt-3"), mimetype='text/event-stream')
            if "/linechart" in  helper.data["message"]:
                return app.response_class(stream_response([{"role": "system", "content": f"{linechat}"},{"role": "user", "content": f"{data['message'].replace('/linechat','')}"}],"gpt-3"), mimetype='text/event-stream')
        elif "gpt-4" in model:

            if "/flowchart" in  helper.data["message"]:
                helper.data["message"]=helper.data["message"].replace("/flowchart","")
                helper.data["systemMessage"]=mermprompt.format(instructions=flowchat)
            if "/complexchart" in  helper.data["message"]:
                helper.data["message"]=helper.data["message"].replace("/complexchart","")
                helper.data["systemMessage"]=mermprompt.format(instructions=complexchat)

            if "/linechart" in  helper.data["message"]:
                helper.data["message"]=helper.data["message"].replace("/linechart","")
                helper.data["systemMessage"]=mermprompt.format(instructions=linechat)

            return app.response_class(stream_response(messages,"gpt-4"), mimetype='text/event-stream')




    if not streaming and "AI conversation titles assistant" in messages[0]["content"]:
        print("USING GPT_4 CONVERSATION TITLE")
        k=gpt4(messages,"gpt-3.5-turbo")
        print(k)
        return helper.output(k)
    elif not streaming :
        if True:
            print("USING GPT_4 NO STREAM")
            print(model)

            k=gpt4(messages,model)
            print(k)
            return helper.output(k)
    if  streaming and "/aigen" not in helper.data["message"] and model!="gpt-4-code": 
        return app.response_class(stream_response(messages,model), mimetype='text/event-stream')
    elif streaming and "/aigen" in helper.data["message"]  and model!="gpt-4-code":
        helper.task_query=helper.data["message"].replace("/aigen","")

        return app.response_class(aigen(model), mimetype='text/event-stream')

    elif model=="gpt-4-code":
        return app.response_class(aigen(model), mimetype='text/event-stream')





@app.route('/api/<name>')
def hello_name(name):
   url = "https://"+name
   helper.server=url
   return f'{helper.server}'

@app.route('/context', methods=['POST'])
def my_form_post():
    text = req.form['text']
    helper.filen=f"static/{secure_filename(req.form['filename'])}"

    if text!="image":
        m.update_data('context', text)
        m.save()
    else:
        link= f"https://codegen-server.onrender.com/static/{req.form['filename']}"
        m.update_data('uploaded_image',link)
        m.save()        
        print(link)
        return "[Image Uploaded]"
    return "[File added]"

@app.route('/context')
def my_form():
    return '''
<form method="POST">
    <textarea name="text"></textarea>
    <input type="submit">
</form>
'''

@app.route('/upload', methods=['GET','POST'])
def index():
 
    # If a post method then handle file upload
    if req.method == 'POST':
 
        if 'file' not in req.files:
            return redirect('/')
 
        file = req.files['file']
 
 
        if file :
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
 
 
    # Get Files in the directory and create list items to be displayed to the user
    file_list = ''
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        # Create link html
        link = url_for("static", filename=f) 
        file_list = file_list + '<li><a href="%s">%s</a></li>' % (link, f)
 
    # Format return HTML - allow file upload and list all available files
    return_html = '''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload File</h1>
    <form method=post enctype=multipart/form-data>
            <input type=file name=file><br>
            <input type=submit value=Upload>
    </form>
    <hr>
    <h1>Files</h1>
    <ol>%s</ol>
    ''' % file_list
 
    return return_html

@app.route('/upload_image', methods=['GET', 'POST']) #Obsolete
def upload():
    global img
    if req.method == 'POST': 
        file=req.files['file1']
        print(file.filename)
        if 'file1' not in req.files: 
            print("EROR")
            return 'there is no file1 in form!'
        client = pyimgur.Imgur("47bb97a5e0f539c")
        r = client._send_request('https://api.imgur.com/3/image', method='POST', params={'image': b64encode(file.read())})
        m.update_data('uploaded_image', r["link"])
        m.save()        
        print("image saved")
        return f"[Image Uploaded]"

    return '''
    <h1>Upload new Image</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file1">
      <input type="submit">
    </form>
    '''

def get_embedding(input_text, token):
    huggingface_token = helper.huggingface_token
    embedding_model = 'sentence-transformers/all-mpnet-base-v2'
    max_token_length = 500

    # Load the tokenizer for the 'all-mpnet-base-v2' model
    tokenizer = AutoTokenizer.from_pretrained(embedding_model)
    # Tokenize the text and split the tokens into chunks of 500 tokens each
    tokens = tokenizer.tokenize(input_text)
    token_chunks = [tokens[i:i + max_token_length]
                    for i in range(0, len(tokens), max_token_length)]

    # Initialize an empty list
    embeddings = []

    # Create embeddings for each chunk
    for chunk in token_chunks:
        # Convert the chunk tokens back to text
        chunk_text = tokenizer.convert_tokens_to_string(chunk)

        # Use the Hugging Face API to get embeddings for the chunk
        api_url = f'https://api-inference.huggingface.co/pipeline/feature-extraction/{embedding_model}'
        headers = {'Authorization': f'Bearer {huggingface_token}'}
        chunk_text = chunk_text.replace('\n', ' ')

        # Make a POST request to get the chunk's embedding
        response = requests.post(api_url, headers=headers, json={
                                 'inputs': chunk_text, 'options': {'wait_for_model': True}})

        # Parse the response and extract the embedding
        chunk_embedding = response.json()
        # Append the embedding to the list
        embeddings.append(chunk_embedding)

    # averaging all the embeddings
    # this isn't very effective
    # someone a better idea?
    num_embeddings = len(embeddings)
    average_embedding = [sum(x) / num_embeddings for x in zip(*embeddings)]
    embedding = average_embedding
    return embedding


@app.route('/embeddings', methods=['POST'])
def embeddings():
    input_text_list = req.get_json().get('input')
    input_text      = ' '.join(map(str, input_text_list))
    token           = req.headers.get('Authorization').replace('Bearer ', '')
    embedding       = get_embedding(input_text, token)
    
    return {
        'data': [
            {
                'embedding': embedding,
                'index': 0,
                'object': 'embedding'
            }
        ],
        'model': 'text-embedding-ada-002',
        'object': 'list',
        'usage': {
            'prompt_tokens': None,
            'total_tokens': None
        }
    }

@app.route('/')
def yellow_name():
   return f'Server 1 is OK and server 2 check: {helper.server}'

@app.route('/clear_all')
def clear_all():
   return str(clear2())
 
@app.route("/v1/models")
def models():
    print("Models")
    return helper.model



if __name__ == '__main__':
    config = {
        'host': '0.0.0.0',
        'port': 1337,
        'debug': False,
    }

    app.run(**config)
