import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import List, Dict

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Update this with your frontend URL when hosting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "resume-qa-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    ) 
    )
index = pc.Index(index_name)
def populate_index():
    with open("qa_pairs.txt", "r") as f:
        qa_pairs = f.read().split("\n\n")
    
    for i, qa_pair in enumerate(qa_pairs):
        parts = qa_pair.split("\nA: ")
        if len(parts) != 2:
            print(f"Skipping malformed QA pair: {qa_pair}")
            continue
        q, a = parts
        q = q.replace("Q: ", "")
        text = f"Question: {q}\nAnswer: {a}"
        embedding = get_embedding(text)
        index.upsert(vectors=[{
            "id": f"qa_{i}",
            "values": embedding,
            "metadata": {"content": text}
        }])
    print(f"Populated index with {len(qa_pairs)} QA pairs")

# Call the function to populate the index when the app starts
populate_index()
class Message(BaseModel):
    text: str

class Conversation(BaseModel):
    id: uuid.UUID
    messages: List[Dict[str, str]]

conversations: Dict[uuid.UUID, Conversation] = {}

def get_or_create_conversation(conversation_id: uuid.UUID = None):
    if conversation_id is None or conversation_id not in conversations:
        conversation_id = uuid.uuid4()
        conversations[conversation_id] = Conversation(id=conversation_id, messages=[])
    return conversations[conversation_id]

@app.post("/chat")
async def chat(message: Message, conversation: Conversation = Depends(get_or_create_conversation)):
    conversation.messages.append({"role": "user", "content": message.text})
    
    user_embedding = get_embedding(message.text)
    results = index.query(vector=user_embedding, top_k=3, include_metadata=True)
    context = "\n".join([match['metadata']['content'] for match in results['matches']])

    prompt = f"""
    You are an AI assistant representing Shubham Gupta. Answer questions based on the provided context and conversation history. If you don't have enough information to answer accurately, try to provide a relevant response based on the available information. Keep your answers concise, ideally no more than 2-3 sentences.

    Context:
    {context}

    Conversation history:
    {' '.join([f"{m['role']}: {m['content']}" for m in conversation.messages[:-1]])}

    Question: {message.text}

    Answer:
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant representing Shubham Gupta. Answer based on the provided information and context."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_response = completion.choices[0].message.content.strip()
    conversation.messages.append({"role": "assistant", "content": ai_response})

    # Generate suggested questions
    suggested_questions_prompt = f"""
    Based on the previous conversation, the last answer, and the context provided, suggest 3 brief follow-up questions that the user might want to ask next. Each question should be no longer than 10 words and should be directly related to the information about Shubham Gupta or the conversation history. Do not include numbers or prefixes in the questions. Never give response in list like 1. 2. 3. etc. or with questions inside double quotes"" "" Always given line seperated answers.

    Context:
    {context}

    Previous conversation:
    {' '.join([f"{m['role']}: {m['content']}" for m in conversation.messages])}

    Suggested questions:
    """

    suggested_questions_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to generate relevant follow-up questions about Shubham Gupta based on the resume and conversation history."},
            {"role": "user", "content": suggested_questions_prompt}
        ]
    )

    suggested_questions = suggested_questions_completion.choices[0].message.content.strip().split('\n')
    suggested_questions = [q.strip() for q in suggested_questions if q.strip()]
    
    return {
        "response": ai_response,
        "conversation_id": conversation.id,
        "suggested_questions": suggested_questions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)