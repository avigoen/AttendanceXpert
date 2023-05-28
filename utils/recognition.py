import torch, json
import torchvision.transforms as transforms
from PIL import Image
from utils.Models.resnet import ResnetModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ]
)

labels = None
with open("static/labels.json", "r") as f:
    data = json.load(f)
    labels = {int(k): v for k, v in data.items()}


def _get_model():
    model_resnet = ResnetModel(119, device)
    model_resnet.setup(0.001)
    model_resnet.load_state_dict(torch.load("outputs/V2/resnet_classifier.pth"))
    return model_resnet.cnn.eval()

FACE_MODEL = _get_model()

def recognise(faces):
    # model = _get_model()
    identities = []
    for idx, face in enumerate(faces):
        img = Image.fromarray(face)
        img = TRANSFORM(img)
        img = img.unsqueeze(0)
        img = img.to(device)
        output = FACE_MODEL(img)
        _, label = output.max(1)
        output = label.item()
        name = labels[output]
        identities.append({"index": idx, "label": output, 'name': name})
    return identities
