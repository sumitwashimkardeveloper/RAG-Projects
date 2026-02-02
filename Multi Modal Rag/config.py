import os
from typing import Dict, Any

class Config:
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME = "multi-modal-rag"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv"}
    SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".flac", ".aac"}
    SUPPORTED_DOC_FORMATS = {".pdf", ".docx", ".pptx"}

    TEMP_DIR = "./temp_media"

    OCR_ENABLED = True
    OBJECT_DETECTION_ENABLED = True
    AUDIO_TRANSCRIPTION_ENABLED = True
    VIDEO_FRAME_SAMPLING = 5

class MediaTypeConfig:
    MEDIA_PROCESSORS: Dict[str, Any] = {
        "image": {
            "enabled": True,
            "extract_text": True,
            "extract_objects": True,
            "chunk_strategy": "spatial"
        },
        "table": {
            "enabled": True,
            "extract_structure": True,
            "chunk_strategy": "row-based"
        },
        "chart": {
            "enabled": True,
            "extract_data": True,
            "extract_labels": True,
            "chunk_strategy": "semantic"
        },
        "video": {
            "enabled": True,
            "frame_sampling": 5,
            "extract_audio": True,
            "chunk_strategy": "temporal"
        },
        "audio": {
            "enabled": True,
            "transcription": True,
            "voice_fingerprint": True,
            "chunk_strategy": "temporal"
        },
        "powerpoint": {
            "enabled": True,
            "extract_slides": True,
            "extract_speaker_notes": True,
            "chunk_strategy": "slide-based"
        }
    }
