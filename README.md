# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python a bit more convenient.

## Usage

Initialize pcaw with your Canvas insance's domain and API  access token:

```python
from pcaw import Pcaw

domain = '<canvas>' # e.g. 'canvas.instructure.com'
access_token = '<token_goes_here>'

canvasAPI = Pcaw(domain, access_token)
```

## Examples

### Pagination

```python
from pcaw import Pcaw

canvasAPI = Pcaw(domain, access_token)

endpoint_to_paginate = 'courses/xxxxx/assignments'

# Automatically paginate and return full array of JSON objects from an endpoint:
canvasAPI.paginate(endpoint_to_paginate, per_page=100)

# Paginate with HTTP parameters
params = {"scope": "sent", "as_user_id": user_id}
canvasAPI.paginate(endpoint_to_paginate, params, per_page=100)
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

canvasAPI.create_quiz(course_id=1234, title="Quiz title",
                      description="Quiz description", quiz_type="graded_quiz")

# Alternatively:
details = {
    "course_id": 1234,
    "title": "Quiz title",
    "description": "Quiz description",
    "quiz_type": "graded_quiz",
}

# Referencable quiz object AKA pcaw quiz object
quiz = canvasAPI.create_quiz(**details)
```

#### Generate quiz object from existing quiz using `get_quiz()` method

```python
quiz = canvasAPI.get_quiz(quiz_id=7670, course_id=15)

# Additional parameters are optional (this applies to all pcaw Quizzes methods)
addn_params = {'example': "parameter"}
quiz = canvasAPI.get_quiz(quiz_id=7670, course_id=15, additional_parameters=addn_params)

quiz.id # Returns: 7670
```

#### Creating a quiz question using `create_question()` method

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 1234
quiz_id = 1234

# Use quiz object:
course_id = quiz.course_id
quiz_id = quiz.id

addn_params = {'question[neutral_comments]': "Neutral Comment"}

canvasAPI.create_question(course_id=course_id, quiz_id=quiz_id,
                          title="Title", text="Text", q_type="essay_question",
                          additional_params=addn_params, points=10)
# Alternatively:
question_details = {
    "course_id": course_id,
    "quiz_id": quiz_id,
    "title": "Title",
    "text": "Text",
    "q_type": "essay_question",
    # Optional
    "points": 10, # Defaults to 1
    "additional_params": addn_params
}

canvasAPI.create_question(**question_details)
```

### More examples

#### Creating a course using genericPOST method

```python
canvasAPI = Pcaw(domain, access_token)

account_id = 1234
endpoint = f'accounts/{account_id}/courses'

params = {'course[name]': "Course Name",
          'course[course_code]': "Course_Code_1234"}

canvasAPI.genericPOST(endpoint, params)
```

#### Getting all assignment IDs in a course

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 1234
endpoint = f'courses/{course_id}/assignments'

params = {'example': "parameter"}
assignment_objects = canvasAPI.paginate(endpoint, params, per_page=100)

assignment_ids = []
for assignment in assignment_objects:
    assignment_ids.append(assignment["id"])

print(assignment_ids)

# or

assignment_id_map = map(lambda x: x["id"], assignment_objects)
assignment_ids = list(assignment_id_map)

print(assignment_ids)
```
