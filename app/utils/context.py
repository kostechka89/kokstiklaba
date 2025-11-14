from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CurrentUser:
    id: UUID
    name: str
    email: str
    avatar_url: Optional[str]
    is_author: bool
    is_admin: bool
    registered_at: datetime

