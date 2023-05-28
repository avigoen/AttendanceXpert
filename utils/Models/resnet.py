import torch.nn as nn
from .parent import ParentModel
from torchvision.models import resnet50

class ResnetModel(ParentModel):
    def __init__(self, num_classes, device):
        super(ResnetModel, self).__init__(num_classes, device)
        pass

    def build_model(self):
        cnn = resnet50(weights='IMAGENET1K_V2')
        cnn.fc = nn.Linear(2048, self.num_classes)
        return cnn.to(self._device)