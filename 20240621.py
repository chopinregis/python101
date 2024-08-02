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