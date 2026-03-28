import requests
import json

url = 'https://api.makcorps.com/free/london'
headers = {
    'Authorization': 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MTc2NzczNjAsImlkZW50aXR5IjozLCJuYmYiOjE1MTc2NzczNjAsImV4cCI6MTUxNzY3OTE2MH0.ytSqQj3VDymEaJz9EIdskWELwDQZRD1Dbo6TuHaPz9U'
}

print(f"Testing {url} ...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status:", response.status_code)
    try:
        data = response.json()
        print(json.dumps(data, indent=2)[:500] + "...")
    except:
        print("Raw text:", response.text[:500])
except Exception as e:
    print("Error:", e)
