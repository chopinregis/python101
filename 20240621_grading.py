def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # Handle both JSON and URL-encoded form data
    request_json = request.get_json(silent=True)
    request_args = request.args
 
    number = None
 
    if request_args and 'number' in request_args:
        number = request_args['number']
    elif request_json and 'number' in request_json:
        number = request_json['number']
 
    if number is None:
        return 'Please provide a number as a query parameter or in the request body.', 400
 
    try:
        number = int(number)
    except ValueError:
        return 'The provided number must be an integer.', 400
 
    if number < 0:
        return 'Factorial is not defined for negative numbers.', 400
 
    result = 1
    for i in range(1, number + 1):
        result *= i
 
    return f'\nThe factorial of {number} is {result}.'



def grades(request):
    """Grades a student's exam."""
    # Handle both JSON and URL-encoded form data
    request_json = request.get_json(silent=True)
    request_args = request.args

    score = None
    if request_args and 'score' in request_args:
        score = request_args['score']
    elif request_json and 'score' in request_json:
        score = request_json['score']

    if score is None:
        return 'Please provide a score as a query parameter or in the request body.', 400

    try:
        score = int(score)
    except ValueError:
        return 'The provided score must be an integer.', 400

    if score < 0 or score > 100:
        return 'The provided score must be between 0 and 100.', 400

    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'
    

import random

animals = ["cat", "dog", "bird", "fish", "snake"]

def choose_animal(request):
  """Chooses a random animal and displays a fun message.

  Args:
      request (flask.Request): HTTP request object (not used in this example).

  Returns:
      A string containing a fun message with a random animal.
  """
  chosen_animal = random.choice(animals)
  message = f"""
  <h1>Surprise! You've encountered a {chosen_animal.title()} in the wild!</h1>
  <p>Click the button below to see another animal.</p>
  <button onclick="window.location.reload()">Try Again</button>
  """
  return message



def grades(request):
  """Grades a student's exam based on score provided in JSON or query parameters.
  Args:
      request (flask.Request): HTTP request object.
  Returns:
      A string containing the letter grade or an error message.
  """
  # Ensure the function works without Flask dependencies
  request_json = request.get_json(silent=True)
  request_args = request.args
