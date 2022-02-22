from typing import Dict, Text, Tuple, List, Optional
from dataclasses import dataclass, field
from math import ceil

ELIGIBILITY_THRESHOLD = 2 / 3
PARTICIPATION_THRESHOLD = 3 / 4
ELIGIBLE_VOTERS = 5
proposals = ("p1", "p2", "p3")

@dataclass
class Votes(Dict):
    """Dataclass for a Ballot Vote Interface"""

    in_favour: List = field(default=None)
    against: List = field(default=None)


class Ballot:
    
    def __init__(self, proposals: Tuple[Text], votes: Votes) -> None:
        self.proposals, self.votes = proposals, votes
        self.all_votes = [*self.against, *self.in_favour]
        self.validate()

    @property
    def in_favour(self) -> Optional[List[Text]]:
        return self.votes.in_favour or []

    @property
    def against(self) -> Optional[List[Text]]:
        return self.votes.against or []
    
    def validate(self) -> None:
        if sorted(self.all_votes) != sorted(set(self.all_votes)):
            exit("You cannot vote the same proposal twice")
        
        for voted_proposal in self.all_votes:
            if voted_proposal not in self.proposals:
                exit(f"{voted_proposal} doesn't exist as a choice")

class BallotBox:
    
    def __init__(self) -> None:
        self.entries: List[Ballot] = []

    def addBallot(self, ballot: Ballot) -> None:
        if len(self.entries) == 0:
            self.capacity: int = len(ballot.proposals)

        if len(ballot.proposals) != self.capacity:
            exit(f"{ballot.__str__} cannot be added to Ballot Box")

        self.entries.append(ballot)

    def validate_participation(self) -> None:
        if len(self.entries) < ceil(ELIGIBLE_VOTERS * PARTICIPATION_THRESHOLD):
            exit("This vote has not enough ballots to be considered valid")


class IRV:

    def __init__(self, ballot_box: BallotBox) -> None:
        self.ballot_box = ballot_box
        self.results()

    def results(self):
        self.ballot_box.validate_participation()

        while True:
            stats = self.round_stats()
            prominent_proposal = self.find_most_prominent(stats)

            if self.passes(prominent_proposal[1]):
                print(f"{prominent_proposal[0]} is accepted")
                break

            min_votes = self.find_least_prominent(stats)
            self.discard(min_votes)

            if not sum(i > 0 for i in stats.values()):
                print("No proposal was accepted")
                break

    def passes(self, prominent_vote_count: int) -> bool:

        return prominent_vote_count >= ceil(len(self.ballot_box.entries) * ELIGIBILITY_THRESHOLD)


    def find_most_prominent(self, stats: Dict[Text, int]) -> List[Text]:

        return max(stats.items(), key=lambda x: x[1])


    def find_least_prominent(self, stats: Dict[Text, int]) -> List[Text]:

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


def get_votes() -> List[Votes]:
    return [
        Votes(in_favour=["p1", "p3", "p2"]), Votes(in_favour=["p1", "p2"], against=["p3"]),
        Votes(in_favour=["p2"], against=["p1", "p3"]), Votes(in_favour=["p2"], against=["p3"])
    ]

if __name__ == "__main__":
    ballot_box = BallotBox()
    votes = get_votes()
    for vote in votes:
        ballot_box.addBallot(Ballot(proposals, vote))
    
    IRV(ballot_box)
