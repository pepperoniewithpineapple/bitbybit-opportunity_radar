from dataclasses import dataclass
from typing import Literal, Optional

from utils import ACADEMIC_LEVELS


AcademicLevel = Literal[*ACADEMIC_LEVELS]


@dataclass
class Opportunity:
    id: str
    title: str
    type: str
    interests: list[str]
    eligible_levels: list[AcademicLevel]
    beginner_friendly: bool
    deadline: str
    url: str
    organiser: str
    personalisation_score: Optional[float] = 1.0

    def __str__(self) -> str:
        return f"{self.title} {self.type} {' '.join(self.interests)} {self.organiser} " + ("beginner_friendly" if self.beginner_friendly else "not_beginner_friendly")

    def to_dict(self) -> dict: #  For storage
        selfdict = self.__dict__
        if "personalisation_score" in selfdict:
            del selfdict["personalisation_score"]
        return selfdict


type OpportunityID = str
@dataclass
class Student:
    name: str
    level: AcademicLevel
    interests: list[str]
    career_goals: list[str]
    personalisation_profile: str = ""


@dataclass
class AppliedOpportunity(Opportunity):
    status: Literal["pending", "approved", "rejected", "ongoing", "completed"] = "pending"
    notes: str = ""


@dataclass
class PortfolioItem:
    title: str
    organiser: str
    role: str
    dates: str
    hours: Optional[float] = None
    awards: Optional[list[str]] = None
