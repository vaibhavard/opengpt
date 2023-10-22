import json
import requests
import time
import random
import tiktoken
import g4f
import random
from helpers.prompts import *

python_boolean_to_json = {
    "true": True,
}

providers=[g4f.Provider.GPTalk	,g4f.Provider.GptForLove	,g4f.Provider.Theb	,g4f.Provider.NoowAi	,g4f.Provider.Vercel,g4f.Provider.Llama2]

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

data = {
    'jailbreakConversationId':json.dumps(python_boolean_to_json),
    "stream":True,
    "systemMessage":gpt4mod
}
