import sys
from typing import List, Optional, TypedDict

sys.dont_write_bytecode = True


class GeneratedSingleImage(TypedDict):
    id: str
    url: str
    nsfw: bool

class CustomModel(TypedDict):
    id: str
    userId: str
    name: str
    modelHeight: int
    modelWidth: int

class GeneratedImage(TypedDict):
    model_id: str
    scheduler: str
    coreModel: str
    sdVersion: str
    prompt: str
    negativePrompt: Optional[str] = None
    id: str
    status: str
    quantity: int
    createdAt: str
    public: bool
    nsfw: bool
    custom_model: CustomModel
    generated_images: List[GeneratedSingleImage]