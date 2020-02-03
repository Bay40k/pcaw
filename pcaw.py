import requests
from json.decoder import JSONDecodeError

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.
# TODO: implement logger


class Pcaw:
    def __init__(self, access_token):
        self.headers = {'Authorization': f"Bearer {access_token}"}

    def genericPOST(self, endpoint, data):
        """
        Generic POST request function that passes your desired parameters to a
        desired endpoint, using self.headers
        """
        try:
            r = requests.post(endpoint, data=data, headers=self.headers)
            print(r.text)
        except Exception:
            print(f"ERROR: There was an error running \
                the request: {Exception}")
            raise

    def paginate(self, url, per_page, params=None):
        """
        Returns all items/objects (in an array) from an endpoint
        / handles pagination
        """
        print("pcaw: paginating\n")

        per_page_url = url + f"?per_page={per_page}"
        r = requests.get(per_page_url, headers=self.headers, params=params)

        print(f"Full URL with HTTP params: {r.url}")

        assert "/api/v1" in url, "/api/v1 was not found in the passed URL."
        assert r.status_code != 401, "401 Unauthorized, is your access " \
            "token correct?"

        assert r.status_code == requests.codes.ok, "Request not OK, " \
            f"response code: {r.status_code}"

        assert "Log In to Canvas" not in r.text, "Canvas login page " \
            "reached, is your access token correct?"

        try:
            raw = r.json()
        except JSONDecodeError:
            print("ERROR: The response is not valid JSON. \n")
            raise
        except Exception as e:
            print(f"ERROR: There was an unexpected error. {e}\n")
            raise

        item_set = []

        print('Going through first page...')
        for item in raw:
            # print(item)
            item_set.append(item)

        print('Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers=self.headers)
            raw = r.json()
            for item in raw:
                # print(item)
                item_set.append(item)

        if not item_set:
            print(f"There were no objects found at this endpoint: {r.url}")

        return item_set
