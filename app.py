from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container
from textual.reactive import reactive
from textual.coordinate import Coordinate
from textual import events
from textual.widgets import ListView, ListItem

from league import League
from league_stats import LeagueStats


class LeaderboardTable(DataTable):
    def update_leaderboard(self, league: League):
        self.clear(True)
        self.add_columns("Rank", "Competitor", "Score",
                         "# Rounds", "Avg Score")
        leaderboard = league.get_leaderboard()
        for rank, entry, in enumerate(leaderboard, 1):
            self.add_row(
                str(rank),
                entry['name'],
                str(entry['score']),
                str(entry['rounds']),
                str(f"{entry['avg_score']:.1f}"),
            )


class RoundsTable(DataTable):
    def update_rounds(self, league: League):
        self.clear(True)
        self.add_columns("Name", "Description")
        for r in league.rounds.get_all():
            self.add_row(r.name, r.description)


class CompetitorStats(ListView):
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

        points_received_by_player = stats.get('points_received_by_player', {})
        points_given_to_player = stats.get('points_given_to_player', {})

        received_lines = []
        given_lines = []

        if points_received_by_player:
            received_lines.append("Points received from each player:")
            for voter_id, points in points_received_by_player.items():
                voter = league.competitors.get_by_id(voter_id)
                voter_name = voter.name if voter else voter_id
                received_lines.append(f"{voter_name}: {points}")
        else:
            received_lines.append("Points received from each player: None")

        if points_given_to_player:
            given_lines.append("Points given to each player:")
            for submitter_id, points in points_given_to_player.items():
                submitter = league.competitors.get_by_id(submitter_id)
                submitter_name = submitter.name if submitter else submitter_id
                given_lines.append(f"{submitter_name}: {points}")
        else:
            given_lines.append("Points given to each player: None")

        max_len = max(len(received_lines), len(given_lines))
        received_lines += [""] * (max_len - len(received_lines))
        given_lines += [""] * (max_len - len(given_lines))

        side_by_side = [
            f"{left:<35}   {right}"
            for left, right in zip(received_lines, given_lines)
        ]

        # Clear and repopulate the ListView
        self.clear()
        self.append(ListItem(Static(f"[b]{competitor.name}[/b]")))
        self.append(
            ListItem(Static(f"Total Votes Received: {stats['total_votes_received']}")))
        self.append(
            ListItem(Static(f"Rounds Participated: {stats['rounds_participated']}")))
        self.append(ListItem(Static("")))
        self.append(ListItem(Static(
            f"Best Submission: {getattr(best_submission, 'title', 'N/A')} ({best_points} pts)")))
        self.append(ListItem(
            Static(f"Average Score Per Round: {stats['avg_score_per_round']:.2f}")))
        self.append(ListItem(Static("")))
        self.append(ListItem(Static(
            f"Voted Most Often For: {most_often_voted_for} ({most_often_voted_for_count} times)")))
        self.append(ListItem(Static(
            f"Voted Most Often From: {most_often_votes_from} ({most_often_votes_from_count} times)")))
        self.append(ListItem(Static("")))
        self.append(ListItem(Static(
            f"Awarded the Most Points To: {most_points_given_to} ({most_points_given_to_count} pts)")))
        self.append(ListItem(Static(
            f"Received the Most Points From: {most_points_from} ({most_points_from_count} pts)")))
        self.append(ListItem(Static("")))
        for line in side_by_side:
            self.append(ListItem(Static(line)))


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
        self.stats_panel = CompetitorStats()

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
            "Leaderboard view. Use arrows, Enter or click for stats, 'r' for rounds.")
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
            self.status.update(
                f"Stats for {competitor.name}. Press Esc to return.")
            await self.main_container.remove_children()
            await self.main_container.mount(self.stats_panel)
            self.stats_panel.update_stats(
                self.league, self.league_stats, competitor)
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
