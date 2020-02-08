import requests
from json.decoder import JSONDecodeError
import json
import pprint
from requests.compat import urljoin
import urllib.parse

# Python Canvas API Wrapper (pcaw)
# Prototype, by Bailey M.
# TODO: - verify __init__ 'domain' variable URL formatting
#       - in progress - implement endpoints as classes, with mixins for them
#           in the "Pcaw" class, e.g. 'Pcaw(Quizzes):'
#       - change genericPOST method name to just 'post'
#       - move mixin classes to separate files?
#       - refactor paginate method to use request method
#       - implement get_questions Quizzes method


class Quizzes:
    def __init__(self):
        pass

    def get_quiz(self, course_id, quiz_id, params={}):
        """
        Gets a single quiz, returns JSON quiz object

        GET /api/v1/courses/:course_id/quizzes/:id
        https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.show
        """
        f_name = "get_quiz"
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("params", params, dict)

        full_endpoint = f"courses/{course_id}/quizzes/{quiz_id}"

        quiz_url = urljoin(self.domain, full_endpoint)

        self.log(f_name, f"Generating quiz object from: {quiz_url}")
        if params:
            pretty_params = pprint.pformat(params, width=50)
            self.log(f_name, f"Additional parameters: \n{pretty_params}")

        response = self.request(quiz_url, "GET", params=params)
        response = response.json()

        html_url = response["html_url"]

        self.log(f_name, f"Success; Quiz object URL: {html_url}")

        return response

    def create_quiz(self, course_id, title, description, quiz_type,
                    params={}):
        """
        Creates a quiz, returns JSON quiz object

        POST /api/v1/courses/:course_id/quizzes
        https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.create
        """
        f_name = "create_quiz"
        self.check_type("course_id", course_id, int)
        self.check_type("title", title, str)
        self.check_type("description", description, str)
        self.check_type("quiz_type", quiz_type, str)
        self.check_type("params", params, dict)

        quiz_types = ["practice_quiz", "assignment", "graded_survey", "survey"]

        assert quiz_type in quiz_types, \
            f"pcaw: Not a valid quiz type: {quiz_type}"

        full_endpoint = f"courses/{course_id}/quizzes/"

        quizzes_endpoint = urljoin(self.domain, full_endpoint)

        http_params = {
            "quiz[title]": title,
            "quiz[description]": description,
            "quiz[quiz_type]": quiz_type
        }

        self.log(f_name, f"Creating '{quiz_type}' quiz at: {quizzes_endpoint}")

        full_params = {**http_params, **params}
        pretty_params = pprint.pformat(full_params, width=50)
        self.log(f_name, f"Final parameters: \n{pretty_params}")

        response = self.genericPOST(quizzes_endpoint, full_params)

        html_url = response["html_url"]

        self.log(f_name, f"pcaw: create_quiz: New quiz URL: {html_url}")

        return response

    def create_question(self, course_id, quiz_id, title,
                        text, q_type, points=1, params={}):
        """
        Creates a quiz question

        POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions
        https://canvas.instructure.com/doc/api/quiz_questions.html#method.quizzes/quiz_questions.create
        """
        f_name = "create_question"
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("title", title, str)
        self.check_type("text", text, str)
        self.check_type("q_type", q_type, str)
        self.check_type("points", points, int)
        self.check_type("params", params, dict)

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
            f"FATAL: Not a valid question type: {q_type}"

        http_params = {
            "question[question_name]": title,
            "question[question_text]": text,
            "question[question_type]": q_type,
            "question[points_possible]": points
        }

        self.log(f_name, f"Creating '{q_type}' question at: {questions_endpoint}")

        full_params = {**http_params, **params}
        pretty_params = pprint.pformat(full_params, width=50)
        self.log(f_name, f"Final parameters: \n{pretty_params}")

        self.genericPOST(questions_endpoint, full_params)


class Pcaw(Quizzes):
    def __init__(self, domain, access_token,
                 show_responses=False, log_level="ERROR"):
        """
        Enable show_responses to show HTTP responses from requests method
        """
        self.headers = {'Authorization': f"Bearer {access_token}"}
        self.access_token = access_token
        self.show_responses = show_responses
        parsed_domain = urllib.parse.ParseResult("https", domain, "/api/v1/",
                                                 params='', query='',
                                                 fragment='')
        self.domain = parsed_domain.geturl()

        self.log_level = log_level
        self.log("init", f"Initalized; Domain: {self.domain}")

    def log(self, f_name, string, log_level="INFO"):
        """
        Method that handles logging
        """
        function_name = f_name
        log_level = log_level.upper()
        log_levels = ["INFO", "WARNING", "ERROR"]

        assert self.log_level in log_levels, \
            f"FATAL: Not a valid log_level {log_level}"

        print_log = False

        if log_level in ["INFO", "WARNING"]:
            if self.log_level == log_level:
                print_log = True

        if log_level == "ERROR":
            print_log = True

        if print_log:
            print(f"pcaw: {log_level}: {function_name}: {string}")

    def format_json(self, json_string):
        """
        Takes an ugly JSON string (from a response)
        and returns a nicely formatted JSON string

        Enable "check" to only check if the string
        is valid JSON, without printing
        """
        f_name = "format_json"  # Used for logging

        try:
            json_loads = json.loads(json_string)
            json_dumps = json.dumps(json_loads, indent=2)
            return(json_dumps)

        except JSONDecodeError:
            self.log(f_name, "The response is not valid JSON. Possibly HTML?"
                     f"\nRaw Response:\n{json_string}", "ERROR")
            raise

    def request(self, url, request_type, params={}):
        """
        Generic HTTP request function that passes your desired parameters to a
        desired URL, using self.headers

        Returns HTTP response object
        """
        f_name = "request"
        self.check_type("url", url, str)
        self.check_type("params", params, dict)
        self.check_type("request_type", request_type, str)
        request_type = request_type.upper()

        # Currently supported types
        request_types = ["GET", "POST", "PUT", "DELETE"]

        assert request_type in request_types, \
            f"FATAL: Not a valid request type: {request_type}"

        if request_type in ["POST", "PUT"]:
            assert params, f"FATAL: 'params' not specified for {request_type} request"

        self.log(f_name, f"{request_type} Requesting URL: {url}")

        args = {"url": url, "headers": self.headers}
        if request_type == "POST":
            r = requests.post(data=params, **args)
        elif request_type == "PUT":
            r = requests.put(data=params, **args)
        elif request_type == "GET":
            r = requests.get(**args)
        elif request_type == "DELETE":
            r = requests.delete(**args)

        response = self.format_json(r.text)

        if "errors" in r.text:
            self.log(f_name, f"Canvas API returned error(s): \n{response}",
                     "ERROR")

        assert r.status_code == requests.codes.ok, "FATAL: Request not OK, " \
            f"response status code: {r.status_code}" \
            f"\nResponse: \n{response}"

        self.log(f_name, f"Success; {request_type} request to '{url}' sucessful")
        if self.show_responses:
            self.log(f_name, f"Response: \n{response}")

        return r

    def genericPOST(self, endpoint, params):
        """
        Generic POST request function that passes your desired
        parameters to a desired endpoint, using self.headers

        Returns JSON object of response
        """
        self.check_type("params", params, dict)
        self.check_type("endpoint", endpoint, str)

        url = urljoin(self.domain, endpoint)

        r = self.request(url, request_type="POST", params=params)

        return r.json()

    def paginate(self, endpoint, params={}, per_page=100):
        """
        Returns all items/JSON objects (in an array) from an endpoint
        / handles pagination
        """
        f_name = "paginate"
        self.log(f_name, f"Paginating: {endpoint}")

        endpoint = urljoin(self.domain, endpoint)

        per_page_url = endpoint + f"?per_page={per_page}"
        r = requests.get(per_page_url, headers=self.headers, params=params)

        self.log(f_name, f"Full URL with HTTP params: {r.url}")

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
            self.log(f_name, f"The response is not valid JSON. \n{e}", "ERROR")
            raise
        except Exception as e:
            self.log(f_name, f"There was an unexpected error: \n{e}", "ERROR")
            raise

        item_set = []

        self.log(f_name, 'Going through first page...')
        for item in raw:
            item_set.append(item)

        self.log(f_name, 'Going through the next pages...')
        while r.links['current']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers=self.headers)
            raw = r.json()
            for item in raw:
                item_set.append(item)

        if not item_set:
            self.log(f_name, f"There were no objects found at this endpoint: {r.url}", "WARNING")

        self.log(f_name, f"Success; Sucessfully paginated endpoint: {r.url}")
        return item_set

    def check_type(self, variable_name, object_to_check, intended_type):
        """
        Function that checks to make sure objects are the right type
        """
        assert isinstance(object_to_check, intended_type), \
            f"'{variable_name}' must be type '{intended_type.__name__}', " \
            f"instead it's: '{type(object_to_check).__name__}'"
