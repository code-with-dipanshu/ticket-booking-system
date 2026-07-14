import requests

BASE='http://127.0.0.1:8000'
login = requests.post(f'{BASE}/api/v1/auth/login', data={'username':'customer@booking.com','password':'secret123'})
print('login', login.status_code)
token = login.json().get('access_token')
headers={'Authorization': f'Bearer {token}'}
print('token len', len(token or ''))
resp = requests.post(f'{BASE}/api/v1/bookings', json={'event_id':1,'seat_category_id':1,'quantity':1}, headers={**headers,'Content-Type':'application/json'})
print('booking status', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('parse error', e, resp.text[:1000])
