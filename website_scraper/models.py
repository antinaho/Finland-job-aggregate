from dataclasses import dataclass
from datetime import date

@dataclass
class Job:
    source: str
    post_date: date

    title: str
    company: str
    location: str
    description: str
    apply_url: str