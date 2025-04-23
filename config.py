import os
import platform

OS_NAME = platform.system()
IS_WINDOWS = OS_NAME == "Windows"

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

QUESTION_COUNT = 10
ANSWER_COUNT = 4
OPTION_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
OPTION_MAP_REVERSE = {0: "A", 1: "B", 2: "C", 3: "D"}
QUESTIONS_FILE_PATH = os.path.join(BASE_DIRECTORY, "questions.csv")
QUESTIONS_FILE_HEADER = ["ID", "Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
SCORES_FILE_PATH = os.path.join(BASE_DIRECTORY, "scores.csv")
SCORES_FILE_HEADER = ["Date", "Score", "Question IDs"]
SETTINGS_FILE_PATH = os.path.join(BASE_DIRECTORY, "settings.txt")