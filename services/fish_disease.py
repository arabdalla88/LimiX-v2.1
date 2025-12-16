import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # for Windows

import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
from torchvision import transforms
from PIL import Image

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model ONCE
_model = None

def _load_model():
    global _model
    if _model is None:
        model_path = "models/fish_disease.pth"
        _model = EfficientNet.from_name("efficientnet-b3")
        _model._fc = nn.Linear(_model._fc.in_features, 2)
        _model.load_state_dict(torch.load(model_path, map_location=device))
        _model.to(device)
        _model.eval()
        print("✅ Fish health model loaded")

def predict_fish_health(image_file):
    """
    Input: file path OR file-like object (e.g., from Flask request)
    Output: dict with prediction
    """
    _load_model()  # لو مش محمل، يحمله
    
    # Open image
    img = Image.open(image_file).convert("RGB")
    
    # Preprocess (EfficientNet-B3 needs 300x300)
    transform = transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = transform(img).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = _model(image)
        probs = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)
    
    classes = ["FreshFish", "InfectedFish"]
    pred_class = classes[predicted.item()]
    conf = round(confidence.item() * 100, 2)
    
    return {
        "status": "healthy" if pred_class == "FreshFish" else "sick",
        "confidence": conf,
        "prediction": pred_class
    }