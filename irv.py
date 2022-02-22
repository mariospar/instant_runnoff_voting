from typing import Dict, Text, Tuple, List, Optional
from dataclasses import dataclass, field
from math import ceil

ELIGIBILITY_THRESHOLD = 2 / 3
PARTICIPATION_THRESHOLD = 3 / 4
ELIGIBLE_VOTERS = 10

@dataclass
class Votes(Dict):
    """Dataclass for a Ballot Vote Interface"""

    in_favour: List = field(default=None)
    against: List = field(default=None)


class Ballot:
    
    def __init__(self, proposals: Tuple[Text], votes: Votes) -> None:
        self.proposals, self.votes = proposals, votes

    @property
    def in_favour(self) -> Optional[List[Text]]:
        return self.votes.in_favour or []

    @property
    def against(self) -> Optional[List[Text]]:
        return self.votes.against or []

    @property
    def blanks(self) -> Optional[List[Text]]:
        return (
            sorted(*self.votes.against, *self.votes.in_favour) == sorted(self.proposals)
            if len(self.votes.against) + len(self.votes.in_favour)
            == len(self.proposals)
            else []
        )


class BallotBox:
    
    def __init__(self) -> None:
        self.entries: List[Ballot] = []

    def addBallot(self, ballot: Ballot) -> None:
        if len(self.entries) == 0:
            self.capacity: int = len(ballot.proposals)

        if len(ballot.proposals) != self.capacity:
            exit(f"{ballot.__str__} cannot be added to Ballot Box")

        self.entries.append(ballot)
    
    def validate(self) -> None:
        if self.entries < ceil(ELIGIBLE_VOTERS * PARTICIPATION_THRESHOLD):
            exit("This vote has not enough ballots to be considered valid")


class IRV:

    def __init__(self, ballot_box: BallotBox) -> None:
        self.ballot_box = ballot_box

    def results(self):
        self.ballot_box.validate()
        while True:
            stats = self.round_stats()
            prominent_proposal = max(stats.items(), key=lambda x: x[1])
            if self.passes(prominent_proposal[1]):
                print(f"{prominent_proposal[0]} is accepted")
                break
            min_votes = self.find_min(stats)
            self.discard(min_votes)
            if not sum(i > 0 for i in stats.values()):
                print("No proposal was accepted")
                break

    def passes(self, prominent_vote_count: int) -> bool:
        threshold = ceil(len(self.ballot_box.entries) * ELIGIBILITY_THRESHOLD)
        return prominent_vote_count >= threshold

    def find_min(self, stats: Dict[Text, int]) -> List[Text]:
        removed_zeros = stats
        for k, v in stats.copy().items():
            if v == 0:
                stats.pop(k)

        return [
            k
            for k, v in removed_zeros.items()
            if v == min(removed_zeros.items(), key=lambda x: x[1])[1]
        ]

    def init_counter(self) -> Dict[Text, int]:
        return {proposal: 0 for proposal in self.ballot_box.entries[0].proposals}

    def round_stats(self) -> Dict[Text, int]:
        counter = self.init_counter()

        for ballot in self.ballot_box.entries:
            if len(ballot.in_favour) > 0:
                counter[ballot.in_favour[0]] += 1

        return counter

    def discard(self, least_prominent: List[Text]) -> None:

        for proposal in least_prominent:
            for ballot in self.ballot_box.entries:
                if proposal in ballot.in_favour:
                    ballot.in_favour.remove(proposal)


ballot_box = BallotBox()

proposals = ("p1", "p2", "p3", "p4")

a = Votes(in_favour=["p4", "p1", "p3"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p2", "p1"], against=["p3, p4"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p1", "p4"], against=["p2"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p3", "p4", "p1"], against=["p2"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p4", "p3", "p2"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p2", "p4", "p3"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

a = Votes(in_favour=["p2", "p4"])
b = Ballot(proposals, a)
ballot_box.addBallot(b)

count = IRV(ballot_box)

count.results()
