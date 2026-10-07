import torch
import torch.nn as nn

# Notes:
# Implements transformer as module
# Self attention usually perserves: batch size and sequence length


class MyTransformer(nn.Module):
    def __init__(self, d_model, d_head, d_mlp, d_voc, d_pos, p):
        super().__init__()

        self.token_embedding = nn.Embedding(d_voc, d_model)
        self.position_embedding = nn.Embedding(d_pos, d_model)

        self.block = TransformerBlock(
            d_model=d_model,
            d_head=d_head,
            d_mlp=d_mlp
        )

        self.classifier = nn.Linear(d_model, p)

    def forward(self, X, pos):
        X = self.token_embedding(X) + self.position_embedding(pos)
        output, attention = self.block(X)

        # Classifies using final token representation
        logits = self.classifier(output[-1])

        return logits, attention
    

class TransformerBlock(nn.Module):
    def __init__(self, d_model, d_head, d_mlp):
        super().__init__()

        self.attention = SelfAttention(d_model, d_head)

        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_mlp),
            nn.ReLU(),
            nn.Linear(d_mlp, d_model)
        )

    def forward(self, X):
        X, attention = self.attention(X)

        mlp_output = self.mlp(X)
        X = X + mlp_output

        return X, attention
        

class SelfAttention(nn.Module):
    # d_model -> size of input token
    # d_head -> size of token inside head
    def __init__(self, d_model, d_head):
        super().__init__()

        self.W_Q = nn.Linear(d_model, d_head, bias=False)
        self.W_K = nn.Linear(d_model, d_head, bias=False)
        self.W_V = nn.Linear(d_model, d_head, bias=False)

        # Used to project output into original model space
        self.W_O = nn.Linear(d_head, d_model, bias=False)

        self.d_head = d_head

    def forward(self, X):
        Q = self.W_Q(X)
        K = self.W_K(X)
        V = self.W_V(X)

        scores = Q @ K.transpose(-2, -1)
        scaled_scores = scores / (self.d_head ** 0.5)
        seq_len = X.shape[-2] # Gets sequence dimension
        # Set device for later GPU use
        mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=X.device), diagonal=1)
        masked_scores = scaled_scores.masked_fill(mask, float("-inf"))
        # dim should be -1
        attention = torch.softmax(masked_scores, dim=-1)
        head_output = attention @ V

        # output projection
        projected_output = self.W_O(head_output)
        residual = X + projected_output

        return residual, attention



if __name__ == "__main__":
    torch.manual_seed(0)

    tokens = torch.tensor([5, 4, 7])
    positions = torch.tensor([0, 1, 2])

    # Config
    d_voc = 8
    d_pos = 3
    d_model = 4
    d_head = 2
    d_mlp = 8
    p = 7 # How many possible output logits

    transformer = MyTransformer(d_model, d_head, d_mlp, d_voc, d_pos, p)
    logits, attention = transformer(tokens, positions)

    print(logits)

    # LOSS
    loss_fn = nn.CrossEntropyLoss()
    target = torch.tensor(2)
    # Cross entropy loss works with batches, it needs the logits as (batches, classes)
    # and the target as (1,) one target per batch item
    loss = loss_fn(logits.unsqueeze(0), target.unsqueeze(0))

    print(loss)