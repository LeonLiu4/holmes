import openai

def analyze_chat_log(chat_log, prompt, api_key):
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": chat_log}
        ],
        max_tokens=1000
    )
    return response['choices'][0]['message']['content']
