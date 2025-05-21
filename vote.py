"""
votes.py

This module defines the Vote class and the VotesManager class.
The Vote class represents a vote with all relevant fields from the CSV.
The VotesManager class manages a list of votes, allowing for addition, removal, and retrieval.
"""

import csv
from typing import List, Optional


class Vote:
    """
    Represents a vote with all relevant fields from the CSV.
    """

    def __init__(
        self,
        spotify_uri: str,
        voter_id: str,
        created: str,
        points_assigned: str,
        comment: str,
        round_id: str
    ) -> None:
        self.spotify_uri = spotify_uri
        self.voter_id = voter_id
        self.created = created
        self.points_assigned = points_assigned
        self.comment = comment
        self.round_id = round_id

    def __repr__(self) -> str:
        return (
            f"Vote(spotify_uri='{self.spotify_uri}', voter_id='{self.voter_id}', created='{self.created}', "
            f"points_assigned='{self.points_assigned}', comment='{self.comment}', round_id='{self.round_id}')"
        )


class VotesManager:
    """
    Manages a list of votes, allowing for addition, removal, and retrieval.
    """
    ############################################################################
    # Special Methods
    ############################################################################

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.votes: List[Vote] = []
        self._load_votes()

    ############################################################################
    # Public Methods
    ############################################################################
    def get_by_spotify_uri(self, spotify_uri: str) -> List[Vote]:
        """
        Returns all votes for the given Spotify URI.
        """
        return [v for v in self.votes if v.spotify_uri == spotify_uri]

    def get_by_voter_id(self, voter_id: str) -> List[Vote]:
        """
        Returns all votes by the given voter ID.
        """
        return [v for v in self.votes if v.voter_id == voter_id]

    def get_by_round_id(self, round_id: str) -> List[Vote]:
        """
        Returns all votes for the given round ID.
        """
        return [v for v in self.votes if v.round_id == round_id]

    def get_all(self) -> List[Vote]:
        """
        Returns a list of all votes.
        """
        return self.votes

    def add_vote(
        self,
        spotify_uri: str,
        voter_id: str,
        created: str,
        points_assigned: str,
        comment: str,
        round_id: str
    ) -> Vote:
        """
        Adds a new vote with the given details.
        """
        vote = Vote(spotify_uri, voter_id, created,
                    points_assigned, comment, round_id)
        self.votes.append(vote)
        self._save_votes()
        return vote

    def remove_vote(self, spotify_uri: str, voter_id: str, round_id: str) -> bool:
        """
        Removes the vote with the given Spotify URI, voter ID, and round ID.
        Returns True if removed, False if not found.
        """
        for vote in self.votes:
            if (
                vote.spotify_uri == spotify_uri and
                vote.voter_id == voter_id and
                vote.round_id == round_id
            ):
                self.votes.remove(vote)
                self._save_votes()
                return True
        return False

    ############################################################################
    # Private Methods
    ############################################################################
    def _save_votes(self) -> None:
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Spotify URI', 'Voter ID', 'Created', 'Points Assigned', 'Comment', 'Round ID'
            ])
            for v in self.votes:
                writer.writerow([
                    v.spotify_uri, v.voter_id, v.created, v.points_assigned, v.comment, v.round_id
                ])

    def _load_votes(self) -> None:
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                vote = Vote(
                    row['Spotify URI'],
                    row['Voter ID'],
                    row['Created'],
                    row['Points Assigned'],
                    row['Comment'],
                    row['Round ID']
                )
                self.votes.append(vote)


# Example usage
if __name__ == "__main__":
    manager = VotesManager('data/votes.csv')
    print("All votes:", manager.get_all())
    new_vote = manager.add_vote(
        'spotify:track:EXAMPLE', 'voter_id', '2025-01-01T00:00:00Z', '3', 'Example comment', 'round_id'
    )
    print("Added vote:", new_vote)
    print("All votes after addition:", manager.get_all())

    # Remove the added vote
    manager.remove_vote('spotify:track:EXAMPLE', 'voter_id', 'round_id')
    print("All votes after removal:", manager.get_all())
