"""
league.py

This module defines the LeagueManager class, which manages all core data managers:
CompetitorsManager, RoundsManager, SubmissionsManager, and VotesManager.
It provides methods to filter and aggregate data across the entire league.
"""

from competitor import CompetitorsManager, Competitor
from round import RoundsManager, Round
from submission import SubmissionsManager, Submission
from vote import VotesManager, Vote
from typing import List, Optional, Dict


class League:

    ############################################################################
    # Special Methods
    ############################################################################

    def __init__(
        self,
        competitors_csv: str,
        rounds_csv: str,
        submissions_csv: str,
        votes_csv: str
    ) -> None:
        self.competitors = CompetitorsManager(competitors_csv)
        self.rounds = RoundsManager(rounds_csv)
        self.submissions = SubmissionsManager(submissions_csv)
        self.votes = VotesManager(votes_csv)

    ############################################################################
    # Public Methods
    ############################################################################

    def get_submissions_by_competitor(self, competitor_id: str) -> List[Submission]:
        return self.submissions.get_by_submitter_id(competitor_id)

    def get_submissions_by_round(self, round_id: str) -> List[Submission]:
        return self.submissions.get_by_round_id(round_id)

    def get_votes_by_round(self, round_id: str) -> List[Vote]:
        return self.votes.get_by_round_id(round_id)

    def get_votes_by_competitor(self, competitor_id: str) -> List[Vote]:
        """
        Get all votes for all submissions by a competitor.
        """
        competitor_subs = self.get_submissions_by_competitor(competitor_id)
        uris = {s.spotify_uri for s in competitor_subs}
        return [v for v in self.votes.get_all() if v.spotify_uri in uris]

    def get_votes_for_submission(self, spotify_uri: str) -> List[Vote]:
        return self.votes.get_by_spotify_uri(spotify_uri)

    def get_rounds_for_competitor(self, competitor_id: str) -> List[Round]:
        """
        Get all rounds in which a competitor has submitted.
        """
        round_ids = {
            s.round_id for s in self.get_submissions_by_competitor(competitor_id)}
        return [r for r in self.rounds.get_all() if r.id in round_ids]

    def get_comments_for_submission(self, spotify_uri: str) -> List[str]:
        """
        Get all comments for a given submission.
        """
        return [v.comment for v in self.get_votes_for_submission(spotify_uri) if v.comment]

    def get_comments_for_competitor(self, competitor_id: str) -> List[str]:
        """
        Get all comments for all submissions by a competitor.
        """
        comments = []
        for sub in self.get_submissions_by_competitor(competitor_id):
            comments.extend(self.get_comments_for_submission(sub.spotify_uri))
        return comments

    def tally_competitor_score(self, competitor_id: str) -> int:
        """
        Sum all points assigned to all submissions by this competitor.
        """
        votes = self.get_votes_by_competitor(competitor_id)
        return sum(int(v.points_assigned) for v in votes if str(v.points_assigned).isdigit())

    def tally_scores_by_round(self, round_id: str) -> Dict[str, int]:
        """
        Returns a dict mapping competitor_id to their total score in a round.
        """
        subs = self.get_submissions_by_round(round_id)
        scores: Dict[str, int] = {}
        for sub in subs:
            votes = self.get_votes_for_submission(sub.spotify_uri)
            total = sum(int(v.points_assigned)
                        for v in votes if str(v.points_assigned).isdigit())
            scores[sub.submitter_id] = scores.get(sub.submitter_id, 0) + total
        return scores

    def get_leaderboard(self) -> List[Dict]:
        """
        Returns a sorted list of competitors and their total scores, descending.
        """
        leaderboard = []
        for competitor in self.competitors.get_all():
            score = self.tally_competitor_score(competitor.id)
            rounds = len(self.get_rounds_for_competitor(competitor.id))
            avg_score_per_round = score / rounds if rounds else 0
            leaderboard.append({
                'competitor': competitor,
                'score': score,
                'rounds': len(self.get_rounds_for_competitor(competitor.id)),
                'avg_score': avg_score_per_round,
                'name': competitor.name
            })
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return leaderboard

    def get_competitor_by_name(self, name: str) -> Optional[Competitor]:
        return self.competitors.get_by_name(name)

    def get_round_by_name(self, name: str) -> Optional[Round]:
        return self.rounds.get_by_name(name)

    def get_submission_by_uri(self, spotify_uri: str) -> Optional[Submission]:
        return self.submissions.get_by_spotify_uri(spotify_uri)

    def get_vote(self, spotify_uri: str, voter_id: str, round_id: str) -> Optional[Vote]:
        votes = self.votes.get_by_spotify_uri(spotify_uri)
        for v in votes:
            if v.voter_id == voter_id and v.round_id == round_id:
                return v
        return None


# Example usage
if __name__ == "__main__":
    league = League(
        'data/competitors.csv',
        'data/rounds.csv',
        'data/submissions.csv',
        'data/votes.csv'
    )

    print("Leaderboard:")
    for entry in league.get_leaderboard():
        print(f"{entry['competitor'].name}: {entry['score']} points")

    print("\nScores by round:")
    for game_round in league.rounds.get_all():
        print(f"Round: {game_round.name}")
        scores = league.tally_scores_by_round(game_round.id)
        for competitor_id, score in scores.items():
            competitor = league.competitors.get_by_id(competitor_id)
            name = competitor.name if competitor else competitor_id
            print(f"  {name}: {score} points")
