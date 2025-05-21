from league import League
from typing import Dict, List, Tuple, Optional


class LeagueStats:
    """
    Provides advanced statistics and insights for a League instance.
    """

    def __init__(self, league: League):
        self.league = league

    def most_voted_submission(self) -> Optional[Tuple[str, int]]:
        """
        Returns the Spotify URI and vote count of the submission with the most votes.
        """
        vote_counts: Dict[str, int] = {}
        for vote in self.league.votes.get_all():
            vote_counts[vote.spotify_uri] = vote_counts.get(
                vote.spotify_uri, 0) + 1
        if not vote_counts:
            return None
        most_voted = max(vote_counts.items(), key=lambda x: x[1])
        return most_voted  # (spotify_uri, count)

    def highest_scoring_submission(self) -> Optional[Tuple[str, int]]:
        """
        Returns the Spotify URI and total points of the highest scoring submission.
        """
        score_counts: Dict[str, int] = {}
        for vote in self.league.votes.get_all():
            if str(vote.points_assigned).isdigit():
                score_counts[vote.spotify_uri] = score_counts.get(
                    vote.spotify_uri, 0) + int(vote.points_assigned)
        if not score_counts:
            return None
        highest = max(score_counts.items(), key=lambda x: x[1])
        return highest  # (spotify_uri, total_points)

    def average_points_per_competitor(self) -> Dict[str, float]:
        """
        Returns a dict mapping competitor_id to their average points per submission.
        """
        averages: Dict[str, float] = {}
        for competitor in self.league.competitors.get_all():
            subs = self.league.get_submissions_by_competitor(competitor.id)
            if not subs:
                continue
            total_points = sum(
                sum(int(v.points_assigned) for v in self.league.get_votes_for_submission(
                    sub.spotify_uri) if str(v.points_assigned).isdigit())
                for sub in subs
            )
            averages[competitor.id] = total_points / len(subs)
        return averages

    def most_generous_voter(self) -> Optional[Tuple[str, int]]:
        """
        Returns the voter_id who has given out the most total points.
        """
        voter_points: Dict[str, int] = {}
        for vote in self.league.votes.get_all():
            if str(vote.points_assigned).isdigit():
                voter_points[vote.voter_id] = voter_points.get(
                    vote.voter_id, 0) + int(vote.points_assigned)
        if not voter_points:
            return None
        return max(voter_points.items(), key=lambda x: x[1])

    def most_critical_voter(self) -> Optional[Tuple[str, int]]:
        """
        Returns the voter_id who has given out the fewest total points (but has voted).
        """
        voter_points: Dict[str, int] = {}
        for vote in self.league.votes.get_all():
            if str(vote.points_assigned).isdigit():
                voter_points[vote.voter_id] = voter_points.get(
                    vote.voter_id, 0) + int(vote.points_assigned)
        if not voter_points:
            return None
        return min(voter_points.items(), key=lambda x: x[1])

    def competitor_stats(self, competitor_id: str) -> Dict:
        """
        Returns a dictionary of interesting stats for a specific competitor.
        """
        stats = {}
        # Total number of votes received (all submissions)
        votes_received = self.league.get_votes_by_competitor(competitor_id)
        stats['total_votes_received'] = self.league.tally_competitor_score(
            competitor_id)

        # Total number of rounds participated in
        rounds = self.league.get_rounds_for_competitor(competitor_id)
        stats['rounds_participated'] = len(rounds)

        # All submissions by this competitor
        submissions = self.league.get_submissions_by_competitor(competitor_id)

        # Best submission (by total points)
        best_submission = None
        best_points = -1
        for sub in submissions:
            votes = self.league.get_votes_for_submission(sub.spotify_uri)
            points = sum(int(v.points_assigned)
                         for v in votes if str(v.points_assigned).isdigit())
            if points > best_points:
                best_points = points
                best_submission = sub
        stats['best_submission'] = (
            best_submission, best_points) if best_submission else None

        # The person they voted for the most (by count)
        votes_cast = []
        points_given = {}
        for vote in self.league.votes.get_by_voter_id(competitor_id):
            sub = self.league.get_submission_by_uri(vote.spotify_uri)
            if sub:
                votes_cast.append(sub.submitter_id)
                # Track points given to each submitter
                if str(vote.points_assigned).isdigit():
                    points_given[sub.submitter_id] = points_given.get(
                        sub.submitter_id, 0) + int(vote.points_assigned)
        if votes_cast:
            from collections import Counter
            most_often_voted_for_id, count = Counter(
                votes_cast).most_common(1)[0]
            most_often_voted_for = self.league.competitors.get_by_id(
                most_often_voted_for_id)
            stats['most_often_voted_for'] = (most_often_voted_for, count)
        else:
            stats['most_often_voted_for'] = None

        # The person they gave the most points to (by sum of points)
        if points_given:
            most_points_given_id = max(points_given, key=points_given.get)
            most_points_given_to = self.league.competitors.get_by_id(
                most_points_given_id)
            stats['most_points_given_to'] = (
                most_points_given_to, points_given[most_points_given_id])
        else:
            stats['most_points_given_to'] = None

        # The person who voted for them the most (by count)
        received_from = []
        points_received_from = {}
        for vote in votes_received:
            received_from.append(vote.voter_id)
            # Track points received from each voter
            if str(vote.points_assigned).isdigit():
                points_received_from[vote.voter_id] = points_received_from.get(
                    vote.voter_id, 0) + int(vote.points_assigned)
        if received_from:
            from collections import Counter
            most_often_votes_from_id, count = Counter(
                received_from).most_common(1)[0]
            most_often_votes_from = self.league.competitors.get_by_id(
                most_often_votes_from_id)
            stats['most_often_votes_from'] = (most_often_votes_from, count)
        else:
            stats['most_often_votes_from'] = None

        # The person who gave them the most points (by sum of points)
        if points_received_from:
            most_points_from_id = max(
                points_received_from, key=points_received_from.get)
            most_points_from = self.league.competitors.get_by_id(
                most_points_from_id)
            stats['most_points_from'] = (
                most_points_from, points_received_from[most_points_from_id])
        else:
            stats['most_points_from'] = None

        return stats


if __name__ == "__main__":
    # Example usage
    league = League(
        'data/competitors.csv',
        'data/rounds.csv',
        'data/submissions.csv',
        'data/votes.csv'
    )
    league_stats = LeagueStats(league)
    print(league_stats.most_voted_submission())
    print(league_stats.highest_scoring_submission())
    print(league_stats.average_points_per_competitor())
    print(league_stats.most_generous_voter())
    print(league_stats.most_critical_voter())

    for competitor in league.competitors.get_all():
        print(f"Stats for {competitor.name}:")
        stats = league_stats.competitor_stats(competitor.id)
        print(stats)
