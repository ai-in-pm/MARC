import os

# Base directory path
base_dir = r'c:/cc-working-dir/MARC'
# Create project directories
dirs = ['src', 'tests', 'examples']

for dir_name in dirs:
    full_path = os.path.join(base_dir, dir_name)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created directory: {full_path}")
