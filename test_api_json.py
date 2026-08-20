import os
from google import genai
from google.genai import types

# load keys
if os.path.exists('.env'):
    with open('.env', 'rb') as f:
        content = f.read().replace(b'\x00', b'')
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('utf-16', errors='ignore')
        for line in text.splitlines():
            if '=' in line:
                name, val = line.strip().split('=', 1)
                os.environ[name.strip()] = val.strip()

secrets_path = os.path.join('.streamlit', 'secrets.toml')
if os.path.exists(secrets_path):
    import toml
    try:
        secrets = toml.load(secrets_path)
        if 'gemini' in secrets:
            key = secrets['gemini'].get('api_key') or secrets.get('gemini_api_key')
            if key:
                os.environ['GEMINI_API_KEY'] = key
    except Exception as e:
        print(f"Error loading secrets.toml: {e}")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print("Sending request...")
prompt = "List 3 colors in a JSON list of strings."
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        max_output_tokens=1000,
        temperature=0,
        response_mime_type="application/json"
    )
)
print("Response:", response.text)
