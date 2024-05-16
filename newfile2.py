import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

class LoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Login Page")
        self.master.geometry("300x200")
        self.master.config(bg="#f2f2f2")

        self.label_username = tk.Label(master, text="Username:", bg="#f2f2f2")
        self.label_username.pack(pady=5)
        self.entry_username = tk.Entry(master)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(master, text="Password:", bg="#f2f2f2")
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack(pady=5)

        self.btn_login = tk.Button(master, text="Login", command=self.login)
        self.btn_login.pack(pady=5)

        # Connect to SQLite database
        self.conn = sqlite3.connect('user_accounts.db')
        self.c = self.conn.cursor()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Check if username and password exist in the database
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.c.fetchone()

        if user:
            messagebox.showinfo("Login Successful", "Welcome to the Quiz App!")
            self.master.destroy()  # Close the login window
            # Open the quiz window
            quiz_window = tk.Tk()
            quiz_window.title("Quiz App")
            quiz_window.geometry("400x300")
            quiz_app = QuizApp(quiz_window)
            quiz_window.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.current_question = None
        self.questions = self.get_questions_from_database()  # Fetch questions from the database
        self.score = 0
        self.questions_answered = 0
        self.previous_questions = set()

        self.master.config(bg="#f2f2f2")

        self.question_label = tk.Label(master, text="", font=("Helvetica", 14), bg="#f2f2f2")
        self.question_label.pack(pady=10)

        self.option_buttons = []
        for i in range(4):
            option_button = tk.Button(master, text="", font=("Helvetica", 12), command=lambda idx=i: self.submit_answer(idx), bg="#b3e0ff")
            option_button.pack(pady=5, padx=20, ipadx=10, ipady=5, fill=tk.X)
            self.option_buttons.append(option_button)

        self.display_question()

    def get_questions_from_database(self):
        conn = sqlite3.connect('quiz_questions.db')
        c = conn.cursor()
        c.execute('SELECT * FROM questions')
        questions = c.fetchall()
        conn.close()
        return questions

    def display_question(self):
        if self.questions_answered < 10:
            remaining_questions = [q for q in self.questions if q not in self.previous_questions]
            if remaining_questions:
                self.current_question = random.choice(remaining_questions)
                self.question_label.config(text=self.current_question[1])
                options = random.sample(self.current_question[2:6], 4)
                for i, option in enumerate(options):
                    self.option_buttons[i].config(text=option)
                self.previous_questions.add(self.current_question)
            else:
                self.show_score()
        else:
            self.show_score()

    def submit_answer(self, selected_index):
        if self.questions_answered < 10:
            answer = self.option_buttons[selected_index].cget("text")
            correct_answer = self.current_question[6]
            if answer == correct_answer:
                self.score += 1
                messagebox.showinfo("Result", "Correct!")
            else:
                messagebox.showinfo("Result", f"Incorrect! The correct answer is {correct_answer}.")
            self.questions_answered += 1
            self.display_question()
        else:
            self.show_score()

    def show_score(self):
        score_window = tk.Toplevel(self.master)
        score_window.title("Quiz Score")
        score_window.config(bg="#f2f2f2")

        score_label = tk.Label(score_window, text=f"Your score: {self.score}/10", font=("Helvetica", 14), bg="#f2f2f2")
        score_label.pack(pady=10)

        restart_button = tk.Button(score_window, text="Take Quiz Again", font=("Helvetica", 12), command=self.restart_quiz, bg="#b3e0ff")
        restart_button.pack(pady=5, ipadx=10,ipady=5)

    def restart_quiz(self):
        self.score = 0
        self.questions_answered = 0
        self.previous_questions = set()
        self.display_question()

# Create SQLite database for user accounts
def create_user_database():
    conn = sqlite3.connect('user_accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    sample_users = [
        ("user1", "password1"),
        ("user2", "password2"),
        ("user3", "password3"),
        # Add more user accounts here...
    ]

    c.executemany('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', sample_users)
    conn.commit()
    conn.close()

# Create SQLite database for quiz questions
def create_question_database():
    conn = sqlite3.connect('quiz_questions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY,
                    question TEXT,
                    option1 TEXT,
                    option2 TEXT,
                    option3 TEXT,
                    option4 TEXT,
                    correct_answer TEXT
                )''')

    # Sample questions
    sample_questions = [
        ("What is the capital of France?", "Paris", "Berlin", "Madrid", "Rome", "Paris"),
        ("Who wrote 'Romeo and Juliet'?", "William Shakespeare", "Jane Austen", "Charles Dickens", "Mark Twain", "William Shakespeare"),
        # Add more questions here...
    ]

    c.executemany('INSERT OR IGNORE INTO questions (question, option1, option2, option3, option4, correct_answer) VALUES (?, ?, ?, ?, ?, ?)', sample_questions)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Create user accounts and quiz questions databases
    create_user_database()
    create_question_database()

    # Create Tkinter window and run the login page
    root = tk.Tk()
    login_page = LoginPage(root)
    root.mainloop()