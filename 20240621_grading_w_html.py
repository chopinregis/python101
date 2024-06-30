import random

def grades(request):
    """Grades a student's exam based on score provided in JSON or query parameters, with HTML interface.

    Args:
        request (flask.Request): HTTP request object.

    Returns:
        An HTML string containing the letter grade or a form to input the score.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    score = None
    if request_args and 'score' in request_args:
        score = request_args['score']
    elif request_json and 'score' in request_json:
        score = request_json['score']

    if score is None:
        # HTML form for score input
        return """
        <html>
            <head><title>Grade Calculator</title></head>
            <body>
                <h1>Please enter your score:</h1>
                <form method="get">
                    <input type="text" name="score">
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        """, 200

    try:
        score = int(score)
    except ValueError:
        return 'The provided score must be an integer.', 400

    if score < 0 or score > 100:
        return 'The provided score must be between 0 and 100.', 400

    grade = None
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    elif score >= 60:
        grade = 'D'
    else:
        grade = 'F'

    # Display the result with an HTML button to try again
    return f"""
    <html>
        <head><title>Grade Result</title></head>
        <body>
            <h1>Your grade is: {grade}</h1>
            <button onclick="window.location='{request.url}';">Try Again</button>
        </body>
    </html>
    """, 200
