from dataclasses import dataclass
from datetime import datetime

@dataclass
class Job:
    source: str
    post_date: datetime.date

    title: str
    company: str
    location: str
    description: str
    apply_url: str