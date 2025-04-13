import locale
import tkinter as tk
from app import App
from question import load_questions
from score import load_scores

if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, 'en_GB')
    all_questions = load_questions()
    all_scores = load_scores()
    root = tk.Tk()
    app = App(root, all_questions, all_scores) 
    app.mainloop()