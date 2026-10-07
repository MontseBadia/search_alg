import torch
from torch import nn

# -- TOKEN EMBEDDINGS --

# We'll define a vocabulary of 8 items (for modulo 7): 0, 1, 2, 3, 4, 5, 6, =
# We'll define 4 features per token
d_voc = 8
d_model = 4

# Create embedding table
# This will store 8 learned vectors, each of length 4
token_embedding = nn.Embedding(d_voc, d_model)


# -- POSITIONAL EMBEDDINGS --

# We'll define 3 positions
d_pos = 3

# Create embedding table
position_embedding = nn.Embedding(d_pos, d_model)


if __name__ == "__main__":
    tokens = torch.tensor([5, 4, 7])  # use 7 as the ID for "="
    X = token_embedding(tokens)
    print(X.shape)

    positions = torch.tensor([0, 1, 2])
    pos = position_embedding(positions)
    print(pos.shape)

    X = token_embedding(tokens) + position_embedding(positions)
    print(X.shape)
