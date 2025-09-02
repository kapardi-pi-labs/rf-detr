import wandb
from rfdetr import RFDETRLarge
import pandas as pd

# Initialize WandB
wandb.init(project="object_detection_training", name="detr_train_classes_28")
model = RFDETRLarge()

history = []

def callback2(data):
    history.append(data)
    
    # Log training and validation loss
    wandb.log({
        "epoch": data["epoch"],
        "train_loss": data["train_loss"],
        "val_loss": data["test_loss"],
        "avg_precision": data["test_coco_eval_bbox"][0],  # AP (IoU=0.50:0.95)
        "avg_recall": data["test_coco_eval_bbox"][6]  # AR (IoU=0.50:0.95, maxDets=1)
    })

model.callbacks["on_fit_epoch_end"].append(callback2)

# Train model
model.train(dataset_dir='/shared/kapardi/object_detection_data/data_corpus_240725',
            epochs=10,
            batch_size=4,
            grad_accum_steps=1,
            num_workers=3,
            lr=1e-5,
            multi_scale=True, 
            expanded_scales=True,
            num_classes=28
            )


# Finish WandB logging
wandb.finish()
