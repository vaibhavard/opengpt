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

providers=[g4f.Provider.GptGo,g4f.Provider.FreeGpt,g4f.Provider.GeekGpt,g4f.Provider.GPTalk,g4f.Provider.Llama2,g4f.Provider.GptForLove]

provi = [
g4f.Provider.Liaobots,
g4f.Provider.Phind,
g4f.Provider.GeekGpt,
g4f.Provider.Yqcloud,
g4f.Provider.AItianhu	,
g4f.Provider.AItianhuSpace	,
g4f.Provider.Aivvm	,
g4f.Provider.AiAsk	,
g4f.Provider.ChatgptX	,
g4f.Provider.FreeGpt	,
g4f.Provider.GPTalk	,
g4f.Provider.GptForLove	,
g4f.Provider.GptGo	,
g4f.Provider.Llama2	,
g4f.Provider.NoowAi	,
g4f.Provider.OpenaiChat	,
g4f.Provider.Acytoo	,
g4f.Provider.Raycast,
g4f.Provider.ChatAiGpt	,
g4f.Provider.ChatForAi	,
g4f.Provider.Chatgpt4Online	,
g4f.Provider.ChatgptDemo	,
g4f.Provider.ChatgptLogin	,
g4f.Provider.CodeLinkAva	,
g4f.Provider.EasyChat	,
g4f.Provider.Aibn	,

]
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
