import re

from openai import OpenAI

client = OpenAI()


def score(text):
    reply = client.chat.completions.create(model="m", messages=[{"role": "user", "content": text}])
    content = reply.choices[0].message.content
    return int(re.search(r"Score: (\d+)", content).group(1))
