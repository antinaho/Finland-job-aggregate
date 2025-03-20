from dataclasses import dataclass
from datetime import datetime

@dataclass
class Job:
    source: str
    post_date: datetime.date
    post_url: str

    title: str
    company: str
    location: str
    description: str
    apply_url: str

@dataclass
class Listing:
    date: datetime.date
    url: str