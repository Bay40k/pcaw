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

#### Creating a quiz using create_quiz method

```python
canvasAPI = Pcaw(domain, access_token)

details = {
    "course_id": course_id,
    "title": "Quiz title",
    "description": "Quiz description",
    "quiz_type": "graded_quiz"
}

# Referencable quiz object
quiz = canvasAPI.create_quiz(**details)
```

#### Creating a quiz question using create_question method

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 1234
quiz_id = 1234

# You can reference a quiz object as well:
quiz_id = quiz.id

# Additional parameters are optional
addn_params = {'question[neutral_comments]': "Neutral Comment"}

canvasAPI.create_question(course_id, quiz_id,
                          "Title", "Text", "essay_question", addn_params, points=10)
# Alternatively:
question_details = {
    "course_id": course_id,
    "quiz_id": quiz_id,
    "name": "Title",
    "text": "Text",
    "q_type": "essay_question",
    "additional_params": addn_params,
    "points": 10
}

canvasAPI.create_question(**question_details)
```

### More examples

#### Creating a course using genericPOST method

```python
canvasAPI = Pcaw(domain, access_token)

endpoint = 'accounts/x/courses'
params = {'course[name]': "Course Name", 'course[course_code]': "Course_Code_1234"}

canvasAPI.genericPOST(endpoint, params)
```

#### Getting all assignment IDs in a course

```python
canvasAPI = Pcaw(domain, access_token)

course_id = 'xxxxxxx'
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
