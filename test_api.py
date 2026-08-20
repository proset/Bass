import os
import sys

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

# Clean up ANTHROPIC_API_KEY if it contains weird space characters
if 'ANTHROPIC_API_KEY' in os.environ:
    key = os.environ['ANTHROPIC_API_KEY']
    if 'R E V' in key:
        key = key.split('R E V')[0].strip()
    os.environ['ANTHROPIC_API_KEY'] = key

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

print("Testing Gemini...")
try:
    from google import genai
    print("google-genai is installed!")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in 3 words"
    )
    print("Gemini response:", response.text)
except Exception as e:
    print("Gemini failed:", e)

print("Testing Claude...")
try:
    import anthropic
    print("anthropic is installed!")
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello in 3 words"}]
    )
    print("Claude response:", "".join(block.text for block in response.content if getattr(block, "type", "") == "text"))
except Exception as e:
    print("Claude failed:", e)
