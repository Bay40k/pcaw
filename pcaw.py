import requests
from json.decoder import JSONDecodeError
import json
from pprint import pprint
from requests.compat import urljoin
import urllib.parse

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.
# TODO: - implement logger
#       - verify __init__ 'domain' variable URL formatting
#       - in progress - implement endpoints as classes, with mixins for them
#           in the "Pcaw" class, e.g. 'Pcaw(Quizzes):'
#       - change genericPOST method name to just 'post'
#       - make QuizObject class
#       - move mixin classes to separate files?
#       - refactor paginate method to use request method
#       - implement get_questions Quizzes method


class Quizzes:
    def __init__(self):
        pass

    def get_quiz(self, quiz_id, course_id, additional_params={}):
        """
        Gets a single quiz, returns pcaw quiz object

        GET /api/v1/courses/:course_id/quizzes/:id
        https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.show
        """
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("course_id", course_id, int)
        self.check_type("additional_params", additional_params, dict)

        full_endpoint = f"courses/{course_id}/quizzes/{quiz_id}"

        quiz_url = urljoin(self.domain, full_endpoint)

        print(f"pcaw: get_quiz: Generating quiz object from: {quiz_url}")
        if additional_params:
            print(f"Additional parameters:")
            pprint(additional_params, width=50)

        response = self.request(quiz_url, "GET", data=additional_params)

        self.json_pretty_print(response.text, check=True)

        response = response.json()
        self.id = response["id"]
        self.html_url = response["html_url"]
        self.course_id = course_id

        print(f"pcaw: get_quiz: Success; Quiz object URL: {self.html_url}")

        return self

    def create_quiz(self, course_id, title, description, quiz_type,
                    additional_params={}):
        """
        Creates a quiz, returns pcaw quiz object

        POST /api/v1/courses/:course_id/quizzes
        https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.create
        """
        self.check_type("course_id", course_id, int)
        self.check_type("title", title, str)
        self.check_type("description", description, str)
        self.check_type("quiz_type", quiz_type, str)
        self.check_type("additional_params", additional_params, dict)

        quiz_types = ["practice_quiz", "assignment", "graded_survey", "survey"]

        assert quiz_type in quiz_types, \
            f"pcaw: Not a valid quiz type: {quiz_type}"

        full_endpoint = f"courses/{course_id}/quizzes/"

        quizzes_endpoint = urljoin(self.domain, full_endpoint)

        params = {
            "quiz[title]": title,
            "quiz[description]": description,
            "quiz[quiz_type]": quiz_type
        }

        print(f"pcaw: create_quiz: Creating '{quiz_type}' quiz at: {quizzes_endpoint}")

        full_params = {**params, **additional_params}
        print("Final parameters:")
        pprint(full_params, width=50)

        response = self.genericPOST(quizzes_endpoint, full_params)

        self.id = response["id"]
        self.html_url = response["html_url"]
        self.course_id = course_id

        print(f"pcaw: create_quiz: New quiz URL: {self.html_url}")

        return self

    def create_question(self, title, text, q_type, quiz_id, course_id,
                        points=1, additional_params={}):
        """
        Creates a quiz question

        POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions
        https://canvas.instructure.com/doc/api/quiz_questions.html#method.quizzes/quiz_questions.create
        """
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("title", title, str)
        self.check_type("text", text, str)
        self.check_type("q_type", q_type, str)
        self.check_type("points", points, int)
        self.check_type("additional_params", additional_params, dict)

        full_endpoint = f"courses/{course_id}/quizzes/{quiz_id}/questions"

        questions_endpoint = urljoin(self.domain, full_endpoint)

        question_types = ["calculated_question", "essay_question",
                            "file_upload_question",
                            "fill_in_multiple_blanks_question",
                            "matching_question", "multiple_answers_question",
                            "multiple_choice_question",
                            "multiple_dropdowns_question",
                            "numerical_question", "short_answer_question",
                            "text_only_question", 'true_false_question']

        assert q_type in question_types, \
            f"pcaw: create_question: Not a valid question type: {q_type}"

        params = {
            "question[question_name]": title,
            "question[question_text]": text,
            "question[question_type]": q_type,
            "question[points_possible]": points
        }

        print(f"pcaw: create_question: Creating '{q_type}' question at: {questions_endpoint}")

        full_params = {**params, **additional_params}
        print("Final parameters:")
        pprint(full_params, width=50)

        self.genericPOST(questions_endpoint, full_params)


class Pcaw(Quizzes):
    def __init__(self, domain, access_token, show_responses=False):
        self.headers = {'Authorization': f"Bearer {access_token}"}
        self.access_token = access_token
        self.show_responses = show_responses
        parsed_domain = urllib.parse.ParseResult("https", domain, "/api/v1/",
                                                 params='', query='',
                                                 fragment='')
        self.domain = parsed_domain.geturl()

        print(f"pcaw: Initalized; Domain: {self.domain}")

    def json_pretty_print(self, json_string, check=False):
        """
        Nicely prints a JSON object

        Enable "check" to only check if the string
        is valid JSON, without printing
        """
        try:
            json_loads = json.loads(json_string)
            json_dumps = json.dumps(json_loads, indent=2)
            if not check:
                print(json_dumps)
            else:
                return True
        except JSONDecodeError:
            if self.show_responses:
                print("pcaw: ERROR: The response is not valid JSON. Possibly HTML?"
                      f"\nRaw Response:\n{json_string}")
            else:
                print("pcaw: ERROR: The response is not valid JSON. Possibly HTML?"
                      "\nEnable show_responses to see raw response")

    def request(self, url, request_type, data=None):
        """
        Generic HTTP request function that passes your desired parameters to a
        desired URL, using self.headers

        Returns HTTP response object

        Enable show_responses to print the HTTP responses from this method
        """
        self.check_type("url", url, str)
        if data:
            self.check_type("data", data, dict)
        self.check_type("request_type", request_type, str)
        request_type = request_type.upper()

        # Currently supported types
        request_types = ["GET", "POST", "PUT", "DELETE"]

        assert request_type in request_types, \
            f"pcaw: request: Not a valid request type: {request_type}"

        if request_type in ["POST", "PUT"]:
            assert data, f"pcaw: request: 'data' not specified for {request_type} request"

        print(f"pcaw: request: {request_type} Requesting URL: {url}")

        args = {"url": url, "headers": self.headers}
        if request_type == "POST":
            r = requests.post(data=data, **args)
        elif request_type == "PUT":
            r = requests.put(data=data, **args)
        elif request_type == "GET":
            r = requests.get(**args)
        elif request_type == "DELETE":
            r = requests.delete(**args)

        if "errors" in r.text:
            print("pcaw: request: Canvas API returned error(s):")
            self.json_pretty_print(r.text)

        if self.show_responses:
            print("pcaw: request: Response:")
            self.json_pretty_print(r.text)

        if r.status_code != requests.codes.ok:
            print("pcaw: request: ERROR: Bad Response:")
            self.json_pretty_print(r.text)

        assert r.status_code == requests.codes.ok, "pcaw: Request not OK, " \
            f"response code: {r.status_code}"

        print(f"pcaw: request: Success; {request_type} request to '{url}' sucessful")
        return r

    def genericPOST(self, endpoint, data):
        """
        Generic POST request function that passes your desired
        parameters (data) to a desired endpoint, using self.headers

        Enable show_responses to print the HTTP responses from this method

        Returns JSON object of response
        """
        self.check_type("data", data, dict)
        self.check_type("endpoint", endpoint, str)

        url = urljoin(self.domain, endpoint)

        r = self.request(url, request_type="POST", data=data)

        return r.json()

    def paginate(self, endpoint, params=None, per_page=100):
        """
        Returns all items/JSON objects (in an array) from an endpoint
        / handles pagination
        """
        endpoint = urljoin(self.domain, endpoint)
        print(f"pcaw: paginate: Paginating: {endpoint}")

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
            print(f"pcaw: paginate: ERROR: The response is not valid JSON. {e}")
            raise
        except Exception as e:
            print(f"pcaw: paginate: ERROR: There was an unexpected error: {e}")
            raise

        item_set = []

        print('pcaw: paginate: Going through first page...')
        for item in raw:
            # print(item)
            item_set.append(item)

        print('pcaw: paginate: Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers=self.headers)
            raw = r.json()
            for item in raw:
                # print(item)
                item_set.append(item)

        if not item_set:
            print(f"pcaw: paginate: There were no objects found at this endpoint: {r.url}")

        print(f"pcaw: paginate: Success; Sucessfully paginated endpoint: {r.url}")
        return item_set

    def check_type(self, variable_name, object_to_check, intended_type):
        """
        Function that checks to make sure objects are the right type
        """
        assert isinstance(object_to_check, intended_type), \
            f"'{variable_name}' must be type '{intended_type.__name__}', " \
            f"instead it's: '{type(object_to_check).__name__}'"

