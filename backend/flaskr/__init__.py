from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})


    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    
  
    """
    @TODO:
    GET requests for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}
        return jsonify({
            'success': False,
            'categories': formatted_categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        return questions[start:end]

    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = {category.id: category.type for category in Category.query.all()}
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': categories,
            'current_category': None
        })
     
                  
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        db.session.delete(question)
        db.session.commit()
        return jsonify({'success': True, 'deleted': question_id})
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions/add', methods=['POST'])
    def add_question():
        try:
            # Parse the JSON data from the request body
            data = request.get_json()

            # Extract the required fields
            question_text = data.get('question', None)
            answer = data.get('answer', None)
            difficulty = data.get('difficulty', None)
            category = data.get('category', None)
            

            # Validate the required fields
            if not question_text or not answer or not difficulty or not category:
                return jsonify({
                    "success": False,
                    "message": "Missing required fields"
                }), 400

            # Create a new Question object
            new_question = Question(
                question=question_text,
                answer=answer,
                difficulty=difficulty,
                category=category
            )            

            # Add the question to the database
            db.session.add(new_question)
            db.session.commit()

            # Return a success response
            return jsonify({
                "success": True,
                "message": "Question added successfully"
            }), 201

        except Exception as e:
            # Handle unexpected errors
            db.session.rollback()  # Rollback in case of errors
            return jsonify({
                "success": False,
                "message": "An error occurred while processing your request",
                "error": str(e)
            }), 500

        finally:
            db.session.close() 
     
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_questions():
        try:
            # Parse the JSON body from the request
            body = request.get_json()
            search_term = body.get('searchTerm', None)            

            # Validate that searchTerm is provided
            if not search_term:
                abort(400, description="Search term is missing in the request.")

            # Query the database for questions containing the search term (case-insensitive)
            search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            # Format the questions into a list of dictionaries
            formatted_questions = [question.format() for question in search_results]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': None  # You can update this as needed
            })

        except Exception as e:
            # Handle unexpected errors
            print(f"Error during search: {str(e)}")  # Debugging
            abort(500, description="An error occurred while searching for questions.")
        """
        
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id): 
        try:
            # Fetch the category by ID
            category = Category.query.filter_by(id=id).one_or_none()
            if category is None:
                return jsonify({
                    "success": False,
                    "message": "Category not found"
                }), 404

            # Fetch all questions for the given category
            questions = Question.query.filter_by(category=id).all()

            # Format the questions into a list of dictionaries
            questions_data = [{
                "id": question.id,
                "question": question.question,
                "answer": question.answer,
                "difficulty": question.difficulty,
                "category": question.category
            } for question in questions]

            # Construct the response object
            return jsonify({
                "success": True,
                "questions": questions_data,
                "totalQuestions": len(questions_data),
                "currentCategory": category.type
            }), 200

        except Exception as e:
            # Handle unexpected errors
            return jsonify({
                "success": False,
                "message": "An error occurred while processing your request",
                "error": str(e)
            }), 500
            print(f"Category ID received: {id}")  # Debugging
            category = Category.query.filter_by(id=id).first()
            if not category:
                print(f"Category with ID {id} not found")  # Debugging
                return jsonify({
                    "success": False,
                    "message": "Category not found"
                }), 404
            
            questions = Question.query.filter_by(category=id).all()
            questions_data = [{
                "id": question.id,
                "question": question.question,
                "answer": question.answer,
                "category": question.category,
                "difficulty": question.difficulty
            } for question in questions]
            
            response = {
                "success": True,
                "questions": questions_data,
                "total_questions": len(questions_data),
                "current_category": category.type,
            }
            return jsonify(response), 200
  
        
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            # Get the JSON data from the request
            body = request.get_json()
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', None)

            # Validate request data
            if quiz_category is None:
                abort(400, description="Missing 'quiz_category' in request data.")

            # If category is "ALL" (or id=0), retrieve questions from all categories
            if quiz_category['id'] == 0:
                questions_query = Question.query.all()
            else:
                # Retrieve questions only from the selected category
                questions_query = Question.query.filter_by(category=quiz_category['id']).all()

            # Filter out previous questions
            remaining_questions = [question for question in questions_query if question.id not in previous_questions]

            # If no questions remain, return None
            if len(remaining_questions) == 0:
                return jsonify({
                    'success': True,
                    'question': None
                })

            # Select a random question from the remaining questions
            new_question = random.choice(remaining_questions).format()

            return jsonify({
                'success': True,
                'question': new_question
            })

        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging
            abort(500, description="An error occurred while fetching the next question.")
    """
    
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

    return app

