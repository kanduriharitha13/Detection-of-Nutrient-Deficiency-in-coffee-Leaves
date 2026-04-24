import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from collections import Counter
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# ================= CONFIG =================
DATASET_DIR = "dataset"
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS_STAGE1 = 6
EPOCHS_STAGE2 = 6
LEARNING_RATE_STAGE1 = 0.0003
LEARNING_RATE_STAGE2 = 0.00005

DEVICE = torch.device(
    "mps" if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)

# ================= TRAIN =================
def train():

    if not os.path.exists(DATASET_DIR):
        print("Dataset folder not found!")
        return

    print("Using device:", DEVICE)

    # -------- TRANSFORMS --------
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.75, 1.0)),
        transforms.RandomRotation(30),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.3, 0.3, 0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],
                             [0.229,0.224,0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],
                             [0.229,0.224,0.225])
    ])

    full_dataset = datasets.ImageFolder(DATASET_DIR)
    class_names = full_dataset.classes
    print("Classes:", class_names)

    # Save class map
    with open("class_indices.json", "w") as f:
        json.dump({c: i for i, c in enumerate(class_names)}, f)

    # Split dataset
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_subset, val_subset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size]
    )

    class TransformedSubset(torch.utils.data.Dataset):
        def __init__(self, subset, transform):
            self.subset = subset
            self.transform = transform

        def __len__(self):
            return len(self.subset)

        def __getitem__(self, idx):
            x, y = self.subset[idx]
            return self.transform(x), y

    train_set = TransformedSubset(train_subset, train_transform)
    val_set = TransformedSubset(val_subset, val_transform)

    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=BATCH_SIZE)

    # -------- MODEL --------
    model = models.mobilenet_v2(
        weights=models.MobileNet_V2_Weights.DEFAULT
    )

    # Replace classifier
    model.classifier[1] = nn.Linear(
        model.last_channel, len(class_names)
    )

    model.to(DEVICE)

    # -------- CLASS WEIGHTS --------
    labels = [full_dataset.targets[i] for i in train_subset.indices]
    class_counts = Counter(labels)
    total = sum(class_counts.values())

    weights = []
    for i in range(len(class_names)):
        weights.append(total / class_counts[i])

    weights = torch.tensor(weights).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights)

    # ==================================================
    # 🔥 STAGE 1 – Train classifier only
    # ==================================================
    print("\nStage 1: Training classifier...\n")

    for param in model.features.parameters():
        param.requires_grad = False

    optimizer = optim.Adam(model.classifier.parameters(),
                           lr=LEARNING_RATE_STAGE1)

    train_loop(model, train_loader, val_loader,
               criterion, optimizer, EPOCHS_STAGE1)

    # ==================================================
    # 🔥 STAGE 2 – Fine-tune last layers
    # ==================================================
    print("\nStage 2: Fine-tuning backbone...\n")

    for param in model.features[-4:].parameters():
        param.requires_grad = True

    optimizer = optim.Adam(filter(lambda p: p.requires_grad,
                                  model.parameters()),
                           lr=LEARNING_RATE_STAGE2)

    train_loop(model, train_loader, val_loader,
               criterion, optimizer, EPOCHS_STAGE2)

    torch.save(model.state_dict(), "plant_disease_model.pt")
    print("✅ Model saved successfully!")


# ================= TRAIN LOOP =================
def train_loop(model, train_loader, val_loader,
               criterion, optimizer, epochs):

    for epoch in range(epochs):

        for phase in ["train", "val"]:

            if phase == "train":
                model.train()
                loader = train_loader
            else:
                model.eval()
                loader = val_loader

            running_loss = 0
            running_corrects = 0

            for inputs, labels in loader:
                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels)

            epoch_loss = running_loss / len(loader.dataset)
            epoch_acc = running_corrects.float() / len(loader.dataset)

            print(f"{phase.upper()}  "
                  f"Loss: {epoch_loss:.4f}  "
                  f"Acc: {epoch_acc:.4f}")

        print("-" * 30)


if __name__ == "__main__":
    train()
