import torch.nn as nn

class HandNetwork(nn.Module):
    """
    Neural Network that is used to predict gestures given hand landmark coordinates (which can be extracted using Google's Mediapipe module)
    """
    def __init__(self, classes):
        super(HandNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(42, 120)
        self.fc2 = nn.Linear(120, 100)
        self.fc3 = nn.Linear(100, 100)
        self.fc4 = nn.Linear(100, len(classes))
    def forward(self, x):
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x