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
#       - move mixin classes to separate files?
#       - rename Pcaw class to "ApiHandler", and have
#           module classes/mixins inherit from that
#       - implement way to get associated question banks for questions in a quiz,
#           to be able to get the bank's "updated_at" parameter


class Quizzes:
    def __init__(self):
        pass

    def get_quiz(self, course_id, quiz_id, params={}):
        """
        Gets a single quiz, returns JSON Quiz object

        GET /api/v1/courses/:course_id/quizzes/:id
        https://canvas.instructure.com/doc/api/quizzes.html#method.quizzes/quizzes_api.show
        """
        f_name = "get_quiz"
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("params", params, dict)

        full_endpoint = f"courses/{course_id}/quizzes/{quiz_id}"

        quiz_url = urljoin(self.domain, full_endpoint)
        self.log(f_name, f"Getting quiz object from: {quiz_url}")
        response = self.get(quiz_url, params)

        html_url = response["html_url"]
        self.log(f_name, f"Success; Quiz object URL: {html_url}")

        return response

    def create_quiz(self, course_id, title, description, quiz_type,
                    params={}):
        """
        Creates a quiz, returns JSON Quiz object

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

        response = self.post(quizzes_endpoint, full_params)

        html_url = response["html_url"]

        self.log(f_name, f"New quiz URL: {html_url}")

        return response

    def get_questions(self, course_id, quiz_id,
                      quiz_submission_id=None, quiz_submission_attempt=None,
                      params={}):
        """
        Returns array of JSON QuizQuestion objects in a quiz or a submission

        GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions
        https://canvas.instructure.com/doc/api/quiz_questions.html#method.quizzes/quiz_questions.index
        """
        f_name = "get_questions"
        self.check_type("course_id", course_id, int)
        self.check_type("quiz_id", quiz_id, int)
        self.check_type("params", params, dict)
        if quiz_submission_id:
            self.check_type("quiz_submission_id", quiz_submission_id, int)
            params["quiz_submission_id"] = quiz_submission_id
        if quiz_submission_attempt:
            self.check_type("quiz_submission_attmpt", quiz_submission_attempt, int)
            params["quiz_submission_attempt"] = quiz_submission_attempt

        full_endpoint = f"courses/{course_id}/quizzes/{quiz_id}/questions"

        final_url = urljoin(self.domain, full_endpoint)

        self.log(f_name, f"Getting quiz questions from: {final_url}")
        if params:
            pretty_params = pprint.pformat(params, width=50)
            self.log(f_name, f"Additional parameters: \n{pretty_params}")

        response = self.paginate(final_url, params=params)
        self.log(f_name, f"Success; Successfully obtained questions from quiz: {quiz_id}")

        return response

    def create_question(self, course_id, quiz_id, title,
                        text, q_type, points=1, params={}):
        """
        Creates a quiz question, returns JSON QuizQuestion object

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

        r = self.post(questions_endpoint, full_params)
        return r


class Pcaw(Quizzes):
    def __init__(self, domain, access_token,
                 show_responses=False, log_level="WARNING"):
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
        self.log_level = self.log_level.upper()
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

    def format_json(self, json_object):
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

    def post(self, endpoint, params):
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

    def paginate(self, endpoint, per_page=100, params={}):
        """
        Returns all items/JSON objects (in an array) from an endpoint
        / handles pagination
        """
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

    def check_type(self, variable_name, object_to_check, intended_type):
        """
        Function that checks to make sure objects are the right type
        """
        assert isinstance(object_to_check, intended_type), \
            f"'{variable_name}' must be type '{intended_type.__name__}', " \
            f"instead it's: '{type(object_to_check).__name__}'"

    def get(self, endpoint, params={}):
        """
        Generic GET function to get/return a single JSON object from an endpoint
        """
        f_name = "get"
        self.check_type("endpoint", endpoint, str)
        self.check_type("params", params, dict)

        full_url = urljoin(self.domain, endpoint)

        self.log(f_name, f"Getting JSON object from: {full_url}")
        if params:
            pretty_params = pprint.pformat(params, width=50)
            self.log(f_name, f"Additional parameters: \n{pretty_params}")

        response = self.request(full_url, "GET", params=params)
        response = response.json()

        self.log(f_name, f"Success; JSON object URL: {full_url}")

        return response
