import os
from tea.params import PATH

texts = [
    "This is a test sentence. This is another test sentence.",
    "This is a test sentence. This is another test sentence.",
    "This is a test sentence. This is another test sentence.",
    "This is a test sentence. This is another test sentence.",
    "This is a test sentence. This is another test sentence.",
    "This is a test sentence. This is another test sentence.",
]

print(len(texts[0:40]))

# for chunk in range(0, len(texts), 4):
#     print(len(texts[chunk:chunk+4]))