#https://ollama.com/library/qwen3

from ollama import Client

client = Client(host='http://host.docker.internal:11434')
response = client.chat(
    model='qwen3:1.7b',
    messages=[{'role': 'user', 'content': 'Give me a best finance advice.'}],
)
print(response.message.content)