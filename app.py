import random
from datetime import datetime
import tkinter as tk
from tkinter import StringVar
import tkinter.messagebox as messagebox
from question import Question, save_questions
from score import Score, save_scores
from settings import is_first_run, has_run_now
from config import QUESTION_COUNT, ANSWER_COUNT

class App(tk.Frame):
    def __init__(self, master, all_questions: list[Question], all_scores: list[Score]):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.all_questions = all_questions
        self.all_scores = all_scores
        self.is_first_run = is_first_run()
        self.is_running_game = False
        self.sort_mode = "score"
        self.sort_reverse = False
        self.launch()

    def create_tutorial_ui(self):
        self.tutorial_window = tk.Toplevel(self.master)
        self.tutorial_window.title(f"Welcome")
        self.tutorial_window.minsize(width=500, height=450)
        self.tutorial_window.maxsize(width=500, height=450)
        self.tutorial_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.tutorial_window.grab_set()

        tutorial_text = """
Welcome to my multiple choice quiz

From the home menu there are 4 options you can choose from:

The first is start quiz, this takes you to a 10 question quiz, at the end there is a results view

In the results view, you can take another quiz, go to the leaderboard or go home

In the quiz, the keyboard keys 1-4 and A-D can be used to select answers, the enter button can be used as the the submit button

From home, you can go to the leaderboard which shows all the previous results, you can click on the headers to change the sort order

The 3rd option from home is change questions, here you get a list of all the questions and answers and can click a button to edit them

The final option reopens this help guide.
To exit this tutorial click launch below!

Have fun!!!
        """

        tutorial_text_content = tk.Label(self.tutorial_window, text=tutorial_text, wraplength=460)
        tutorial_text_content.pack()

        ready_button = tk.Button(self.tutorial_window, text="Launch", font=("Arial", 12), command=self.close_tutorial)
        ready_button.pack()

    def create_home_ui(self):
        self.master.minsize(width=300, height=170)
        self.master.maxsize(width=600, height=400)
        self.master.title("Home")

        start_quiz_button = tk.Button(self.master, text="Start Quiz", command=self.start_quiz)
        start_quiz_button.pack(pady=(10,5))

        leaderboard_button = tk.Button(self.master, text="Leaderboard", command=self.show_leaderboard)
        leaderboard_button.pack(pady=5)

        change_questions_button = tk.Button(self.master, text="Change Questions", command=self.show_question_list)
        change_questions_button.pack(pady=(5))

        tutorial_button = tk.Button(self.master, text="Tutorial", command=self.show_tutorial)
        tutorial_button.pack(pady=(5,10))

    def create_quiz_ui(self, previous_score: Score = None):
        self.master.minsize(width=340, height=240)
        self.master.maxsize(width=600, height=400)
        self.master.title("Quiz" if not previous_score else "Retrying a Quiz")

        question_text = StringVar(value=self.question)
        question_label = tk.Label(self.master, textvariable=question_text, wraplength=300, font=("Arial", 12))
        question_label.pack(pady=(10,5))

        self.quiz_selected_answer = StringVar(value="x")
        self.quiz_selected_answer.trace_add("write", self.on_answer_selected)
        self.quiz_answer_radio_buttons = []

        for option in self.answers:
            rb = tk.Radiobutton(self.master, text=option, variable=self.quiz_selected_answer, value=option)
            rb.pack(pady=2)
            self.quiz_answer_radio_buttons.append(rb)

        for i in range(len(self.answers)):
            self.master.bind(str(i+1), lambda e, idx=i: self.quiz_selected_answer.set(self.answers[idx]))

        for i, key in enumerate(["a", "b", "c", "d"]):
            self.master.bind(key, lambda e, idx=i: self.quiz_selected_answer.set(self.answers[idx]))

        self.quiz_action_button_text = StringVar(value="Submit")

        self.quiz_submit_button = tk.Button(self.master, textvariable=self.quiz_action_button_text, command=lambda:self.quiz_button_action(previous_score))
        self.quiz_submit_button.pack(pady=(8,4))
        self.quiz_submit_button.config(state=tk.DISABLED)

        if previous_score:
            back_button = tk.Button(self.master, text="Back to Leaderboard", command=self.back_to_leaderboard)
            back_button.pack(pady=(4,8))
        else:
            exit_button = tk.Button(self.master, text="Exit", command=self.cancel_game)
            exit_button.pack(pady=(4,8))

        self.master.bind('<Return>', lambda e: self.quiz_button_action(previous_score))

    def create_results_ui(self, previous_score: Score = None):
        self.master.minsize(width=340, height=140)
        self.master.maxsize(width=600, height=400)
        self.master.title("Results" if not previous_score else "Retry Results")

        if not previous_score:
            results_summary_label = tk.Label(self.master, text=f"You got {self.correct_count} correct and {self.incorrect_count} incorrect", font=("Arial", 12))
            results_summary_label.pack(pady=8)

            new_quiz_button = tk.Button(self.master, text="New Quiz", command=self.start_quiz)
            new_quiz_button.pack(pady=6)

            row_frame = tk.Frame(self.master)
            row_frame.pack(pady=(10,2), anchor="center")

            home_button = tk.Button(row_frame, text="Home", command=self.return_home)
            home_button.grid(row=0, column=0, padx=4)

            home_button = tk.Button(row_frame, text="Leaderboard", command=self.back_to_leaderboard)
            home_button.grid(row=0, column=1, padx=4)
        else:
            results_summary_label = tk.Label(self.master, text=f"You got {self.correct_count} correct and {self.incorrect_count} incorrect\nYour previous result was {previous_score.score}")
            results_summary_label.pack(pady=8)
            
            back_button = tk.Button(self.master, text="Back to Leaderboard", command=self.back_to_leaderboard)
            back_button.pack(pady=(4,8))
        
    def create_leaderboard_ui(self):
        self.master.minsize(width=400, height=300)
        self.master.maxsize(width=400, height=self.master.winfo_screenheight()-50)
        self.master.title("Leaderboard")

        container = tk.Frame(self.master)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.all_scores != []:
            home_button = tk.Button(scrollable_frame, text="Home", command=self.return_home)
            home_button.grid(row=0, column=0, columnspan=3, pady=10, padx=10)

            score_arrow = "↑" if self.sort_mode == "score" and not self.sort_reverse else "↓" if self.sort_mode == "score" else ""
            header_score = tk.Button(scrollable_frame, text=f"Score {score_arrow}", font=("Arial", 12, "underline"), command=self.toggle_sort_by_score,)
            header_score.grid(row=1, column=0, padx=10)

            date_arrow = "↑" if self.sort_mode == "date" and not self.sort_reverse else "↓" if self.sort_mode == "date" else ""
            header_date = tk.Button(scrollable_frame, text=f"Date {date_arrow}", font=("Arial", 12, "underline"), command=self.toggle_sort_by_date)
            header_date.grid(row=1, column=1, padx=10)

            def get_sort_key(mode):
                if mode == "score":
                    return lambda s: (-int(s.score), datetime.strptime(str(s.date), "%Y-%m-%d %H:%M:%S.%f"))
                elif mode == "date":
                    return lambda s: (datetime.strptime(str(s.date), "%Y-%m-%d %H:%M:%S.%f"), -int(s.score))
                else:
                    raise ValueError("Invalid sort mode")
                
            sort_key = get_sort_key(self.sort_mode)
            sort_order = self.sort_reverse

            def convert_date(date: str) -> str:
                try:
                    dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                except:
                    dt = date
                custom_format = dt.strftime("%d/%m/%Y %H:%M")
                return custom_format
                
            for i, score in enumerate(sorted(self.all_scores, key=sort_key, reverse=sort_order), start=2):
                ldb_score = tk.Label(scrollable_frame, text=score.score)
                ldb_score.grid(row=i, column=0, pady=2)

                ldb_date = tk.Label(scrollable_frame, text=convert_date(score.date))
                ldb_date.grid(row=i, column=1, pady=2)

                ldb_retry = tk.Button(scrollable_frame, text="Retry Questions", command=lambda s=score: self.retry_quiz(s))
                ldb_retry.grid(row=i, column=2, pady=4, padx=(10,))
        else:
            title = tk.Label(scrollable_frame, text="No scores recorded")
            title.grid(row=0, column=0, columnspan=3, pady=5, padx=80)

            home_button = tk.Button(scrollable_frame, text="Home", command=self.return_home)
            home_button.grid(row=1, column=0, columnspan=3, pady=5, padx=80)

    def create_question_list_ui(self):
        self.master.minsize(width=560, height=400)
        self.master.maxsize(width=800, height=self.master.winfo_screenheight()-50)
        self.master.title("Questions")

        container = tk.Frame(self.master)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        scrollbar.pack(side="right", fill="y")

        top_row_frame = tk.Frame(scrollable_frame)
        top_row_frame.pack(pady=(10,2), anchor="center")

        home_button = tk.Button(top_row_frame, text="Home", command=self.return_home)
        home_button.grid(row=0, column=0, padx=4)

        create_new_button = tk.Button(top_row_frame, text="New Question", command=self.create_edit_question_ui)
        create_new_button.grid(row=0, column=1, padx=4)

        for index, q in enumerate(self.all_questions):
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(pady=15, anchor="center")

            question_label = tk.Label(row_frame, text=f"{index+1}: {q.question}", font=("Arial", 12, "bold"), anchor="center")
            question_label.grid(row=0, column=0, padx=2)

            edit_button = tk.Button(row_frame, text="Edit", command=lambda q=q: self.create_edit_question_ui(q))
            edit_button.grid(row=0, column=1, padx=2)

            for a in q.answers:
                answer_label = tk.Label(scrollable_frame, text=a, anchor="center")
                answer_label.pack(pady=1)
                answer_label.config(fg="green" if q.correct_answer == a else "red")

        canvas.config(yscrollcommand=scrollbar.set)

    def create_edit_question_ui(self, question: Question = None):
        is_new_question = not question
        save_title = "Add" if not question else "Save"
        question = question if question else Question(len(self.all_questions)+1, "Question...", "Option 1...", "Option 2...", "Option 3...", "Option 4...", "B")

        new_x = self.master.winfo_x() + self.master.winfo_width() + 10
        new_y = self.master.winfo_y()

        self.edit_q_window = tk.Toplevel(self.master)
        self.edit_q_window.title(f"Editing Question {question.id}")
        self.edit_q_window.minsize(width=450, height=360)
        self.edit_q_window.maxsize(width=500, height=400)
        self.edit_q_window.geometry(f"450x400+{new_x}+{new_y}") 
        self.edit_q_window.protocol("WM_DELETE_WINDOW", self.confirm_cancel_edits)
        self.edit_q_window.grab_set()

        edit_label = tk.Label(self.edit_q_window, text="Add the question name, 4 answer options and specify the correct answer with the radio button.", wraplength=420)
        edit_label.pack(pady=10)

        self.question_text_var = StringVar(value=question.question)
        self.question_text_var.trace_add("write", self.on_question_edit)
        self.question_entry = tk.Entry(self.edit_q_window, textvariable=self.question_text_var, width=50, validate="key", validatecommand=(self.master.register(self.validate_question_length), "%P"))
        self.question_entry.pack(pady=20)
        self.question_entry.bind("<Return>", lambda e: self.edit_q_window.focus())

        self.correct_answer_index_var = tk.StringVar(value=question.correct_answer_index)
        self.correct_answer_index_var.trace_add("write", self.on_question_edit)

        answer_entries = []
        self.answer_text_vars = []

        for i, _ in enumerate(["A", "B", "C", "D"]):
            edit_question_frame = tk.Frame(self.edit_q_window)
            edit_question_frame.pack()

            correct_answer_index_radiobutton = tk.Radiobutton(edit_question_frame, variable=self.correct_answer_index_var, value=i)
            correct_answer_index_radiobutton.pack(side="left")

            answer_var = StringVar(value=question.answers[i])
            answer_var.trace_add("write", self.on_question_edit)
            self.answer_text_vars.append(answer_var)

            answer_entry = tk.Entry(edit_question_frame, textvariable=answer_var, width=40, validate="key", validatecommand=(self.master.register(self.validate_answer_length), "%P"))
            answer_entry.pack(side="right", padx=(0,10))
            answer_entries.append(answer_entry)
            answer_entry.bind("<Return>", lambda e: self.edit_q_window.focus())
        
        action_button_row_frame = tk.Frame(self.edit_q_window)
        action_button_row_frame.pack(pady=(10,4), anchor="center")

        self.save_button = tk.Button(action_button_row_frame, text=save_title, command=lambda: self.save_question(is_new_question, question))
        self.save_button.grid(row=0, column=0, padx=4)
        self.save_button.config(fg="blue", state=tk.DISABLED)

        if not is_new_question:
            delete_button = tk.Button(action_button_row_frame, text="Delete", command=lambda: self.delete_question(question))
            delete_button.config(fg="red")
            delete_button.grid(row=0, column=1, padx=4)

        cancel_button = tk.Button(self.edit_q_window, text="Cancel", command=self.confirm_cancel_edits)
        cancel_button.pack(pady=(4,12))

        self.original_question_data = self.get_current_question_data()

    def on_app_close(self):
        if not self.is_first_run:
            save_questions(self.all_questions)
            save_scores(self.all_scores)
        self.master.quit()

    def launch(self):
        if self.is_first_run:
            self.create_tutorial_ui()
        self.create_home_ui()

    def start_quiz(self, previous_score: Score = None):
        if previous_score is not None:
            self.questions = [q for q in self.all_questions if q.id in previous_score.question_ids]

            if not len(self.questions) == 10:
                self.questions = random.sample(self.all_questions, QUESTION_COUNT)
        else:
            self.questions = random.sample(self.all_questions, QUESTION_COUNT)

        self.q_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.is_running_game = True
        self.update_qa()
        self.remove_all_widgets()
        self.create_quiz_ui(previous_score)

    def show_leaderboard(self):
        self.remove_all_widgets()
        self.create_leaderboard_ui()

    def show_question_list(self):
        self.remove_all_widgets()
        self.create_question_list_ui()

    def show_tutorial(self):
        self.create_tutorial_ui()

    def close_tutorial(self):
        self.tutorial_window.destroy()
        self.master.update_idletasks()
        if self.is_first_run:
            has_run_now()
            self.is_first_run = is_first_run()

    def remove_all_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def return_home(self):
        self.remove_all_widgets()
        self.create_home_ui()

    def update_qa(self):
        qa = self.questions[self.q_index]
        self.question = qa.question
        self.answers = random.sample(qa.answers, ANSWER_COUNT)
        self.correct_answer = qa.correct_answer

    def on_answer_selected(self, *args):
        self.quiz_submit_button.config(state=tk.NORMAL)

    def unbind_quiz_keys(self):
        for i in range(1, 5):
            self.master.unbind(str(i))
        for key in ["a", "b", "c", "d"]:
            self.master.unbind(key)
        self.master.unbind('<Return>')

    def quiz_button_action(self, previous_score: Score = None):
        if not self.is_running_game or self.quiz_submit_button.cget("state") == "disabled":
            return
        
        title = self.quiz_action_button_text.get()

        if title == "Submit":
            self.check_answer()
        elif title == "Next Question":
            self.next_question(previous_score)
        else:
            self.end_game(previous_score)

    def check_answer(self):
        selected_option = self.quiz_selected_answer.get()

        if selected_option == self.correct_answer:
            self.correct_count += 1
            self.highlight_answer(selected_option, "green")
        else:
            self.incorrect_count += 1
            self.highlight_answer(selected_option, "red")

        self.quiz_action_button_text.set("Next Question" if self.q_index < 9 else "Results")

    def next_question(self, previous_score: Score = None):
        self.q_index += 1
        self.update_qa()
        self.remove_all_widgets()
        self.create_quiz_ui(previous_score)
        self.quiz_action_button_text.set("Submit")

    def end_game(self, previous_score: Score = None):
        self.unbind_quiz_keys()
        self.save_score()
        self.is_running_game = False
        self.remove_all_widgets()
        self.create_results_ui(previous_score)

    def save_score(self):
        ids = [int(q.id) for q in self.questions]
        score = self.correct_count
        date = datetime.now()
        new_score = Score(date, score, ids)
        self.all_scores.append(new_score)
    
    def cancel_game(self):
        self.unbind_quiz_keys()
        self.is_running_game = False
        self.remove_all_widgets()
        self.create_home_ui()

    def back_to_leaderboard(self):
        self.is_running_game = False
        self.show_leaderboard()

    def highlight_answer(self, selected_option: str, color: str):
        for rb in self.quiz_answer_radio_buttons:
            if rb.cget("value") == selected_option:
                rb.config(fg=color)

    def toggle_sort_by_score(self):
        if self.sort_mode == "score":
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_mode = "score"
            self.sort_reverse = False
        self.show_leaderboard()

    def toggle_sort_by_date(self):
        if self.sort_mode == "date":
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_mode = "date"
            self.sort_reverse = True
        self.show_leaderboard()
        
    def retry_quiz(self, previous_score: Score):
        self.start_quiz(previous_score)

    def get_current_question_data(self):
        return (
            self.question_entry.get(),
            [var.get() for var in self.answer_text_vars],
            self.correct_answer_index_var.get()
        )

    def confirm_cancel_edits(self):
        current_data = self.get_current_question_data()
        if current_data != self.original_question_data:
            result = messagebox.askquestion("Cancel Edits", "Are you sure you want to discard changes?", icon="warning")
            if result == "yes":
                self.edit_q_window.destroy()
        else:
            self.edit_q_window.destroy()

    def on_question_edit(self, *args):
        current_data = self.get_current_question_data()
        if current_data != self.original_question_data:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def save_question(self, is_new: bool, question: Question):
        current_data = self.get_current_question_data()
        question.reformat(current_data)

        if is_new:
            self.all_questions.append(question)

        self.close_edit_window()

        button_action_type = "added" if is_new else "updated"
        messagebox.showinfo(button_action_type.capitalize(), f"Question {button_action_type} successfully!")

    def delete_question(self, question: Question):
        if question in self.all_questions:
            self.all_questions.remove(question)
            self.close_edit_window()
            messagebox.showinfo("Deleted", "Question deleted successfully!")
        else:
            messagebox.showerror("Error", "Question not found!")

    def close_edit_window(self):
        self.show_question_list()
        self.edit_q_window.destroy()
        self.master.update_idletasks()

    def validate_question_length(self, new_value: str):
        return len(new_value) <= 80
    
    def validate_answer_length(self, new_value: str):
        return len(new_value) <= 40
    