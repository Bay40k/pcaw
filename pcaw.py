import requests
from json.decoder import JSONDecodeError
import json
from pprint import pprint
from requests.compat import urljoin
import urllib.parse

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.
# TODO: implement logger
#       verify __init__ 'domain' variable URL formatting


class Pcaw:
    def __init__(self, domain, access_token, show_responses=False):
        self.headers = {'Authorization': f"Bearer {access_token}"}
        self.access_token = access_token
        self.show_responses = show_responses
        parsed_domain = urllib.parse.ParseResult("https", domain, "/api/v1/",
                                                 params='', query='',
                                                 fragment='')
        self.domain = parsed_domain.geturl()

        print(f"pcaw: Initalized; Domain: {self.domain}")

    def json_pretty_print(self, json_string):
        try:
            json_loads = json.loads(json_string)
            json_dumps = json.dumps(json_loads, indent=2)
            print(json_dumps)
        except JSONDecodeError:
            if self.show_responses:
                print("ERROR: The response is not valid JSON. Possibly HTML?"
                      f"\nRaw Response:\n{json_string}")
            else:
                print("ERROR: The response is not valid JSON. Possibly HTML?"
                      "\nEnable show_responses to see raw response")

    def genericPOST(self, endpoint, data):
        """
        Generic POST request function that passes your desired parameters to a
        desired endpoint, using self.headers

        Enable show_responses to print the HTTP responses from this method
        """
        endpoint = urljoin(self.domain, endpoint)
        print(f"pcaw: Requesting URL: {endpoint}")

        r = requests.post(endpoint, data=data, headers=self.headers)

        if "errors" in r.text:
            print("pcaw: Canvas API returned error(s):")
            if not self.show_responses:
                self.json_pretty_print(r.text)

        if self.show_responses:
            print("pcaw: Response:")
            self.json_pretty_print(r.text)

        if r.status_code != requests.codes.ok:
            print("pcaw: ERROR: Bad Response:")
            self.json_pretty_print(r.text)

        assert r.status_code == requests.codes.ok, "pcaw: Request not OK, " \
            f"response code: {r.status_code}"

        print(f"pcaw: Success; POST request to '{endpoint}' sucessful")

    def paginate(self, endpoint, per_page=100, params=None):
        """
        Returns all items/JSON objects (in an array) from an endpoint
        / handles pagination
        """
        endpoint = urljoin(self.domain, endpoint)
        print(f"pcaw: paginating: {endpoint}")

        per_page_url = endpoint + f"?per_page={per_page}"
        r = requests.get(per_page_url, headers=self.headers, params=params)

        print(f"Full URL with HTTP params: {r.url}")

        assert "/api/v1" in endpoint, \
            "pcaw: /api/v1 was not found in the passed URL."

        assert r.status_code != 401, "pcaw: 401 Unauthorized, is your " \
            "access token correct?"

        assert r.status_code == requests.codes.ok, "pcaw: Request not OK, " \
            f"response code: {r.status_code}"

        assert "Log In to Canvas" not in r.text, "pcaw: Canvas login page " \
            "reached, is your access token correct?"

        try:
            raw = r.json()
        except JSONDecodeError as e:
            print(f"ERROR: The response is not valid JSON. {e}")
            raise
        except Exception as e:
            print(f"ERROR: There was an unexpected error: {e}")
            raise

        item_set = []

        print('pcaw: paginating: Going through first page...')
        for item in raw:
            # print(item)
            item_set.append(item)

        print('pcaw: paginating: Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers=self.headers)
            raw = r.json()
            for item in raw:
                # print(item)
                item_set.append(item)

        if not item_set:
            print(f"pcaw: There were no objects found at this endpoint: {r.url}")

        print(f"pcaw: Success; Sucessfully paginated endpoint: {r.url}")
        return item_set

    def check_type(self, variable_name, object_to_check, intended_type):
        """
        Function that checks to make sure objects are the right type
        """
        assert isinstance(object_to_check, intended_type), \
            f"'{variable_name}' must be type '{intended_type.__name__}', " \
            f"instead it's: '{type(object_to_check).__name__}'"

    def create_question(self, course_id, quiz_id, name,
                        text, q_type, points, addtional_params={}):
        """
        Creates a quiz question

        POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions
        https://canvas.instructure.com/doc/api/quiz_questions.html#method.quizzes/quiz_questions.create
        """
        self.check_type("additional_params", addtional_params, dict)
        self.check_type("points", points, int)
        self.check_type("name", name, str)
        self.check_type("text", text, str)
        self.check_type("q_type", q_type, str)
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)

        questions_endpoint = urljoin(self.domain, f"courses/{course_id}/quizzes/{quiz_id}/questions")

        question_types = ["calculated_question", "essay_question",
                          "file_upload_question",
                          "fill_in_multiple_blanks_question",
                          "matching_question", "multiple_answers_question",
                          "multiple_choice_question",
                          "multiple_dropdowns_question",
                          "numerical_question", "short_answer_question",
                          "text_only_question", 'true_false_question']

        assert q_type in question_types, f"Not a valid question type: {q_type}"

        params = {
            "question[question_name]": name,
            "question[question_text]": text,
            "question[question_type]": q_type,
            "question[points_possible]": points
        }

        print(f"pcaw: Creating '{q_type}' question at: {questions_endpoint}")

        full_params = {**params, **addtional_params}
        print("Parameters:")
        pprint(full_params, width=1)

        self.genericPOST(questions_endpoint, full_params)
