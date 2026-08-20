import urllib.request
import urllib.parse
import re

def search(query):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        links = re.findall(r'<a class="result__url" href="([^"]+)">([^<]+)</a>', html)
        return links
    except Exception as e:
        return str(e)

print("--- 900M ---")
print(search('site:openai.com "900 million" "weekly active users"'))
print("--- 800M ---")
print(search('site:openai.com "800 million" "weekly active users"'))
print("--- 900M theinformation ---")
print(search('site:theinformation.com "900 million" "weekly active users" openai'))
print("--- 800M theinformation ---")
print(search('site:theinformation.com "800 million" "weekly active users" openai'))
