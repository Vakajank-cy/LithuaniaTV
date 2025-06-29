from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pymongo import MongoClient
import uuid
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'lithuanian_tv')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
channels_collection = db.channels
programs_collection = db.programs

# Models
class Channel(BaseModel):
    id: str
    name: str
    logo: str
    stream_url: str
    category: str
    language: str
    description: str
    is_live: bool = True

class Program(BaseModel):
    id: str
    channel_id: str
    title: str
    description: str
    start_time: str
    end_time: str
    genre: str

# Initialize default Lithuanian channels
@app.on_event("startup")
async def startup_event():
    # Check if channels already exist
    if channels_collection.count_documents({}) == 0:
        default_channels = [
            {
                "id": str(uuid.uuid4()),
                "name": "LRT Televizija",
                "logo": "https://images.unsplash.com/photo-1597432683665-4988f859868f?w=200",
                "stream_url": "https://lrt.lt/stream", # Official LRT stream
                "category": "National",
                "language": "Lithuanian",
                "description": "Lithuania's national public broadcaster",
                "is_live": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "LNK",
                "logo": "https://images.pexels.com/photos/8254894/pexels-photo-8254894.jpeg?w=200",
                "stream_url": "https://lnk.lt/stream", # Official LNK stream
                "category": "Commercial",
                "language": "Lithuanian", 
                "description": "Free and independent Lithuanian channel",
                "is_live": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "LRT Plius",
                "logo": "https://images.unsplash.com/photo-1714623282496-9571c28f7722?w=200",
                "stream_url": "https://lrt.lt/stream/plius",
                "category": "Cultural",
                "language": "Lithuanian",
                "description": "LRT's cultural and educational channel",
                "is_live": True
            }
        ]
        
        for channel in default_channels:
            channels_collection.insert_one(channel)
        
        # Add sample programs
        sample_programs = [
            {
                "id": str(uuid.uuid4()),
                "channel_id": default_channels[0]["id"],
                "title": "Žinios",
                "description": "Daily news program",
                "start_time": "19:00",
                "end_time": "19:30",
                "genre": "News"
            },
            {
                "id": str(uuid.uuid4()),
                "channel_id": default_channels[1]["id"],
                "title": "LNK Žinios",
                "description": "Evening news",
                "start_time": "18:30",
                "end_time": "19:00",
                "genre": "News"
            }
        ]
        
        for program in sample_programs:
            programs_collection.insert_one(program)

# API Routes
@app.get("/api/channels")
async def get_channels():
    """Get all available channels"""
    channels = list(channels_collection.find({}, {"_id": 0}))
    return {"channels": channels}

@app.get("/api/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get specific channel details"""
    channel = channels_collection.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@app.get("/api/channels/{channel_id}/programs")
async def get_channel_programs(channel_id: str):
    """Get programs for a specific channel"""
    programs = list(programs_collection.find({"channel_id": channel_id}, {"_id": 0}))
    return {"programs": programs}

@app.get("/api/programs/now")
async def get_current_programs():
    """Get currently playing programs across all channels"""
    current_time = datetime.now().strftime("%H:%M")
    # For demo purposes, return sample current programs
    programs = list(programs_collection.find({}, {"_id": 0}))
    return {"current_programs": programs}

@app.get("/api/stream/{channel_id}")
async def get_stream_url(channel_id: str):
    """Get streaming URL for a specific channel"""
    channel = channels_collection.find_one({"id": channel_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return {
        "channel": channel["name"],
        "stream_url": channel["stream_url"],
        "is_live": channel["is_live"]
    }

@app.post("/api/channels")
async def add_channel(channel: Channel):
    """Add a new channel"""
    channel_dict = channel.dict()
    channels_collection.insert_one(channel_dict)
    return {"message": "Channel added successfully", "channel": channel_dict}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Lithuanian TV Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)