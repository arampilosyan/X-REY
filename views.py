import pickle
from pathlib import Path

import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

predict_labels = {
    0:"Normal",
    1:"Tuberculosis"
}
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATHS = [
    BASE_DIR / "main/model.pkl",
    BASE_DIR.parent / "main/model.pkl",
]
_MODEL = None
_MODEL_LOAD_ERROR = None


def _load_model():
    global _MODEL, _MODEL_LOAD_ERROR
    if _MODEL is not None or _MODEL_LOAD_ERROR is not None:
        return _MODEL
    try:
        for model_path in MODEL_PATHS:
            if model_path.exists():
                with model_path.open("rb") as model_file:
                    _MODEL = pickle.load(model_file)
                break
        if _MODEL is None:
            joined_paths = ", ".join(str(path) for path in MODEL_PATHS)
            _MODEL_LOAD_ERROR = f"model.pkl not found. Checked: {joined_paths}"
    except Exception as exc:
        _MODEL_LOAD_ERROR = str(exc)
    return _MODEL


def _preprocess_image(image_file):
    image = Image.open(image_file).convert("L").resize((150, 150))
    image_array = np.asarray(image, dtype=np.float32) / 255.0
    return image_array.reshape(1, 150, 150, 1)


def index(request):
    return render(request, "index.html")


@require_POST
def predict(request):
    model = _load_model()
    if model is None:
        return JsonResponse(
            {
                "error": "Model could not be loaded.",
                "detail": _MODEL_LOAD_ERROR or "Unknown model load error.",
            },
            status=500,
        )

    image_file = request.FILES.get("image")
    if image_file is None:
        return JsonResponse({"error": "No image uploaded."}, status=400)

    try:
        features = _preprocess_image(image_file)
        prediction = model.predict(features)

        value = prediction[0]
        print(value)
        if hasattr(value, "item"):
            
            value = predict_labels[np.argmax(value)]

        return JsonResponse({"prediction": str(value)})
    except Exception as exc:
        return JsonResponse({"error": "Prediction failed.", "detail": str(exc)}, status=500)