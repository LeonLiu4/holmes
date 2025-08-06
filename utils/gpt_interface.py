from openai import OpenAI

def analyze_chat_log(chat_log, prompt, api_key):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": chat_log}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content
