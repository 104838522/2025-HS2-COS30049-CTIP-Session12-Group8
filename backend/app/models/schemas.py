# Pydantic models for request and response schemas
from pydantic import BaseModel
from typing import Optional, List, Dict


class SignupIn(BaseModel):
    name: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class Highlight(BaseModel):
    line: int
    score: float
    snippet: str


class AnalyzeOut(BaseModel):
    result: str
    confidence: Optional[float]
    processing_time_sec: float
    timestamp: str
    highlights: Optional[List[dict]] = None


class UpdateUserIn(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
