import os
import csv
import ast
from config import SCORES_FILE_PATH, SCORES_FILE_HEADER

class Score:
    def __init__(self, date: str, score: int, question_ids: list[int]):
        self.date = date
        self.score = score
        self.question_ids = question_ids

    def info(self) -> str:
        return f"{self.date},{self.score},{self.question_ids}"
    
    def csv_line(self) -> list[str]:
        return [self.date, self.score, self.question_ids]

def load_scores() -> list[Score]:
    make_file_if_doesnt_exist()
    with open(SCORES_FILE_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        scores: list[Score] = []

        for row in reader:
            scores.append(Score(
                row[SCORES_FILE_HEADER[0]],
                row[SCORES_FILE_HEADER[1]],
                ast.literal_eval(row[SCORES_FILE_HEADER[2]].strip()),
            ))
        
        return scores
    
def save_scores(scores: list[Score]):
    with open(SCORES_FILE_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(SCORES_FILE_HEADER)

        for score in scores:
            writer.writerow(score.csv_line())

def make_file_if_doesnt_exist():
    if not os.path.exists(SCORES_FILE_PATH):
        with open(SCORES_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(SCORES_FILE_HEADER)
