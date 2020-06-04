from collections import defaultdict
from dataclasses import dataclass, field
from typing import List


@dataclass
class Job:
    id: int
    status: str
    name: str
    allow_failure: bool


@dataclass
class Stage:
    id: int
    jobs: List[Job] = field(default_factory=list)

    @property
    def maxid(self):
        return max(j.id for j in self.jobs)


@dataclass
class Pipeline:
    id: int
    user: str
    status: str
    web_url: str
    stages: List[Job] = field(default_factory=lambda: defaultdict(list))
