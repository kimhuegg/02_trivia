import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = [c.format() for c in categories]

      # format for catgories
      converted_categpries = {}
      for c in formatted_categories:
          converted_categpries[c.get('id')] = c.get('type')
        
      return jsonify({
        'success': True,
        'categories': converted_categpries,
        'total_categories': len(formatted_categories)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
      try:
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = [c.format() for c in questions]
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [c.format() for c in categories]

        # format for questions
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        if page:
          return_questions = formatted_questions[start:end]
        else:
           return_questions = formatted_questions[0:10]

        # format for catgories
        converted_categpries = {}
        for c in formatted_categories:
            converted_categpries[c.get('id')] = c.get('type')
        
        return jsonify({
            'success': True,
            'questions': return_questions,
            'total_questions': len(formatted_questions),
            'categories': converted_categpries
          })
      except:
        abort(422)
  
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      if question is None:
        abort(404)
      else:
        question.delete()
        return jsonify({
            "success": True,
            "question": question.format()
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])     
  def create_question():
    try:
      body = request.get_json()

      new_question = body.get('question')
      new_answer = body.get('answer')
      new_category = body.get('category')
      new_difficulty = body.get('difficulty')

      #if 
      if new_question and new_answer and new_category and new_difficulty: 
        question = Question(new_question, new_answer, new_category, new_difficulty)
        question.insert()

        # format return question
        selection = Question.query.order_by(Question.id).all()
        formatted_questions = [c.format() for c in selection]

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        if page:
          return_questions = formatted_questions[start:end]
        else:
          return_questions = formatted_questions[0:10]

        return jsonify({
          'success': True,
          'created': question.id,
          'questions': return_questions,
          'total_questions': len(formatted_questions),
        })
      else:
        abort(422)

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])     
  def search_questions():
    try:
        body = request.get_json()
        search_term = body.get('searchTerm')

        # format return question
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
        formatted_questions = [c.format() for c in selection]

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        if page:
          return_questions = formatted_questions[start:end]
        else:
          return_questions = formatted_questions[0:10]

        return jsonify({
          'success': True,
          'questions': return_questions,
          'total_questions': len(formatted_questions),
        })


    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')     
  def get_questions_by_category(category_id):
    try:
        # format return question
        selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
          abort(422)
        formatted_questions = [c.format() for c in selection]

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        if page:
          return_questions = formatted_questions[start:end]
        else:
          return_questions = formatted_questions[0:10]

        return jsonify({
          'success': True,
          'questions': return_questions,
          'total_questions': len(formatted_questions),
          'current_category': category.format()['type'],
        })


    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_questions_to_play():
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions')
      quiz_category = body.get('quiz_category')
      questions = None
      if quiz_category['id'] == 0:
        questions = Question.query.order_by(Question.id).all()
      else:
        questions = Question.query.filter(Question.category == quiz_category['id']).order_by(Question.id).all()

      list_random_questions = [q.format() for q in questions if q.id not in previous_questions]
      total_questions = len(list_random_questions)
      print(list_random_questions)

      #random question
      if total_questions > 0:
        randomNum = random.randint(0, total_questions - 1 )
        return_question = list_random_questions[randomNum]

        return jsonify({
          'success': True,
          'question': return_question
        })
      else:
        return jsonify({
          'success': True,
        })
    except:
      abort(422)
    return

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
  @app.errorhandler(404)
  def notfound(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
      }), 404
  
  return app

    