from dataclasses import dataclass
from typing import Literal

from utils import ACADEMIC_LEVELS


AcademicLevel = Literal[*ACADEMIC_LEVELS]


@dataclass
class Opportunity:
    id: str
    title: str
    type: str
    interests: list[str]
    eligible_levels: list[AcademicLevel]
    cost: str
    beginner_friendly: bool
    deadline: str
    url: str
    organizer: str

    def __str__(self) -> str:
        return f"{self.title} {self.type} {' '.join(self.interests)} {self.organizer}"


@dataclass
class Student:
    name: str
    level: AcademicLevel
    interests: list[str]


@dataclass
class Application:
    opp_id: str
    status: Literal["pending", "approved", "rejected"]
    notes: str = ""