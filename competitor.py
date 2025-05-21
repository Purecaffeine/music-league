"""
competitor.py

This module defines the Competitor class and the CompetitorsManager class.
The Competitor class represents a competitor with an ID and name.
The CompetitorsManager class manages a list of competitors, allowing for addition,
removal, and retrieval.
"""

import csv
from typing import List, Optional


class Competitor:
    """
    Represents a competitor with an ID and name.
    """

    def __init__(self, competitor_id: str, name: str) -> None:
        self.id = competitor_id
        self.name = name

    def __repr__(self) -> str:
        return f"Competitor(id='{self.id}', name='{self.name}')"


class CompetitorsManager:
    """
    Manages a list of competitors, allowing for addition, removal, and retrieval.
    """
    ############################################################################
    # Special Methods
    ############################################################################

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.competitors = []
        self._load_competitors()

    ############################################################################
    # Public Methods
    ############################################################################
    def get_by_id(self, competitor_id: str) -> Optional[Competitor]:
        """
        Returns the first Competitor with the given ID, or None if not found.
        """
        for competitor in self.competitors:
            if competitor.id == competitor_id:
                return competitor
        return None

    def get_by_name(self, name: str) -> Optional[Competitor]:
        """
        Returns the first Competitor with the given name, or None if not found.
        """
        for competitor in self.competitors:
            if competitor.name == name:
                return competitor
        return None

    def get_all(self) -> List[Competitor]:
        """
        Returns a list of all competitors
        """
        return self.competitors

    def add_competitor(self, competitor_id: str, name: str) -> Optional[Competitor]:
        """
        Adds a new competitor with the given ID and name.
        """
        if self.get_by_id(competitor_id) is None:
            competitor = Competitor(competitor_id, name)
            self.competitors.append(competitor)
            self._save_competitors()
            return competitor
        return None

    def remove_competitor(self, competitor_id: str) -> bool:
        """
        Removes the competitor with the given ID.
        Returns True if removed, False if not found.
        """
        competitor = self.get_by_id(competitor_id)
        if competitor:
            self.competitors.remove(competitor)
            self._save_competitors()
            return True
        return False

    ############################################################################
    # Private Methods
    ############################################################################
    def _save_competitors(self) -> None:
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Name'])
            for competitor in self.competitors:
                writer.writerow([competitor.id, competitor.name])

    def _load_competitors(self) -> None:
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                competitor = Competitor(row['ID'], row['Name'])
                self.competitors.append(competitor)


# Example usage
if __name__ == "__main__":
    manager = CompetitorsManager('data/competitors.csv')
    print("All competitors:", manager.get_all())
    new_competitor = manager.add_competitor('C004', 'New Competitor')
    if new_competitor:
        print("Added competitor:", new_competitor)
    else:
        print("Competitor already exists.")

    print("All competitors after addition:")
    for competitor in manager.get_all():
        print(competitor)

    # Remove the added competitor
    manager.remove_competitor('C004')
    print("All competitors after removal:")
    for competitor in manager.get_all():
        print(competitor)
