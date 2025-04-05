import pandas as pd

# Replace 'your_file.json' with the path to your JSON file
file_path = '../users_following.json'

# Read the JSON file into a pandas DataFrame
df = pd.read_json(file_path)





# Display the first few rows of the DataFrame
print(df.head())