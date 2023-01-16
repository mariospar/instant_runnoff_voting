#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Requirements:
    None

Usage:
    add the votes in the get_votes function and run the script

Description:
    The IRV algorithm uses the instant runoff voting algorithm and elects a single winning proposal
    out of a ranked list.
"""

# Futures
from __future__ import annotations

# Built-in/Generic Imports
from typing import Dict, Text, Tuple, List, Optional
from dataclasses import dataclass, field
from math import ceil

__author__ = "Marios Paraskevas"
__date__ = "23/02/2022"
__version__ = "1.0"
__license__ = "MIT"
__status__ = "production"

# Global Constants
ELIGIBILITY_THRESHOLD = 1 / 3
PARTICIPATION_THRESHOLD = 3 / 4
ELIGIBLE_VOTERS = 5
proposals = ("p1", "p2", "p3")


@dataclass
class Votes(Dict):
    """Dataclass for a Ballot Vote Interface"""

    in_favour: List = field(default=None)
    against: List = field(default=None)


# A ballot is a collection of proposals
class Ballot:
    """The Ballot incorporates is a template for differentiates between the types of votes
    and validates the vote's business logic"""

    def __init__(self, proposals: Tuple[Text], votes: Votes) -> None:
        self.proposals, self.votes = proposals, votes
        self.all_votes = [*self.against, *self.in_favour]
        self.validate()

    @property
    def in_favour(self) -> Optional[List[Text]]:
        """Gets the proposals that the user is in favour of

        Returns:
            Optional[List[Text]]: proposals
        """

        return self.votes.in_favour or []

    @property
    def against(self) -> Optional[List[Text]]:
        """Gets the proposals that the user is against of

        Returns:
            Optional[List[Text]]: proposals
        """

        return self.votes.against or []

    def validate(self) -> None:
        """The business logic of a ballot"""

        # This is a check to see if the user has voted the same proposal twice.
        if sorted(self.all_votes) != sorted(set(self.all_votes)):
            exit("You cannot vote the same proposal twice")

        # This is a check to see if the user has voted a proposal that shouldn't be voted.
        for voted_proposal in self.all_votes:
            if voted_proposal not in self.proposals:
                exit(f"{voted_proposal} doesn't exist as a choice")


# `BallotBox` is a class that represents a ballot box. It has a list of ballots and a size.
class BallotBox:
    """The ballot box encapsulates all ballots and validates the inputs. It also whether there
    enough votes in the box in order to have a valid election"""

    def __init__(self) -> None:
        self.entries: List[Ballot] = []

    def addBallot(self, ballot: Ballot) -> None:
        """Adds the ballot to the box and validates it

        Args:
            ballot (Ballot):the ballot to be added in the box
        """
        if len(self.entries) == 0:
            self.size: int = len(ballot.proposals)

        if (
            len(ballot.proposals) != self.size
        ):  # Checks if all the ballots are of the same proposals
            exit(f"{ballot.__str__} cannot be added to Ballot Box")

        self.entries.append(ballot)

    def validate_participation(self) -> None:
        """Validates the participation threshold"""

        if len(self.entries) < ceil(ELIGIBLE_VOTERS * PARTICIPATION_THRESHOLD):
            exit("This vote has not enough ballots to be considered valid")


# IRV is a voting system that uses ranked ballots to elect a single winner
class IRV:
    """It takes a ballot box and then runs the IRV algorithm on it"""

    def __init__(self, ballot_box: BallotBox) -> None:
        self.ballot_box = ballot_box
        self.results()

    def results(self):
        """
        If the most prominent proposal is accepted, then break out of the loop. Otherwise, discard the
        least prominent proposal and continue
        """

        self.ballot_box.validate_participation()

        while True:

            stats = (
                self.round_stats()
            )  # Dictionary with the number of votes for each proposal.
            prominent_proposal = self.find_most_prominent(stats)

            # This is a check to see if the prominent proposal has enough votes to be accepted.
            if self.passes(prominent_proposal[1]):
                print(f"{prominent_proposal[0]} is accepted")
                break

            min_votes = self.find_least_prominent(stats)
            self.discard(min_votes)

            # This is a check to see if there are any votes left in the ballot box. If there are no
            # votes left, then there is no need to continue with the election.
            if not sum(i > 0 for i in stats.values()):
                print("No proposal was accepted")
                break

    def passes(self, prominent_vote_count: int) -> bool:
        """
        If the number of prominent votes is greater than or equal to the number of entries in the ballot
        box multiplied by the eligibility threshold, then the candidate passes

        :param prominent_vote_count: The number of votes that the candidate has received
        :type prominent_vote_count: int
        :return: A boolean value.
        """

        return prominent_vote_count >= ceil(
            len(self.ballot_box.entries) * ELIGIBILITY_THRESHOLD
        )

    def find_most_prominent(self, stats: Dict[Text, int]) -> List[Text]:
        """
        Find the most prominent words in a dictionary of word counts

        :param stats: A dictionary of the stats for each word
        :type stats: Dict[Text, int]
        :return: The most prominent words in the text.
        """

        return max(stats.items(), key=lambda x: x[1])

    def find_least_prominent(self, stats: Dict[Text, int]) -> List[Text]:
        """
        Find the least prominent feature in the dataset

        :param stats: A dictionary of the form {word: frequency}
        :type stats: Dict[Text, int]
        :return: The least prominent words in the text.
        """

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
        """
        Initialize a dictionary with the number of votes for each proposal
        :return: The `init_counter` method returns a dictionary with the keys being the proposals and
        the values being the number of votes for each proposal.
        """

        return {proposal: 0 for proposal in self.ballot_box.entries[0].proposals}

    def round_stats(self) -> Dict[Text, int]:
        """
        * For each ballot in the ballot box, add one to the counter for the candidate that was voted for

        :return: A dictionary with the candidate names as keys and the number of votes as values.
        """

        counter = self.init_counter()

        for ballot in self.ballot_box.entries:
            if len(ballot.in_favour) > 0:
                counter[ballot.in_favour[0]] += 1

        return counter

    def discard(self, least_prominent: List[Text]) -> None:
        """
        Remove the least prominent proposals from the ballot box

        :param least_prominent: A list of proposals that are to be discarded
        :type least_prominent: List[Text]
        """

        for proposal in least_prominent:
            for ballot in self.ballot_box.entries:
                if proposal in ballot.in_favour:
                    ballot.in_favour.remove(proposal)


def get_votes() -> List[Votes]:
    """Returns a list of Votes objects"""

    return [
        Votes(in_favour=["p1", "p3", "p2"]),
        Votes(in_favour=["p1", "p2"], against=["p3"]),
        Votes(in_favour=["p2"], against=["p1", "p3"]),
        Votes(in_favour=["p2"], against=["p3"]),
        Votes(in_favour=["p3", "p2", "p1"]),
        Votes(in_favour=["p1"], against=["p2"])
    ]


if __name__ == "__main__":
    ballot_box = BallotBox()
    votes = get_votes()
    for vote in votes:
        ballot_box.addBallot(Ballot(proposals, vote))

    IRV(ballot_box)
