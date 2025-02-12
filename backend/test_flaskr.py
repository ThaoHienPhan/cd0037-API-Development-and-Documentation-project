import os
import unittest

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "admin"
        self.database_password = ""
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_success(self):
        # Add mock data to the database
        with self.app.app_context():
            category = Category(type="Science")
            db.session.add(category)
            db.session.commit()

        # Send a GET request to the /categories endpoint
        response = self.client.get('/categories')
        data = response.get_json()

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('categories', data)
        self.assertEqual(len(data['categories']), 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
