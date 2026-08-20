import urllib.request
import re

urls = [
    "https://openai.com/index/accelerating-the-next-phase-ai/",
    "https://openai.com/index/delivering-low-latency-voice-ai-at-scale/",
    "https://openai.com/index/openai-and-broadcom-announce-strategic-collaboration/",
]

import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for url in urls:
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8').lower()
        if '900 million' in html or '800 million' in html or 'weekly active' in html:
            print(f"Match found in {url}!")
            snippets = re.findall(r'.{0,50}(900 million|800 million|weekly active).{0,50}', html)
            for s in snippets:
                print("...", s, "...")
        else:
            print(f"No match in {url}")
    except Exception as e:
        print(f"Error {url}: {e}")
