from helpers.config  import *
from helpers.prompts import *
from helpers.provider import *

from helpers.models import model




def streamer(tok):
        completion_timestamp = int(time.time())
        completion_id = ''.join(random.choices(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))
        completion_tokens = num_tokens_from_string(tok)

        completion_data = {
            'id': f'chatcmpl-{completion_id}',
            'object': 'chat.completion.chunk',
            'created': completion_timestamp,
            'model': 'gpt-4',
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": completion_tokens,
                "total_tokens": completion_tokens,
            },
            'choices': [
                {
                    'delta': {
                        'role':"assistant",
                        'content':tok
                    },
                    'index': 0,
                    'finish_reason': None
                }
            ]
        }
        return completion_data


def output(tok):
        completion_timestamp = int(time.time())
        completion_id = ''.join(random.choices(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))
        completion_tokens = num_tokens_from_string(tok)

        return {
            'id': 'chatcmpl-%s' % completion_id,
            'object': 'chat.completion',
            'created': completion_timestamp,
            'model': model,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": completion_tokens,
                "total_tokens": completion_tokens,
            },
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': tok
                },
                'finish_reason': 'stop',
                'index': 0
            }]
        }


