"""
round.py

This module defines the Submission class and the SubmissionManager class.
The Submission class represents a submission with all relevant fields from the CSV.
The CompetitorsManager class manages a list of submissions, allowing for addition, removal, and retrieval.
"""

import csv
from typing import List, Optional


class Submission:
    """
    Represents a submission with all relevant fields from the CSV.
    """

    def __init__(
        self,
        spotify_uri: str,
        title: str,
        album: str,
        artists: str,
        submitter_id: str,
        created: str,
        comment: str,
        round_id: str,
        visible_to_voters: str
    ) -> None:
        self.spotify_uri = spotify_uri
        self.title = title
        self.album = album
        self.artists = artists
        self.submitter_id = submitter_id
        self.created = created
        self.comment = comment
        self.round_id = round_id
        self.visible_to_voters = visible_to_voters

    def __repr__(self) -> str:
        return (
            f"Submission(spotify_uri='{self.spotify_uri}', title='{self.title}', album='{self.album}', "
            f"artists='{self.artists}', submitter_id='{self.submitter_id}', created='{self.created}', "
            f"comment='{self.comment}', round_id='{self.round_id}', visible_to_voters='{self.visible_to_voters}')"
        )


class SubmissionsManager:
    """
    Manages a list of submissions, allowing for addition, removal, and retrieval.
    """
    ############################################################################
    # Special Methods
    ############################################################################

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.submissions: List[Submission] = []
        self._load_submissions()

    ############################################################################
    # Public Methods
    ############################################################################
    def get_by_spotify_uri(self, spotify_uri: str) -> Optional[Submission]:
        """
        Returns the first Submission with the given Spotify URI, or None if not found.
        """
        for submission in self.submissions:
            if submission.spotify_uri == spotify_uri:
                return submission
        return None

    def get_by_submitter_id(self, submitter_id: str) -> List[Submission]:
        """
        Returns all Submissions by the given submitter ID.
        """
        return [s for s in self.submissions if s.submitter_id == submitter_id]

    def get_by_round_id(self, round_id: str) -> List[Submission]:
        """
        Returns all Submissions for the given round ID.
        """
        return [s for s in self.submissions if s.round_id == round_id]

    def get_all(self) -> List[Submission]:
        """
        Returns a list of all submissions.
        """
        return self.submissions

    def add_submission(
        self,
        spotify_uri: str,
        title: str,
        album: str,
        artists: str,
        submitter_id: str,
        created: str,
        comment: str,
        round_id: str,
        visible_to_voters: str
    ) -> Optional[Submission]:
        """
        Adds a new submission with the given details.
        """
        if self.get_by_spotify_uri(spotify_uri) is None:
            submission = Submission(
                spotify_uri, title, album, artists, submitter_id, created, comment, round_id, visible_to_voters
            )
            self.submissions.append(submission)
            self._save_submissions()
            return submission
        return None

    def remove_submission(self, spotify_uri: str) -> bool:
        """
        Removes the submission with the given Spotify URI.
        Returns True if removed, False if not found.
        """
        submission = self.get_by_spotify_uri(spotify_uri)
        if submission:
            self.submissions.remove(submission)
            self._save_submissions()
            return True
        return False

    ############################################################################
    # Private Methods
    ############################################################################
    def _save_submissions(self) -> None:
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Spotify URI', 'Title', 'Album', 'Artist(s)', 'Submitter ID',
                'Created', 'Comment', 'Round ID', 'Visible To Voters'
            ])
            for s in self.submissions:
                writer.writerow([
                    s.spotify_uri, s.title, s.album, s.artists, s.submitter_id,
                    s.created, s.comment, s.round_id, s.visible_to_voters
                ])

    def _load_submissions(self) -> None:
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                submission = Submission(
                    row['Spotify URI'],
                    row['Title'],
                    row['Album'],
                    row['Artist(s)'],
                    row['Submitter ID'],
                    row['Created'],
                    row['Comment'],
                    row['Round ID'],
                    row['Visible To Voters']
                )
                self.submissions.append(submission)


# Example usage
if __name__ == "__main__":
    manager = SubmissionsManager('data/submissions.csv')
    print("All submissions:", manager.get_all())
    new_submission = manager.add_submission(
        'spotify:track:EXAMPLE', 'Example Title', 'Example Album', 'Example Artist',
        'submitter_id', '2025-01-01T00:00:00Z', 'Example comment', 'round_id', 'Yes'
    )
    if new_submission:
        print("Added submission:", new_submission)
    else:
        print("Submission already exists.")
    print("All submissions after addition:", manager.get_all())

    # Remove the added submission
    manager.remove_submission('spotify:track:EXAMPLE')
    print("All submissions after removal:", manager.get_all())
