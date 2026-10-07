import torch
import torch.nn as nn

# Notes:
# Implements attention as module

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
        mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=X.device), diagonal=1)
        masked_scores = scaled_scores.masked_fill(mask, float("-inf"))
        attention = torch.softmax(masked_scores, dim=-1)
        head_output = attention @ V

        # output projection
        projected_output = self.W_O(head_output)
        residual = X + projected_output

        return residual, attention



if __name__ == "__main__":
    torch.manual_seed(0)
    X = torch.randn(3, 4)

    # Attention
    attention_layer = SelfAttention(d_model=4, d_head=2)
    output, attention = attention_layer(X)

    print("attention")
    print(attention)
    print("\noutput")
    print(output)