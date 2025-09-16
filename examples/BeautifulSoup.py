import requests
from bs4 import BeautifulSoup

url = "https://www.nmbt.co.za/events.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

events = soup.find_all('div', class_='event_title')

print("🎉 Upcoming Events in Nelson Mandela Bay:\n")
for i, event in enumerate(events[:10], start=1):
    title = event.get_text(strip=True)
    print(f"{i}. {title}")
