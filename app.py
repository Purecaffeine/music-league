from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container
from textual.reactive import reactive
from textual.coordinate import Coordinate
from textual import events

from league import League
from league_stats import LeagueStats


class LeaderboardTable(DataTable):
    def update_leaderboard(self, league: League):
        self.clear(True)
        self.add_columns("Rank", "Competitor", "Score")
        leaderboard = league.get_leaderboard()
        for idx, entry in enumerate(leaderboard, 1):
            self.add_row(
                str(idx), entry['competitor'].name, str(entry['score']))


class RoundsTable(DataTable):
    def update_rounds(self, league: League):
        self.clear(True)
        self.add_columns("Name", "Description")
        for r in league.rounds.get_all():
            self.add_row(r.name, r.description)


class CompetitorStats(Static):
    def update_stats(self, league: League, league_stats: LeagueStats, competitor):
        stats = league_stats.competitor_stats(competitor.id)
        best_submission, best_points = stats['best_submission'] if stats['best_submission'] else (
            None, None)
        most_often_voted_for = stats['most_often_voted_for'][0].name if stats[
            'most_often_voted_for'] and stats['most_often_voted_for'][0] else "N/A"
        most_often_voted_for_count = stats['most_often_voted_for'][1] if stats['most_often_voted_for'] else 0
        most_often_votes_from = stats['most_often_votes_from'][0].name if stats[
            'most_often_votes_from'] and stats['most_often_votes_from'][0] else "N/A"
        most_often_votes_from_count = stats['most_often_votes_from'][1] if stats['most_often_votes_from'] else 0
        most_points_given_to = stats['most_points_given_to'][0].name if stats[
            'most_points_given_to'] and stats['most_points_given_to'][0] else "N/A"
        most_points_given_to_count = stats['most_points_given_to'][1] if stats['most_points_given_to'] else 0
        most_points_from = stats['most_points_from'][0].name if stats[
            'most_points_from'] and stats['most_points_from'][0] else "N/A"
        most_points_from_count = stats['most_points_from'][1] if stats['most_points_from'] else 0

        # Points received by player (sorted dict: voter_id -> points)
        points_received_by_player = stats.get('points_received_by_player', {})
        points_received_lines = []
        if points_received_by_player:
            points_received_lines.append("\nPoints received from each player:")
            for voter_id, points in points_received_by_player.items():
                voter = league.competitors.get_by_id(voter_id)
                voter_name = voter.name if voter else voter_id
                points_received_lines.append(f"  {voter_name}: {points}")
        else:
            points_received_lines.append(
                "\nPoints received from each player: None")

        # Points given to player (sorted dict: submitter_id -> points)
        points_given_to_player = stats.get('points_given_to_player', {})
        points_given_lines = []
        if points_given_to_player:
            points_given_lines.append("\nPoints given to each player:")
            for submitter_id, points in points_given_to_player.items():
                submitter = league.competitors.get_by_id(submitter_id)
                submitter_name = submitter.name if submitter else submitter_id
                points_given_lines.append(f"  {submitter_name}: {points}")
        else:
            points_given_lines.append("\nPoints given to each player: None")

        self.update(
            f"\n[b]{competitor.name}[/b]\n"
            f"Total Votes Received: {stats['total_votes_received']}\n"
            f"Rounds Participated: {stats['rounds_participated']}\n"
            f"\n"
            f"Best Submission: {getattr(best_submission, 'title', 'N/A')} ({best_points} pts)\n"
            f"\n"
            f"Voted Most Often For: {most_often_voted_for} ({most_often_voted_for_count} times)\n"
            f"Voted Most Often From: {most_often_votes_from} ({most_often_votes_from_count} times)\n"
            f"\n"
            f"Awarded the Most Points To: {most_points_given_to} ({most_points_given_to_count} pts)\n"
            f"Received the Most Points From: {most_points_from} ({most_points_from_count} pts)\n"
            + "\n".join(points_received_lines)
            + "\n".join(points_given_lines)
        )


class LeagueApp(App):
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "show_rounds", "Rounds"),
        ("l", "show_leaderboard", "Leaderboard"),
        ("escape", "show_leaderboard", "Back to Leaderboard"),
    ]

    def __init__(self, league: League, **kwargs):
        super().__init__(**kwargs)
        self.league = league
        self.league_stats = LeagueStats(league)
        self.view_mode = reactive("leaderboard")
        self.leaderboard_table = LeaderboardTable()
        self.rounds_table = RoundsTable()
        self.status = Static(
            "Press 'l' for leaderboard, 'r' for rounds, or 'q' to quit.")
        self.main_container = Container()
        self.stats_panel = CompetitorStats(
            "Select a competitor and press Enter or double-click for stats.")

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.status
        yield self.main_container
        yield Footer()

    async def on_mount(self):
        await self.action_show_leaderboard()

    async def action_show_leaderboard(self):
        self.view_mode = "leaderboard"
        self.status.update(
            "Leaderboard view. Use arrows, Enter or double-click for stats, 'r' for rounds.")
        self.leaderboard_table.update_leaderboard(self.league)
        await self.main_container.remove_children()
        await self.main_container.mount(self.leaderboard_table)
        self.leaderboard_table.focus()
        if self.leaderboard_table.row_count > 0:
            self.leaderboard_table.cursor_type = "row"
            self.leaderboard_table.cursor_coordinate = Coordinate(0, 0)

    async def action_show_rounds(self):
        self.view_mode = "rounds"
        self.status.update("Rounds view. Press 'l' for leaderboard.")
        self.rounds_table.update_rounds(self.league)
        await self.main_container.remove_children()
        await self.main_container.mount(self.rounds_table)
        self.rounds_table.focus()
        if self.rounds_table.row_count > 0:
            self.rounds_table.cursor_type = "row"
            self.rounds_table.cursor_coordinate = Coordinate(0, 0)

    async def action_show_stats(self, competitor_idx: int):
        leaderboard = self.league.get_leaderboard()
        if 0 <= competitor_idx < len(leaderboard):
            competitor = leaderboard[competitor_idx]['competitor']
            self.stats_panel.update_stats(
                self.league, self.league_stats, competitor)
            self.status.update(
                f"Stats for {competitor.name}. Press Esc to return.")
            await self.main_container.remove_children()
            await self.main_container.mount(self.stats_panel)
            self.stats_panel.focus()
            self.view_mode = "stats"

    async def on_key(self, event: events.Key):
        if self.view_mode == "leaderboard":
            if event.key == "enter":
                await self.leaderboard_handle_click_or_enter()

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # Preview panel?
        pass

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # This is triggered by clicking on a row
        if self.view_mode == "leaderboard":
            await self.leaderboard_handle_click_or_enter()

    async def leaderboard_handle_click_or_enter(self):
        row = self.leaderboard_table.cursor_row
        await self.action_show_stats(row)


if __name__ == "__main__":
    league = League(
        'data/competitors.csv',
        'data/rounds.csv',
        'data/submissions.csv',
        'data/votes.csv'
    )
    app = LeagueApp(league)
    app.run()
