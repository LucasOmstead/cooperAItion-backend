import pandas as pd

# Define the file paths
input_file = "input.csv"  # Replace with your actual file path
output_file = "output.csv"  # Replace with desired output file path

# Define the offset value
offset = 240  # Change this value to whatever you want to add

# Load the CSV file
df = pd.read_csv(input_file, header=None)

# Add the offset to the first column (config_id)
df[0] = df[0] + offset

# Save the modified CSV
df.to_csv(output_file, index=False, header=False)

print(f"Updated CSV saved as {output_file}")
