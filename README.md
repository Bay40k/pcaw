# pcaw (Python Canvas API Wrapper)

pcaw makes accessing and using the Canvas LMS REST API through Python a bit more convenient.

#### Usage:
Define a Canvas API endpoint to use (see Canvas API documentation):
```python
url = 'https://example.instructure.com/courses/xxxxx/assignments'
```

Set your API access token:
```python
access_token = 'token_goes_here'
```

Initialize pcaw with the access token:
```python
canvasAPI = Pcaw(access_token)
```

#### Example:
``` python
url = 'https://example.instructure.com/courses/xxxxx/assignments'
access_token = 'token_goes_here'
canvasAPI = Pcaw(access_token)


# Return a paginated list of objects from an endpoint:
canvasAPI.paginate(URL, 100) # (100 means 100 items per page)

# You can also easily reference your access token/Authorization header with:
canvasAPI.headers 
# ( Returns: {'Authorization': f"Bearer {access_token}"} )
```
