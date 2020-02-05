# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python a bit more convenient.

## Usage

Define a Canvas API endpoint to use (see Canvas API documentation):

```python
url = 'https://<canvas>/courses/xxxxx/assignments'
```

Set your API access token:

```python
access_token = '<token_goes_here>'
```

Initialize pcaw with the access token:

```python
canvasAPI = Pcaw(access_token)
```

## Examples

``` python
from pcaw import Pcaw

url = 'https://<canvas>/courses/xxxxx/assignments'
access_token = '<token_goes_here>'
canvasAPI = Pcaw(access_token)


# Automatically paginate and return full list of objects from an endpoint:
canvasAPI.paginate(url, 100) # (100 is equivalent to the '?per_page=100' parameter)

# Paginate with HTTP parameters
params = {"scope": "sent", "as_user_id": user_id}
canvasAPI.paginate(url, 100, params)

# You can also easily reference your access token/Authorization header with:
canvasAPI.headers
# Returns: {'Authorization': "Bearer <token_goes_here>"}
# canvasAPI.access_token returns: <token_goes_here>

# Useful for something like:
import requests
requests.get(url, headers=canvasAPI.headers)

# And to add your own headers you could do:
requests.get(url, headers={**canvasAPI.headers, 'your_own': "headers"})

# Creating a course using genericPOST method:
url = 'https://<canvas>/api/v1/accounts/x/courses'
params = {'course[name]': "Course Name", 'course[course_code]': "Course_Code_1234"}
canvasAPI.genericPOST(url, params)

# Could also be written as:
requests.post(url, headers=canvasAPI.headers, data=params) 

```
