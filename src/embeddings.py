import torch
import os
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
from src.config import TEXT_MODEL_NAME, CLIP_MODEL_NAME

_text_model = None
_clip_model = None
_clip_processor = None

def get_text_model():
    global _text_model
    if _text_model is None:
        _text_model = SentenceTransformer(TEXT_MODEL_NAME)
    return _text_model

def get_clip():
    global _clip_model, _clip_processor
    if _clip_model is None or _clip_processor is None:
        _clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
        _clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    return _clip_model, _clip_processor

def generate_text_embedding(text: str) -> list:
    model = get_text_model()
    embedding = model.encode(text).tolist()
    return embedding

def generate_image_embedding_from_file(image_path: str):
    """Generates a 512-dim CLIP embedding if the image file exists; returns None otherwise."""
    if not image_path or str(image_path).lower() in ['none', 'nan', '']:
        return None

    # Resolve absolute path
    abs_path = os.path.abspath(image_path)

    if not os.path.exists(abs_path):
        print(f"  ❌ Image path not found on disk: {abs_path}")
        return None

    try:
        model, processor = get_clip()
        image = Image.open(abs_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            
            # Unwrap tensor if wrapped inside BaseModelOutputWithPooling
            if hasattr(outputs, 'image_embeds'):
                image_features = outputs.image_embeds
            elif hasattr(outputs, 'pooler_output'):
                image_features = outputs.pooler_output
            else:
                image_features = outputs
            
        # L2 Normalize the tensor vector safely
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.squeeze().tolist()
    except Exception as e:
        print(f"  ⚠️ Error generating image embedding for {abs_path}: {e}")
        return None
    
def generate_clip_text_embedding(text: str) -> list:
    """Generates a 512-dim CLIP text embedding for text-to-image similarity search."""
    model, processor = get_clip()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    
    with torch.no_grad():
        outputs = model.get_text_features(**inputs)
        # Handle both tensor and BaseModelOutputWithPooling outputs
        features = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs
        if hasattr(outputs, 'text_embeds'):
            features = outputs.text_embeds
            
    # Normalize tensor vector
    features = features / features.norm(dim=-1, keepdim=True)
    return features.squeeze().tolist()