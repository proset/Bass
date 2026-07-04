import urllib.request
import pandas as pd
import tempfile
import os

url = "https://ourworldindata.org/grapher/technology-adoption-by-households-in-the-united-states.csv"
print(f"Downloading dataset from {url} with custom User-Agent...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read()
        
    # Write to a temp file
    fd, temp_path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, 'wb') as f:
        f.write(content)
        
    df = pd.read_csv(temp_path)
    print("\nDataset loaded successfully!")
    print(f"Total rows: {len(df)}")
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    
    metric_cols = [c for c in df.columns if c not in ['Entity', 'Code', 'Year']]
    print("\nAvailable Technologies (Columns):")
    for i, c in enumerate(metric_cols):
        print(f"{i+1}. {c}")
        
    # Clean up
    os.remove(temp_path)
except Exception as e:
    print(f"Error: {e}")
