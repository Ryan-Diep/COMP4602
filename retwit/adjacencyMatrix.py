import numpy as np
import pandas as pd

def create_adjacency_matrix(users):
    # Extract all unique user IDs
    user_ids = [user["user_id"] for user in users]
    user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}

    # Initialize an adjacency matrix with zeros
    n = len(user_ids)
    adjacency_matrix = np.zeros((n, n), dtype=int)

    # Populate the adjacency matrix
    for user in users:
        user_id = user["user_id"]
        user_idx = user_index[user_id]

        # Mark connections for "following"
        for following in user.get("following", []):
            following_id = following["id"]
            if following_id in user_index:
                following_idx = user_index[following_id]
                adjacency_matrix[user_idx][following_idx] = 1

        # Mark connections for "followers"
        for follower in user.get("followers", []):
            follower_id = follower["id"]
            if follower_id in user_index:
                follower_idx = user_index[follower_id]
                adjacency_matrix[follower_idx][user_idx] = 1

    # Convert to a DataFrame for better readability
    adjacency_df = pd.DataFrame(adjacency_matrix, index=user_ids, columns=user_ids)
    return adjacency_df
