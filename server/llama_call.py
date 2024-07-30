from dotenv import load_dotenv
load_dotenv()

from groq import Groq
import json

client = Groq()


conversation_history = []
conversation_history.append({
                "role": "system",
                "content": "You are a helpful voice assistant with web search capability. You always return a JSON object with two keys ONLY ('need_search' and 'answer':). The first key contains either 'yes' or 'no' indicating whether you need a web search to answer the question. If the first key's value is 'yes', the second key contains an effective web search query. If the first key's value is 'no', the second key contains a concise answer to the question. YOU WILL BE PROVIDED CONTEXT ON THE QUERY, IF THAT CONTEXT HAS THE ANSWER, NO NEED TO WEB SEARCH. BUT ALWAYS DO WEB SEARCH FOR ANY REAL-TIME INFORMATION QUERY."
            })

def process(Query):
    conversation_history.append({"role": "user", "content": Query})
    
    chat_completion = client.chat.completions.create(
        messages=conversation_history,

        model="llama3-70b-8192",
        temperature=0,
        max_tokens=1024,
        seed=42,
        top_p=0.1,

        response_format={
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {"need_search": {"type": "string"}, "answer": {"type": "string"}},
                "required": ["need_search", "answer"],
            },
        }

    )
    data = chat_completion.choices[0].message.content
    
    conversation_history.append({"role": "assistant", "content": data})
    return json.loads(data)
