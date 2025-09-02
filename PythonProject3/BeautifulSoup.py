import requests
from bs4 import BeautifulSoup

# Target URL for local events
url = "https://www.nmbt.co.za/events.html"

# Send HTTP request
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find event titles (based on observed HTML structure)
events = soup.find_all('div', class_='event_title')

print("🎉 Upcoming Events in Nelson Mandela Bay:\n")
for i, event in enumerate(events[:10], start=1):  # Limit to first 10 events
    title = event.get_text(strip=True)
    print(f"{i}. {title}")