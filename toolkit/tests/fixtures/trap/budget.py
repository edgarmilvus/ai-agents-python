from openai import OpenAI

client = OpenAI()


def run(messages):
    while len(messages) < 20:
        reply = client.chat.completions.create(model="m", messages=messages)
        messages.append(reply)
    return messages
