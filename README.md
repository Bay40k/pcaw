# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python a bit more convenient.

## Usage

Define your Canvas domain:

```python
domain = '<canvas>' # e.g. 'canvas.instructure.com'
```

Set your API access token:

```python
access_token = '<token_goes_here>'
```

Initialize pcaw with the domain and access token:

```python
canvasAPI = Pcaw(domain, access_token)
```

## Examples

### Pagination

```python
from pcaw import Pcaw

domain = '<canvas>'
access_token = '<token_goes_here>'
canvasAPI = Pcaw(domain, access_token)

endpoint_to_paginate = 'courses/xxxxx/assignments'

# Automatically paginate and return full array of JSON objects from an endpoint:
canvasAPI.paginate(endpoint_to_paginate, per_page=100)

# Paginate with HTTP parameters
params = {"scope": "sent", "as_user_id": user_id}
canvasAPI.paginate(endpoint_to_paginate, per_page=100, params)
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

### More examples

```python
# Creating a quiz question using create_question method:
course_id = 1234
quiz_id = 1234

# Additional parameters are optional
addn_params = {'question[neutral_comments]': "Neutral Comment"}

canvasAPI.create_question(course_id, quiz_id, "Title", "Text", "essay_question", points=10, addn_params)
```

```python
# Creating a course using genericPOST method:
endpoint = 'accounts/x/courses'
params = {'course[name]': "Course Name", 'course[course_code]': "Course_Code_1234"}

canvasAPI.genericPOST(endpoint, params)
```

### Getting all assignment IDs in a course

```python
from pcaw import Pcaw

domain = '<canvas>'
course_id = 'xxxxxxx'

endpoint = f'courses/{course_id}/assignments'
access_token = '<token_goes_here>'
canvasAPI = Pcaw(domain, access_token)

params = {'example': "parameter"}
assignment_objects = canvasAPI.paginate(endpoint, per_page=100, params)

assignment_ids = []
for assignment in assignment_objects:
    assignment_ids.append(assignment["id"])

print(assignment_ids)

# or

assignment_id_map = map(lambda x: x["id"], assignment_objects)
assignment_ids = list(assignment_id_map)

print(assignment_ids)
```
