import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained(
        "microsoft/trocr-base-handwritten"
    ).to(device)
    
    return processor, model

_processor = None
_model = None

def get_model():
    global _processor, _model
    
    if _processor is None or _model is None:
        _processor, _model = load_model()
        
    return _processor, _model