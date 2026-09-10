import httpx

url = "https://jsonplaceholder.typicode.com/todos/1"
with httpx.Client(timeout=10.0) as client:
    r = client.get(url, params={"from": "day03"})
    print("status:", r.status_code)
    print("content-type:", r.headers.get("content-type"))
    data = r.json()
    print("url echoed:", data)
