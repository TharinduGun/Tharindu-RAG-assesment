"""
Data models used by the RAG API.
These models define the structure of requests and responses
for the /ask endpoint.
"""
from pydantic import BaseModel

class Question(BaseModel):
    question: str #user entered question in str format

class AnswerResponse(BaseModel):
    question: str
    answer: str
    context: str #answer generated from the context in str format
