import os
import csv
from config import QUESTIONS_FILE_PATH, QUESTIONS_FILE_HEADER, OPTION_MAP, OPTION_MAP_REVERSE

class Question:
    def __init__(self, id: int, question: str, optA: str, optB: str, optC: str, optD: str, correctOpt: str):
        self.id = id
        self.question = question
        self.optA = optA
        self.optB = optB
        self.optC = optC
        self.optD = optD
        self.correctOpt = correctOpt
        self.answers = [optA, optB, optC, optD]
        self.correct_answer_index = OPTION_MAP[correctOpt]
        self.correct_answer = self.answers[self.correct_answer_index]

    def info(self) -> str:
        return f"{self.id},{self.question},{self.optA},{self.optB},{self.optC},{self.optD},{self.correctOpt}"
    
    def csv_line(self) -> list[str]:
        return [self.id, self.question, self.optA, self.optB, self.optC, self.optD, self.correctOpt]
    
    def reformat(self, data: tuple[str, str, str]):
        self.question = data[0]
        self.optA = data[1][0]
        self.optB = data[1][1]
        self.optC = data[1][2]
        self.optD = data[1][3]
        self.answers = data[1]
        self.correct_answer_index = data[2]
        self.correctOpt = OPTION_MAP_REVERSE[int(self.correct_answer_index)]
        self.correct_answer = self.answers[int(self.correct_answer_index)]

def load_questions() -> list[Question]:
    make_file_if_doesnt_exist()
    with open(QUESTIONS_FILE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        questions: list[Question] = []

        for row in reader:
            questions.append(Question(
                int(row[QUESTIONS_FILE_HEADER[0]]),
                row[QUESTIONS_FILE_HEADER[1]],
                row[QUESTIONS_FILE_HEADER[2]],
                row[QUESTIONS_FILE_HEADER[3]],
                row[QUESTIONS_FILE_HEADER[4]],
                row[QUESTIONS_FILE_HEADER[5]],
                row[QUESTIONS_FILE_HEADER[6]].strip()
            ))
        
        return questions
    
def save_questions(questions: list[Question]):
    with open(QUESTIONS_FILE_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUESTIONS_FILE_HEADER)

        for question in questions:
            writer.writerow(question.csv_line())

def make_file_if_doesnt_exist():
    if not os.path.exists(QUESTIONS_FILE_PATH):
        with open(QUESTIONS_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(QUESTIONS_FILE_HEADER)
