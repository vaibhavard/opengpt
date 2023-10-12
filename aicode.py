import threading
import queue

def flask_streaming():
    q = queue.Queue() # create a queue to store the response lines
    def post_request(): # define a function to send the post request in a separate thread
        with requests.post(api_endpoint, json=data, stream=True) as resp:
            for line in resp.iter_lines():
                q.put(line) # put each line of the response into the queue
    threading.Thread(target=post_request).start() # start the thread
    yield("Test") # this should run instantly after requests.post without waiting for response
    while True: # loop until the queue is empty
        try:
            line = q.get(timeout=1) # get a line from the queue with a timeout of 1 second
            yield line # yield the line
            q.task_done() # mark the task as done
        except queue.Empty: # if the queue is empty, break the loop
            break

@app.route("/stream")
def stream():
    return app.response_class(flask_streaming(data), mimetype='text/event-stream')