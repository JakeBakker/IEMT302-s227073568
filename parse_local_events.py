from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import List
import re

try:
    from bs4 import BeautifulSoup  # type: ignore
    _HAVE_BS4 = True
except Exception:
    BeautifulSoup = None  # type: ignore
    _HAVE_BS4 = False


HTML_CONTENT = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Local Events</title>
  </head>
  <body>
    <h1>What's happening nearby</h1>
    <section class=\"events\" aria-label=\"Upcoming local events\">
      <article class=\"event\" data-id=\"e001\">
        <h3>Sunset Yoga in the Park</h3>
        <div class=\"meta\">
          <time datetime=\"2025-09-20T18:30:00\" class=\"date\">Sat, Sep 20, 6:30 PM</time>
          <span class=\"location\">Riverside Park, Lawn B</span>
          <span class=\"price\">Free</span>
          <a class=\"tickets\" href=\"https://example.org/events/sunset-yoga\" target=\"_blank\" rel=\"noopener\">Details</a>
        </div>
        <p class=\"desc\">Bring a mat and water. All levels welcome.</p>
      </article>

      <article class=\"event\" data-id=\"e002\">
        <h3>Farmers' Market</h3>
        <div class=\"meta\">
          <time datetime=\"2025-09-21T09:00:00\" class=\"date\">Sun, Sep 21, 9:00 AM</time>
          <span class=\"location\">Old Town Square</span>
          <span class=\"price\">$</span>
          <a class=\"tickets\" href=\"https://example.org/events/farmers-market\" target=\"_blank\" rel=\"noopener\">Details</a>
        </div>
        <p class=\"desc\">Local produce, baked goods, and live music.</p>
      </article>

      <article class=\"event\" data-id=\"e003\">
        <h3>Indie Film Night</h3>
        <div class=\"meta\">
          <time datetime=\"2025-09-22T20:00:00\" class=\"date\">Mon, Sep 22, 8:00 PM</time>
          <span class=\"location\">Art House Cinema</span>
          <span class=\"price\">$$</span>
          <a class=\"tickets\" href=\"https://example.org/events/indie-film\" target=\"_blank\" rel=\"noopener\">Details</a>
        </div>
        <p class=\"desc\">Three short films by local directors + Q&A.</p>
      </article>

      <article class=\"event\" data-id=\"e004\">
        <h3>Coffee & Code Meetup</h3>
        <div class=\"meta\">
          <time datetime=\"2025-09-24T18:00:00\" class=\"date\">Wed, Sep 24, 6:00 PM</time>
          <span class=\"location\">Bean There Cafe</span>
          <span class=\"price\">Free</span>
          <a class=\"tickets\" href=\"https://example.org/events/coffee-code\" target=\"_blank\" rel=\"noopener\">Details</a>
        </div>
        <p class=\"desc\">Open discussion on Python and open source projects.</p>
      </article>
    </section>
  </body>
  </html>"""


@dataclass
class Event:
    event_id: str
    title: str
    date_iso: str
    date_text: str
    location: str
    price: str
    details_url: str
    description: str


def _parse_with_bs4(html: str) -> List[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events_section = soup.select_one("section.events")
    if not events_section:
        return []

    events: List[Event] = []
    for article in events_section.select("article.event"):
        event_id = article.get("data-id", "")
        title_el = article.select_one("h3")
        date_el = article.select_one("time.date")
        loc_el = article.select_one(".location")
        price_el = article.select_one(".price")
        link_el = article.select_one("a.tickets")
        desc_el = article.select_one(".desc")

        event = Event(
            event_id=event_id,
            title=(title_el.get_text(strip=True) if title_el else ""),
            date_iso=(date_el.get("datetime") if date_el else ""),
            date_text=(date_el.get_text(strip=True) if date_el else ""),
            location=(loc_el.get_text(strip=True) if loc_el else ""),
            price=(price_el.get_text(strip=True) if price_el else ""),
            details_url=(link_el.get("href") if link_el else ""),
            description=(desc_el.get_text(strip=True) if desc_el else ""),
        )

        events.append(event)

    return events


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _parse_with_regex(html: str) -> List[Event]:
    events: List[Event] = []

    article_pattern = re.compile(r'<article[^>]*class="event"[^>]*data-id="([^"]+)"[^>]*>(.*?)</article>', re.DOTALL | re.IGNORECASE)
    for event_id, body in article_pattern.findall(html):
        title_match = re.search(r"<h3>(.*?)</h3>", body, re.DOTALL | re.IGNORECASE)
        date_iso_match = re.search(r"<time[^>]*datetime=\"([^\"]+)\"[^>]*>(.*?)</time>", body, re.DOTALL | re.IGNORECASE)
        location_match = re.search(r"<span[^>]*class=\"location\"[^>]*>(.*?)</span>", body, re.DOTALL | re.IGNORECASE)
        price_match = re.search(r"<span[^>]*class=\"price\"[^>]*>(.*?)</span>", body, re.DOTALL | re.IGNORECASE)
        link_match = re.search(r"<a[^>]*class=\"tickets\"[^>]*href=\"([^\"]+)\"", body, re.DOTALL | re.IGNORECASE)
        desc_match = re.search(r"<p[^>]*class=\"desc\"[^>]*>(.*?)</p>", body, re.DOTALL | re.IGNORECASE)

        event = Event(
            event_id=event_id,
            title=_strip_tags(title_match.group(1)) if title_match else "",
            date_iso=date_iso_match.group(1) if date_iso_match else "",
            date_text=_strip_tags(date_iso_match.group(2)) if date_iso_match else "",
            location=_strip_tags(location_match.group(1)) if location_match else "",
            price=_strip_tags(price_match.group(1)) if price_match else "",
            details_url=link_match.group(1) if link_match else "",
            description=_strip_tags(desc_match.group(1)) if desc_match else "",
        )

        events.append(event)

    return events


def parse_events_from_html(html: str) -> List[Event]:
    if _HAVE_BS4 and BeautifulSoup is not None:
        return _parse_with_bs4(html)
    return _parse_with_regex(html)


def main() -> None:
    events = parse_events_from_html(HTML_CONTENT)
    print(json.dumps([asdict(e) for e in events], indent=2))


if __name__ == "__main__":
    main()

