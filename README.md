# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python simple, allowing for easy creation of Canvas API tools.

## Usage

Initialize pcaw with your Canvas insance's domain and API  access token:

```python
from pcaw import Pcaw

domain = '<canvas>' # e.g. 'canvas.instructure.com'
access_token = '<token_goes_here>'

canvasAPI = Pcaw(domain, access_token)
```

## Logging

```python
# There are 3 logging levels:
# "Error"   - Only print Errors to console
# "Warning" - Print warnings and errors to console (default)
# "Info"    - Prints most information to console, useful for debugging

# You can also enable "show_responses" to print HTTP responses to the console
canvasAPI = Pcaw(domain, access_token, show_responses=True, log_level="info")

# Positional args
canvasAPI = Pcaw(domain, access_token, True, "info")
```

## Examples

### Pagination

```python
from pcaw import Pcaw

canvasAPI = Pcaw(domain, access_token)

endpoint_to_paginate = 'courses/xxxxx/assignments'

# Automatically paginate and return full array of JSON objects from an endpoint:
# per_page defaults to 100, therefore omittable
canvasAPI.paginate(endpoint_to_paginate, per_page=100)

# Paginate with HTTP parameters
params = {"scope": "sent", "as_user_id": user_id}
canvasAPI.paginate(endpoint_to_paginate, params=params)
```

### Authorization headers

```python
# You can also easily reference your access token/Authorization header with:
canvasAPI.headers
# Returns: {'Authorization': "Bearer <token_goes_here>"}
# canvasAPI.access_token returns: <token_goes_here>

# Useful for something like:
import requests
requests.get(url, headers=canvasAPI.headers)

# And to add your own headers you could do:
requests.get(url, headers={**canvasAPI.headers, 'your_own': "headers"})
```

### Quizzes module

#### Creating a quiz using `create_quiz()` method

```python
canvasAPI = Pcaw(domain, access_token)

canvasAPI.create_quiz(1234, title="Quiz title",
                      description="Quiz description", quiz_type="assignment")

# Alternatively:
details = {
    "course_id": 1234,
    "title": "Quiz title",
    "description": "Quiz description",
    "quiz_type": "assignment", # Graded quiz
}

# Referencable JSON Canvas Quiz object
quiz = canvasAPI.create_quiz(**details)
```

#### Get JSON Quiz object from existing quiz using `get_quiz()` method

```python
canvasAPI = Pcaw(domain, access_token)

# Feel free to omit keyword arguments in favor of positional args
quiz = canvasAPI.get_quiz(course_id=15, quiz_id=7670)

quiz["id"] # Returns: 7670

# Additional parameters are optional (this applies to all pcaw Quizzes methods)
addn_params = {'example': "parameter"}
quiz = canvasAPI.get_quiz(15, 7670, params=addn_params)
```

#### Get all questions from a quiz using `get_questions()` method, returns array of JSON QuizQuestion objects

```python
canvasAPI = Pcaw(domain, access_token)

# quiz_submission_id and quiz_submission_attempt are optional
questions = canvasAPI.get_questions(quiz["id"], quiz_submission_id=1234, quiz_submission_attempt=1)

# Nicely print each question:
for question in questions:
    print(canvasAPI.format_json(question))
    # Can do something else with each question here

# Easily print all questions:
print(canvasAPI.format_json(questions))
```

#### Creating a quiz question using `create_question()` method, returns JSON QuizQuestion object

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 1234
quiz_id = 1234

# Use quiz object:
quiz_id = quiz["id"]

addn_params = {'question[neutral_comments]': "Neutral Comment"}

canvasAPI.create_question(course_id, quiz_id,
                          title="Title", text="Text", q_type="essay_question",
                          pontis=10, params=addn_params)
# Alternatively:
question_details = {
    "course_id": course_id,
    "quiz_id": quiz_id,
    "title": "Title",
    "text": "Text",
    "q_type": "essay_question",
    # Optional
    "points": 10, # Defaults to 1
    "params": addn_params
}

canvasAPI.create_question(**question_details)
```

### More examples

#### Creating a course using `post()` method

```python
canvasAPI = Pcaw(domain, access_token)

account_id = 1234
endpoint = f'accounts/{account_id}/courses'

params = {'course[name]': "Course Name",
          'course[course_code]': "Course_Code_1234"}

canvasAPI.post(endpoint, params)
```

#### Getting a single course as a JSON Course object using `get()` method

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 123456
endpoint = f'courses/{course_id}'

# or (per API documentation)

account_id = 1234
endpoint = f'accounts/{account_id}/courses/{course_id}'

course = canvasAPI.get(endpoint)

course["id"] # Returns: 123456
```

#### Getting all assignment IDs in a course

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 1234
endpoint = f'courses/{course_id}/assignments'

params = {'example': "parameter"}
assignment_objects = canvasAPI.paginate(endpoint, params)

assignment_ids = []
for assignment in assignment_objects:
    assignment_ids.append(assignment["id"])

print(assignment_ids)

# or

assignment_id_map = map(lambda x: x["id"], assignment_objects)
assignment_ids = list(assignment_id_map)

print(assignment_ids)
```
