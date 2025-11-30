from django.test import TestCase
from datetime import date, timedelta

from . import scoring


class ScoringTests(TestCase):
    def test_high_impact_prefers_higher_importance(self):
        """High Impact strategy should rank higher-importance task first."""
        today = date.today()
        tasks = [
            {
                "id": "low",
                "title": "Low importance task",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 2,
                "importance": 3,
                "dependencies": [],
            },
            {
                "id": "high",
                "title": "High importance task",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 2,
                "importance": 9,
                "dependencies": [],
            },
        ]

        result = scoring.analyze_tasks(tasks, strategy="high_impact")
        top_task = result[0]
        self.assertEqual(top_task["id"], "high")

    def test_deadline_driven_prefers_earlier_due_date(self):
        """Deadline Driven strategy should rank nearer deadline first when importance is similar."""
        today = date.today()
        tasks = [
            {
                "id": "later",
                "title": "Later deadline",
                "due_date": today + timedelta(days=10),
                "estimated_hours": 2,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "sooner",
                "title": "Sooner deadline",
                "due_date": today + timedelta(days=1),
                "estimated_hours": 2,
                "importance": 7,
                "dependencies": [],
            },
        ]

        result = scoring.analyze_tasks(tasks, strategy="deadline_driven")
        top_task = result[0]
        self.assertEqual(top_task["id"], "sooner")

    def test_fastest_wins_prefers_lower_effort(self):
        """Fastest Wins strategy should rank lower-effort task higher."""
        today = date.today()
        tasks = [
            {
                "id": "slow",
                "title": "Slow task",
                "due_date": today + timedelta(days=3),
                "estimated_hours": 8,
                "importance": 8,
                "dependencies": [],
            },
            {
                "id": "fast",
                "title": "Fast task",
                "due_date": today + timedelta(days=3),
                "estimated_hours": 1,
                "importance": 8,
                "dependencies": [],
            },
        ]

        result = scoring.analyze_tasks(tasks, strategy="fastest_wins")
        top_task = result[0]
        self.assertEqual(top_task["id"], "fast")
