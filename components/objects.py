import logging
import uuid
from typing import Optional

from pydantic import BaseModel, Field


def _build_uuid_string() -> str:
    return uuid.uuid4().hex


_LOGGER = logging.getLogger(__name__)


class PollOption(BaseModel):
    uid: str = Field(..., default_factory=_build_uuid_string)
    text: str
    votes: int = 0


class PollVote(BaseModel):
    poll_uid: str
    option_uid: str
    previous_option_uid: Optional[str] = None


class Poll(BaseModel):
    uid: str = Field(..., default_factory=_build_uuid_string)
    question: str
    option_one: PollOption
    option_two: PollOption
    active: bool = False

    def add_vote(self, poll_vote: PollVote) -> None:
        if poll_vote.option_uid == poll_vote.previous_option_uid:
            _LOGGER.debug(
                "Skipping vote for %s, already voted for that option", poll_vote.option_uid
            )
            return

        for option in (self.option_one, self.option_two):
            if option.uid == poll_vote.option_uid:
                option.votes += 1
            if option.uid == poll_vote.previous_option_uid:
                option.votes -= 1


class PollCookie(BaseModel):
    poll_votes: dict[str, PollVote] = {}
