from json.decoder import JSONDecodeError
from typing import List
from urllib.parse import ParseResult
from urllib.parse import urljoin
import json
import pprint
import requests

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.


class Pcaw:
    def __init__(self, domain: str, access_token: str, show_responses: bool = False, log_level: str = "WARNING"):
        """
        Enable show_responses to show HTTP responses from requests method
        """
        self.headers = {'Authorization': f"Bearer {access_token}"}
        self.access_token = access_token
        self.show_responses = show_responses
        parsed_domain = ParseResult(scheme="https", netloc=domain, path="/api/v1/", params='', query='', fragment='')
        self.domain = parsed_domain.geturl()

        self.log_level = log_level
        self.log("init", f"Initalized; Domain: {self.domain}")

    def log(self, f_name: str, string: str, log_level: str = "INFO"):
        """
        Method that handles logging
        """
        function_name = f_name
        log_level = log_level.upper()
        self.log_level = self.log_level.upper()
        log_levels = ["INFO", "WARNING", "ERROR"]

        assert self.log_level in log_levels, f"FATAL: Not a valid log_level {log_level}"

        print_log = False

        if log_level in ["INFO", "WARNING"]:
            if self.log_level == log_level:
                print_log = True

        if log_level == "ERROR":
            print_log = True

        if print_log:
            print(f"pcaw: {log_level}: {function_name}: {string}")

    def format_json(self, json_object: dict) -> str:
        """
        Takes an ugly JSON pbject (from a response)
        and returns a nicely formatted JSON object
        """
        f_name = "format_json"  # Used for logging

        try:
            json_dumps = json.dumps(json_object, indent=2)
            return(json_dumps)

        except JSONDecodeError:
            self.log(f_name, "The response is not valid JSON. Possibly HTML?"
                     f"\nRaw Response:\n{json_object}", "ERROR")
            raise

    def request(self, url: str, request_type: str, params: dict = None) -> requests.Response:
        """
        Generic HTTP request function that passes your desired parameters to a
        desired URL, using self.headers

        Returns HTTP response object
        """
        f_name = "request"
        request_type = request_type.upper()

        # Currently supported types
        request_types = ["GET", "POST", "PUT", "DELETE"]

        assert request_type in request_types, \
            f"FATAL: Not a valid request type: {request_type}"

        if request_type in ["POST", "PUT"]:
            assert params, f"FATAL: 'params' not specified for {request_type} request"

        self.log(f_name, f"{request_type} Requesting URL: {url}")

        r = None
        args = {"url": url, "headers": self.headers}
        if request_type == "POST":
            r = requests.post(data=params, **args)
        elif request_type == "PUT":
            r = requests.put(data=params, **args)
        elif request_type == "GET":
            r = requests.get(params=params, **args)
        elif request_type == "DELETE":
            r = requests.delete(params=params, **args)

        assert r.status_code != 401, "FATAL: 401 Unauthorized, is your " \
            "access token correct?"

        if "errors" in r.text:
            self.log(f_name, f"Canvas API returned error(s): \n{r.text}",
                     "ERROR")

        assert r.status_code == requests.codes.ok, "FATAL: Request not OK, " \
            f"response status code: {r.status_code}" \
            f"\nResponse: \n{r.text}"

        try:
            json_response = r.json()
        except JSONDecodeError as e:
            self.log(f_name, f"The response is not valid JSON. \n{e}", "ERROR")
            raise
        except Exception as e:
            self.log(f_name, f"There was an unexpected error: \n{e}", "ERROR")
            raise

        response = self.format_json(json_response)

        self.log(f_name, f"Success; {request_type} request to '{url}' sucessful")
        if self.show_responses:
            self.log(f_name, f"Response: \n{response}")

        return r

    def post(self, endpoint: str, params: dict) -> dict:
        """
        Generic POST request function that passes your desired
        parameters to a desired endpoint, using self.headers

        Returns JSON object of response
        """
        url = urljoin(self.domain, endpoint)

        r = self.request(url, request_type="POST", params=params)

        return r.json()

    def paginate(self, endpoint: str, per_page: int = 100, params: dict = None) -> List[dict]:
        """
        Returns all items/JSON objects (in an array) from an endpoint
        / handles pagination
        """
        if not params:
            params = {}
        f_name = "paginate"
        self.log(f_name, f"Paginating: {endpoint}")

        endpoint = urljoin(self.domain, endpoint)
        params = {"per_page": per_page, **params}

        r = self.request(endpoint, "GET", params)
        json_response = r.json()

        self.log(f_name, f"Full URL with HTTP params: {r.url}")

        item_set = []

        self.log(f_name, 'Going through first page...')
        for item in json_response:
            item_set.append(item)

        self.log(f_name, 'Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = self.request(r.links['next']['url'], "GET", params)
            json = r.json()
            for item in json:
                item_set.append(item)

        if not item_set:
            self.log(f_name, f"There were no objects found at this endpoint: {r.url}", "WARNING")

        self.log(f_name, f"Success; Sucessfully paginated endpoint: {r.url}")
        return item_set

    def get(self, endpoint: str, params: dict = None) -> dict:
        """
        Generic GET function to get/return a single JSON object from an endpoint
        """
        if not params:
            params = {}
        f_name = "get"

        full_url = urljoin(self.domain, endpoint)

        self.log(f_name, f"Getting JSON object from: {full_url}")
        if params:
            pretty_params = pprint.pformat(params, width=50)
            self.log(f_name, f"Additional parameters: \n{pretty_params}")

        response = self.request(full_url, "GET", params=params)
        response = response.json()

        self.log(f_name, f"Success; JSON object URL: {full_url}")

        return response
