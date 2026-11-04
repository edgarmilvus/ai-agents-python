from openai import OpenAI

client = OpenAI()
history = []


def turn(text):
    history.append({"role": "user", "content": text})
    prompt = f"Conversation so far: {history}"
    return client.chat.completions.create(model="m", messages=[{"role": "user", "content": prompt}])
