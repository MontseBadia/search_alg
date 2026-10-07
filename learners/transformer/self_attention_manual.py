import torch

# Notes:
# Implements raw attention
# - No batch dimension, otherwise I'd have to change the K.T

if __name__ == "__main__":
    torch.manual_seed(0)

    # 3 token vectors -----
    X = torch.randn(3, 4)
    print(X.shape)

    # Projection Matrices ------
    W_Q = torch.randn(4, 2)
    W_K = torch.randn(4, 2)
    W_V = torch.randn(4, 2)

    Q = X @ W_Q
    K = X @ W_K
    V = X @ W_V

    print(Q, Q.shape)
    print(K, K.shape)
    print(V, V.shape)

    # Attention Scores ------
    scores = Q @ K.T
    print("--attention scores--")
    print(scores, scores.shape)

    # Scale ------
    # Gives the size of the last dimension, which is the query/key dimension (2)
    d_k = Q.shape[-1]
    scaled_scores = scores / (d_k ** 0.5)

    # Masking ------
    seq_len = X.shape[0]
    # Returns upper triangular part of a matrix
    mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool), diagonal=1)
    print("--mask--")
    print(mask)

    # Fills value when mask item is True
    masked_scores = scaled_scores.masked_fill(mask, float("-inf"))
    print("--masked scores--")
    print(masked_scores)

    # Softmax ------
    # dim=1 to apply softmax across the keys of each query
    attention = torch.softmax(masked_scores, dim=1)
    print("--attention--")
    print(attention)
    print(attention.sum(dim=1))

    # Output ------
    output = attention @ V
    print("--output--")
    print(output, output.shape)


