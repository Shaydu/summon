import requests

url = "http://10.0.0.19:8000/nfc-event"
payload = {"token_id": "123", "player": "WiryHealer4014", "action": "give_diamond_sword"}
headers = {"x-api-key": "super-secret-test-key22"}

resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.json())
