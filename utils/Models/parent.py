import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm


class ParentModel(nn.Module):
    def __init__(self, num_classes, device):
        super(ParentModel, self).__init__()
        self.num_classes = num_classes
        self._device = device

    def setup(self, lr):
        self.cnn = self.build_model()
        self.model = nn.DataParallel(
            self.cnn, device_ids=list(range(torch.cuda.device_count()))
        )
        self.criterion = nn.CrossEntropyLoss().to(self._device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.scheduler = ReduceLROnPlateau(
            self.optimizer, mode="min", factor=0.1, patience=5, verbose=True
        )

    def build_model(self):
        raise NotImplementedError()

    def _convert_predicted(self, predicted):
        predicted_onehot = torch.from_numpy(
            np.eye(self.num_classes)[predicted.detach().cpu().numpy()]
        ).to(self._device)
        return predicted_onehot

    def _train_fn(self, train_dataloader):
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        # Training phase
        self.model.train()
        for images, labels in tqdm(
            train_dataloader,
            bar_format="\033[31m{bar}\033[0m{percentage:3.0f}%|{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        ):
            images = images.to(self._device)
            labels = labels.to(self._device)

            self.optimizer.zero_grad()

            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            loss.backward()
            self.optimizer.step()

            train_loss += loss.item()
            _, predicted = outputs.max(1)
            predicted_onehot = self._convert_predicted(predicted)
            train_total += labels.size(0)
            train_correct += predicted_onehot.eq(labels).sum().item() / self.num_classes

        train_accuracy = 100.0 * train_correct / train_total
        train_loss /= len(train_dataloader)
        return train_accuracy, train_loss

    def _val_fn(self, val_dataloader):
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        self.model.eval()
        with torch.no_grad():
            for images, labels in tqdm(
                val_dataloader,
                bar_format="\033[32m{bar}\033[0m{percentage:3.0f}%|{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            ):
                images = images.to(self._device)
                labels = labels.to(self._device)

                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                predicted_onehot = self._convert_predicted(predicted)
                val_total += labels.size(0)
                val_correct += (
                    predicted_onehot.eq(labels).sum().item() / self.num_classes
                )

        val_accuracy = 100.0 * val_correct / val_total
        val_loss /= len(val_dataloader)
        return val_accuracy, val_loss

    def predict(self, X):
        y_pred = []
        with torch.no_grad():
            for image in X:
                image = image.to(self._device)
                output = self.model(image)
                _, pred = output.max(1)
                y_pred.append(pred)
        return y_pred

    def fit(self, train_loader, val_loader, ckpt_path, patience=10):
        # Initialize variables for early stopping
        best_val_loss = float("inf")
        epochs_without_improvement = 0

        accuracies = []
        losses = []

        early_stop = False
        epoch = 1
        while not early_stop:
            train_accuracy, train_loss = self._train_fn(train_loader)
            val_accuracy, val_loss = self._val_fn(val_loader)

            self.scheduler.step(val_loss)
            accuracies.append({"train": train_accuracy, "val": val_accuracy})
            losses.append({"train": train_loss, "val": val_loss})

            # Print epoch results
            print(f"Epoch {epoch}")
            print(
                f"Train Loss: {train_loss:.4f} | Train Accuracy: {train_accuracy:.2f}%"
            )
            print(f"Val Loss: {val_loss:.4f} | Val Accuracy: {val_accuracy:.2f}%")

            # Check for early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(self.state_dict(), ckpt_path)
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1
                if epochs_without_improvement == patience:
                    print(f"No improvement for {patience} epochs. Early stopping...")
                    early_stop = True
            epoch += 1
        return accuracies, losses
