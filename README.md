# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python simple, allowing for easy creation of Canvas API tools.

## Usage

Initialize pcaw with your Canvas insance's domain and API  access token:

```python
from pcaw import Pcaw

domain = '<canvas>' # e.g. 'canvas.instructure.com'
access_token = '<token_goes_here>'

canvas_api = Pcaw(domain, access_token)
```

## Logging

```python
# There are 3 logging levels:
# "Error"   - Only print Errors to console
# "Warning" - Print warnings and errors to console (default)
# "Info"    - Prints most information to console, useful for debugging

# You can also enable "show_responses" to print HTTP responses to the console
canvas_api = Pcaw(domain, access_token, show_responses=True, log_level="info")

# Positional args
canvas_api = Pcaw(domain, access_token, True, "info")

# Omittable
canvas_api = Pcaw(domain, access_token)
```

## Examples

### Pagination

```python
from pcaw import Pcaw

canvas_api = Pcaw(domain, access_token)

endpoint_to_paginate = 'accounts/xxxxx/courses/xxxxx/assignments'

# Automatically paginate and return full array of JSON objects from an endpoint:
# per_page defaults to 100, therefore omittable
assigments = canvas_api.paginate(endpoint_to_paginate, per_page=100)

# Paginate with HTTP parameters
params = {"param": "value", "as_user_id": "<user id>"}
assignments = canvas_api.paginate(endpoint_to_paginate, params=params)
```

### Authorization headers

```python
# You can also easily reference your access token/Authorization header with:
canvas_api.headers
# Returns: {'Authorization': "Bearer <token_goes_here>"}
# canvas_api.access_token returns: <token_goes_here>

# Useful for something like:
import requests
requests.get(url, headers=canvas_api.headers)

# And to add your own headers you could do:
requests.get(url, headers={**canvas_api.headers, 'your_own': "headers"})
```

### More examples

#### Creating a course using `post()` method, returns JSON Course object

```python
canvas_api = Pcaw(domain, access_token)

account_id = 1234
endpoint = f'accounts/{account_id}/courses'

params = {'course[name]': "Course Name",
          'course[course_code]': "Course_Code_1234"}

canvas_api.post(endpoint, params)
```

#### Getting a single course using `get()` method, returns JSON Course object

```python
canvas_api = Pcaw(domain, access_token)

course_id = 123456
account_id = 1234
endpoint = f'accounts/{account_id}/courses/{course_id}'

course = canvas_api.get(endpoint)

course["id"] # Returns: 123456
```

#### Extending Pcaw object with custom `Assignment` object and `get_assignment()` method
```python
from pcaw import Pcaw

class Assignment:
    def __init__(self, id:int, course: int, account: int, obj: dict):
        if not account:
            self.account = None
        else:
            self.account = account
        self.course = course
        self.id = id
        self.obj = obj

class MyPcaw(Pcaw):
    def __init__(self, domain: str, access_token: str):
        super().__init__(domain, access_token)

    def get_assignment(self, assignment_id: int, course: int, 
                       account: int = None, params: dict = None) -> Assignment:
        if not params:
            params = {}
        if account:
            account = f"accounts/{account}/"
        else:
            account = ""
        endpoint = f"{account}courses/{course}/assignments/{assignment_id}"
        assigment = self.get(endpoint, params)
        return Assignment(assignment_id, course, account, assigment)

canvas_api = MyPcaw(domain, access_token)
assignment = canvas_api.get_assignment(assignment_id, course, account)

assignment.id # Returns assignment's id
assignment.obj # Returns assignment raw JSON object (dict)
```

#### Getting all assignment IDs in a course

```python
canvas_api = Pcaw(domain, access_token)

course_id = 1234
endpoint = f'courses/{course_id}/assignments'

params = {'example': "parameter"}
assignment_objects = canvas_api.paginate(endpoint, params)

assignment_ids = []
for assignment in assignment_objects:
    assignment_ids.append(assignment["id"])

print(assignment_ids)

# or

assignment_ids = [a["id"] for a in assignment_objects]

print(assignment_ids)
```
