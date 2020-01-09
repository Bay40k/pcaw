import requests

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.
class Pcaw:
    def __init__(self, access_token):
        self.headers = {'Authorization': f"Bearer {access_token}"}

    # Generic POST request function that passes your desired parameters to a desired endpoint
    def genericPOST(self, endpoint, data):
        try:
            r = requests.post(endpoint, data=data, headers=self.headers)
            print(r.text)
        except Exception as e:
            print(f"There was an error running the request: {e}")

    # Returns all items/objects (in an array) from an endpoint / handles pagination
    def paginate(self, url, per_page):
        url = url + f"?per_page={per_page}"
        r = requests.get(url, headers=self.headers)
        raw = r.json()
        item_set = []

        print('Going through first page...')
        for item in raw:
            # print(item_set)
            item_set.append(item)

        print('Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers=self.headers)
            raw = r.json()
            for item in raw:
                # print(item)
                item_set.append(item)

        return item_set
