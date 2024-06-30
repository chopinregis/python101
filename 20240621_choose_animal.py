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
