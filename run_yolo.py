import os
import torch

print("CWD:", os.getcwd())
weights = r"C:\path\to\yolov5s.pt"   # use full absolute path to be safe
model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights, force_reload=False)

# run on an image
results = model(r"C:\path\to\test_image.jpg")
results.print()
results.save()  # saves to runs/detect/exp by default
