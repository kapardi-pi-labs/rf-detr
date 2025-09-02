from rfdetr import RFDETRLarge
import supervision as sv
from PIL import Image
from tqdm import tqdm
from supervision.metrics import MeanAveragePrecision
import matplotlib.pyplot as plt
from rfdetr.util.coco_classes import COCO_CLASSES
from collections import defaultdict
import random
import numpy as np
import seaborn as sns
import json

# Load the fine-tuned model
model = RFDETRLarge(pretrain_weights='/data/kapardi/models/rf-detr/output/checkpoint_best_total.pth')
model.optimize_for_inference()
# Set up the dataset
dataset = "/shared/kapardi/object_detection_data/data_corpus_240725"

# Path to your COCO annotations
annotations_path = f"{dataset}/valid/_annotations.coco.json"

with open(annotations_path, "r") as f:
    coco_data = json.load(f)

# Add 'iscrowd': 0 if missing in any annotation
for ann in coco_data.get("annotations", []):
    if "iscrowd" not in ann:
        ann["iscrowd"] = 0
    if "area" not in ann:
        # Attempt to compute area from bbox if possible
        if "bbox" in ann and len(ann["bbox"]) == 4:
            _, _, width, height = ann["bbox"]
            ann["area"] = width * height
        else:
            ann["area"] = 0  # fallback default (not ideal, but avoids crash)

# Optionally overwrite or save to a temporary file
with open(annotations_path, "w") as f:
    json.dump(coco_data, f)

ds = sv.DetectionDataset.from_coco(
    images_directory_path=f"{dataset}/valid",
    # annotations_path="/data/kapardi/rf-detr/rf_detr_pi_sense/filtered_data.json",
    annotations_path=f"{dataset}/valid/_annotations.coco.json",
)

targets = []
predictions = []
category_samples = defaultdict(list)

# Perform predictions and store results

for path, image, annotations in tqdm(ds):
    image = Image.open(path)
    if image.mode == 'L':  # Convert grayscale images to RGB
        image = image.convert("RGB")
    detections = model.predict(image, threshold=0.5)

    targets.append(annotations)
    predictions.append(detections)

    # Track samples per category
    for class_id in set(annotations.class_id.tolist()):
        category_samples[class_id].append((path, image, annotations, detections))

# Compute Mean Average Precision (mAP)
map_metric = MeanAveragePrecision()
map_result = map_metric.update(predictions, targets).compute()

# Plot and save mAP result
map_result.plot()
plt.savefig("map_result_plot_31072025_test.png")
plt.close()

# Compute and plot Confusion Matrix (full dataset)
confusion_matrix = sv.ConfusionMatrix.from_detections(
    predictions=predictions,
    targets=targets,
    classes=ds.classes
)

# confusion_matrix.plot()
# plt.savefig("confusion_matrix_plot_10072025_test.png")
# plt.close()

# Plot with normalization and custom colormap


# Extract raw matrix and class names
cm = confusion_matrix.matrix.astype(np.float32)
class_names = ds.classes

# Normalize the matrix (row-wise)
cm_normalized = cm / (cm.sum(axis=1, keepdims=True) + 1e-6)  # Avoid division by zero

# Create heatmap
plt.figure(figsize=(20, 20))
sns.heatmap(
    cm_normalized,
    annot=True,
    fmt=".2f",
    cmap="Blues",           # Use "viridis", "Blues", etc. for other color styles
    xticklabels=class_names,
    yticklabels=class_names
)

# Labels and formatting
plt.title("Confusion Matrix", fontsize=15)
plt.xlabel("Predicted Class", fontsize=15)
plt.ylabel("True Class", fontsize=15)
plt.xticks(rotation=45, fontsize=15)
plt.yticks(fontsize=15)
plt.tight_layout()

# Save
plt.savefig("confusion_matrix_31072025.png")
plt.close()
