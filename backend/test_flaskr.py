import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_USER = os.getenv('DB_USER', 'lethihue')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', "trivia")
DB_PATH = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = DB_PATH
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])
    
    def test_questions_page(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']) <= 10)

    def test_pagination(self):
        res_for_page_1 = self.client().get('/questions')
        data_1 = json.loads(res_for_page_1.data)

        res_for_page_2 = self.client().get('/questions?page=2')
        data_2 = json.loads(res_for_page_2.data)

        self.assertNotEqual(data_1, data_2)

    def test_delete_question(self):
        #prepare 
        question_for_delete = Question("How do you want to create?", "ok", 2, 1)
        self.db.session.add(question_for_delete)
        self.db.session.commit()

        #test delete function
        res = self.client().delete('/questions/' + question_for_delete.id)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_delete_question_not_exist(self):
        res = self.client().delete('/questions/10000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
    

    def test_create_question(self):
        new_question = {
            'question': "How do you want to create?",
            "answer": "ok",
            "category": 2,
            "difficulty": 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_question(self):
        search_query = {
            "searchTerm": "what",
        }
        res = self.client().post('/questions/search', json=search_query)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    

    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_question_to_play(self):
        previous_questions = [1]
        current_info = {
            'previous_questions': previous_questions,
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }

        res = self.client().post('/quizzes', json=current_info)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        if data['question'] :
            self.assertEqual(data['question']['category'], 1)
            self.assertTrue(data['question']['id'] not in previous_questions)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()