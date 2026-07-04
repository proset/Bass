import urllib.request
import pandas as pd
import tempfile
import os

url = "https://ourworldindata.org/grapher/technology-adoption-by-households-in-the-united-states.csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read()
        
    fd, temp_path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, 'wb') as f:
        f.write(content)
        
    df = pd.read_csv(temp_path)
    entities = df['Entity'].unique().tolist()
    print(f"\nFound {len(entities)} unique technology entities:")
    for i, ent in enumerate(sorted(entities)):
        print(f"- {ent}")
        
    os.remove(temp_path)
except Exception as e:
    print(f"Error: {e}")
