"""
round.py

This module defines the Round class and the RoundsManager class.
The Round class represents a round of the game with an ID, time created, name, description, and playlist URL.
The CompetitorsManager class manages a list of competitors, allowing for addition, removal, and retrieval.
"""

import csv
from typing import List, Optional


class Round:
    """
    Represents a game_round with an ID, time_created date, name, description, and playlist URL.
    """

    def __init__(self, round_id: str, time_created: str, name: str, description: str, playlist_url: str) -> None:
        self.id = round_id
        self.time_created = time_created
        self.name = name
        self.description = description
        self.playlist_url = playlist_url

    def __repr__(self) -> str:
        return (f"Round(id='{self.id}', time_created='{self.time_created}', name='{self.name}', "
                f"description='{self.description}', playlist_url='{self.playlist_url}')")


class RoundsManager:
    """
    Manages a list of rounds, allowing for addition, removal, and retrieval.
    """
    ############################################################################
    # Special Methods
    ############################################################################

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.rounds: List[Round] = []
        self._load_rounds()

    ############################################################################
    # Public Methods
    ############################################################################
    def get_by_id(self, round_id: str) -> Optional[Round]:
        """
        Returns the first Round with the given ID, or None if not found.
        """
        for game_round in self.rounds:
            if game_round.id == round_id:
                return game_round
        return None

    def get_by_name(self, name: str) -> Optional[Round]:
        """
        Returns the first Round with the given name, or None if not found.
        """
        for game_round in self.rounds:
            if game_round.name == name:
                return game_round
        return None

    def get_all(self) -> List[Round]:
        """
        Returns a list of all rounds.
        """
        return self.rounds

    def add_round(self, round_id: str, time_created: str, name: str, description: str, playlist_url: str) -> Optional[Round]:
        """
        Adds a new game_round with the given details.
        """
        if self.get_by_id(round_id) is None:
            game_round = Round(round_id, time_created, name,
                               description, playlist_url)
            self.rounds.append(game_round)
            self._save_rounds()
            return game_round
        return None

    def remove_round(self, round_id: str) -> bool:
        """
        Removes the game_round with the given ID.
        Returns True if removed, False if not found.
        """
        game_round = self.get_by_id(round_id)
        if game_round:
            self.rounds.remove(game_round)
            self._save_rounds()
            return True
        return False

    ############################################################################
    # Private Methods
    ############################################################################
    def _save_rounds(self) -> None:
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['ID', 'Created', 'Name', 'Description', 'Playlist URL'])
            for game_round in self.rounds:
                writer.writerow(
                    [game_round.id,
                     game_round.time_created,
                     game_round.name,
                     game_round.description,
                     game_round.playlist_url]
                )

    def _load_rounds(self) -> None:
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                game_round = Round(row['ID'], row['Created'], row['Name'],
                                   row['Description'], row['Playlist URL'])
                self.rounds.append(game_round)


# Example usage
if __name__ == "__main__":
    manager = RoundsManager('data/rounds.csv')
    print("All rounds:", manager.get_all())
    new_round = manager.add_round('R004', '2025-01-01T00:00:00Z', 'New Round',
                                  'A new game_round description', 'https://example.com/playlist')
    if new_round:
        print("Added game_round:", new_round)
    else:
        print("Round already exists.")

    print("All rounds after addition:")
    for game_round in manager.get_all():
        print(game_round)

    # Remove the added game_round
    manager.remove_round('R004')
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    print("All rounds after removal:")
    for game_round in manager.get_all():
        print(game_round)
