import sqlite3
import random
import tkinter as tk
from pydantic import BaseModel
from typing import List


# Modèle pour représenter une question et ses options de réponse
class Question(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str


# Créer ou ouvrir une base de données SQLite
def create_db():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    # Créer une table pour stocker les questions et réponses
    c.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        question_text TEXT,
        option_1 TEXT,
        option_2 TEXT,
        option_3 TEXT,
        option_4 TEXT,
        correct_answer TEXT
    )
    ''')
    conn.commit()
    conn.close()


# Insérer une question dans la base de données
def insert_question(question: Question):
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    c.execute('''
    INSERT INTO questions (question_text, option_1, option_2, option_3, option_4, correct_answer)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        question.question_text,
        question.options[0],
        question.options[1],
        question.options[2],
        question.options[3],
        question.correct_answer
    ))
    conn.commit()
    conn.close()


# Extraire les questions de la base de données (et limiter à 15 questions aléatoires)
def fetch_questions():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    c.execute("SELECT question_text, option_1, option_2, option_3, option_4, correct_answer FROM questions")
    rows = c.fetchall()

    questions = []
    for row in rows:
        question_text, option_1, option_2, option_3, option_4, correct_answer = row
        questions.append({
            'question_text': question_text,
            'options': [option_1, option_2, option_3, option_4],
            'correct_answer': correct_answer
        })

    conn.close()

    # Sélectionner aléatoirement 15 questions (ou moins si la base de données a moins de 15 questions)
    random.shuffle(questions)  # Mélanger les questions
    return questions[:15]  # Retourner les 15 premières questions après mélange


# Fonction pour afficher une question dans l'interface graphique
def show_question():
    global current_question_index, question_label, options_buttons, result_label, questions, asked_questions

    # Vérifier qu'il y a encore des questions non posées
    if len(asked_questions) >= len(questions):
        # Afficher le score final dans une page séparée
        show_final_score()
        return

    # Sélectionner une question aléatoire parmi celles qui n'ont pas encore été posées
    remaining_questions = [i for i in range(len(questions)) if i not in asked_questions]
    random_question_index = random.choice(remaining_questions)

    # Ajouter la question posée à la liste des questions posées
    asked_questions.append(random_question_index)
    current_question_index = random_question_index  # Mettre à jour l'index de la question actuelle
    question = questions[random_question_index]

    question_label.config(text=f"Q{len(asked_questions)}: {question['question_text']}")

    # Mélanger les options de réponse et garder une trace de l'index correct
    options_with_answer = list(zip(question['options'], [i == question['correct_answer'] for i in question['options']]))
    random.shuffle(options_with_answer)

    # Mise à jour de l'indice correct après le mélange des options
    correct_option = next(opt for opt, is_correct in options_with_answer if is_correct)

    # Mettre à jour les boutons avec les options mélangées
    for i, (option, is_correct) in enumerate(options_with_answer):
        options_buttons[i].config(text=option, command=lambda opt=option, correct_option=correct_option: check_answer(opt, correct_option))

    # Mettre à jour la question pour la comparer à la bonne option après le mélange
    question['options'] = [opt for opt, correct in options_with_answer]
    question['correct_answer'] = correct_option  # La bonne réponse après le mélange

    # Cacher la correction pour cette question avant qu'une réponse ne soit donnée
    result_label.config(text="", fg="black", font=("Arial", 24))


# Vérifier la réponse sélectionnée
def check_answer(selected_option, correct_option):
    global score, result_label

    # Déterminer si la réponse sélectionnée est correcte
    if selected_option == correct_option:
        score += 1
        result_label.config(text="Correct!", fg="green", font=("Arial", 24, "bold"))  # Agrandir la police ici
    else:
        result_label.config(text=f"Wrong! Correct answer: {correct_option}", fg="red", font=("Arial", 24, "bold"))  # Agrandir la police ici

    # Afficher la correction sous la question
    result_label.pack(pady=10)
    
    # Passer à la question suivante après un délai pour que l'utilisateur puisse lire la correction
    root.after(2000, show_question)


# Fonction pour afficher le score final
def show_final_score():
    global score, final_score_label, final_score_frame

    # Cacher la page de quiz
    quiz_frame.pack_forget()

    # Afficher le cadre du score final
    final_score_label.config(text=f"Votre score final est : {score}/{len(questions)}")
    final_score_frame.pack(fill="both", expand=True)


# Fonction pour démarrer le quiz et cacher l'écran d'accueil
def start_quiz():
    global current_question_index, score, question_label, options_buttons, result_label, questions, asked_questions

    questions = fetch_questions()
    if not questions:
        print("No questions found in the database. Please add questions first.")
        return

    # Cacher la page d'accueil
    home_frame.pack_forget()

    # Réinitialiser l'état du quiz
    current_question_index = 0
    score = 0
    asked_questions = []

    # Afficher la fenêtre du quiz
    quiz_frame.pack(fill="both", expand=True)

    show_question()


# Créer l'interface principale
root = tk.Tk()
root.title("Quiz App")

# Définir la taille initiale de la fenêtre
root.geometry("600x400")  # Définir la taille de la fenêtre à 600x400 pixels

# Empêcher la redimension de la fenêtre
root.resizable(False, False)  # Ne pas permettre le redimensionnement

# Définir la couleur du fond de la fenêtre principale
root.config(bg="white")

# Créer un cadre pour simuler les bordures personnalisées de la fenêtre
border_frame = tk.Frame(root, bg="#FFB6C1", bd=10)  # Utiliser la couleur rose clair pour la bordure
border_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Frame pour la page d'accueil
home_frame = tk.Frame(border_frame, bg="white")
home_frame.pack(fill="both", expand=True)

# Centrer et agrandir le titre, en utilisant la même couleur que les questions
title_label = tk.Label(home_frame, text="Venez explorer le monde !", font=("Arial", 32), bg="white", fg="#D5006D")  # Couleur rose foncé
title_label.place(relx=0.5, rely=0.3, anchor="center")

# Centrer le bouton sous le titre avec la couleur rose claire
start_button = tk.Button(home_frame, text="Commencer le quiz", font=("Arial", 18), bg="#FFB6C1", command=start_quiz)  # bg="#FFB6C1" pour couleur rose clair
start_button.place(relx=0.5, rely=0.5, anchor="center")  # Placer le bouton centré sous le titre

# Frame pour le quiz
quiz_frame = tk.Frame(border_frame, bg="white")

# Créer un conteneur central pour les questions et réponses
quiz_content_frame = tk.Frame(quiz_frame, bg="white")

# Centrer la question dans ce conteneur avec une police plus grande et un rose plus foncé pour le texte
question_label = tk.Label(quiz_content_frame, text="", wraplength=400, justify="center", bg="white", fg="#D5006D", font=("Arial", 20))  # Rose foncé "#D5006D"
question_label.pack(pady=20)

# Créer les boutons de réponse et les centrer, avec la couleur de fond rose clair
options_buttons = []
for _ in range(4):
    btn = tk.Button(quiz_content_frame, text="", width=30, height=3, font=("Arial", 14), bg="#FFB6C1")  # bg="#FFB6C1" est la couleur rose clair
    btn.pack(pady=10)
    options_buttons.append(btn)

# Centrer les résultats (la correction sera affichée sous chaque question)
result_label = tk.Label(quiz_content_frame, text="", bg="white", fg="black", font=("Arial", 24))  # Agrandir la police ici
result_label.pack(pady=20)

# Pack le conteneur avec la question et les réponses au centre de l'écran
quiz_content_frame.pack(expand=True)

# Frame pour le score final
final_score_frame = tk.Frame(border_frame, bg="white")
final_score_label = tk.Label(final_score_frame, text="", font=("Arial", 32), bg="white", fg="#D5006D")
final_score_label.pack(expand=True)

# Créer la base de données
create_db()

# Afficher la page d'accueil
root.mainloop()
