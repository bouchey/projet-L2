import sqlite3
from ollama import chat
from pydantic import BaseModel
from typing import List
import json
import re

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



def generate_and_store_qcm():
    # Appeler l'IA pour générer les questions
    response = chat(
        messages=[
            {
                'role': 'user',
                'content': 'Génère un quiz de quinze questions simples.',
            }
        ],
        model='llama3.2:1b',
    )

    # Afficher la réponse brute pour le débogage
    print("Réponse brute de l'API :", response)

    try:
        # Extraire le texte brut des questions
        raw_content = response['message']['content']

        # Diviser le contenu en blocs de questions/réponses
        question_blocks = re.split(r'\n\d+\.\s', raw_content.strip())
        question_blocks = [block.strip() for block in question_blocks if block.strip()]  # Supprimer les blocs vides

        for block in question_blocks:
            try:
                # Ignorer les blocs introductifs
                if "multiple-choice quiz questions" in block.lower():
                    continue

                # Extraire la question
                question_match = re.search(r'^(.*?)(?:\n|$)', block)  # Première ligne = question
                if not question_match:
                    raise ValueError("Impossible d'extraire la question.")
                question_text = question_match.group(1).strip()

                # Extraire les options (A), B), C), D))
                options = re.findall(r'^[A-D]\)\s(.*?)(?:\n|$)', block, re.MULTILINE)
                if len(options) < 4:
                    raise ValueError("Options insuffisantes détectées.")

                # Extraire la réponse correcte
                answer_match = re.search(r'(?:Answer:\s)?[A-D]\)\s(.*?)(?:\n|$)', block)
                if not answer_match:
                    raise ValueError("Réponse correcte manquante.")
                correct_answer = answer_match.group(1).strip()

                # Créer une question
                question = Question(
                    question_text=question_text,
                    options=options,
                    correct_answer=correct_answer
                )

                # Insérer dans la base de données
                insert_question(question)
            except ValueError as e:
                print(f"Erreur dans le traitement d'un bloc : {block}\nRaison : {e}")
        
        print("Toutes les questions ont été insérées avec succès.")
    except Exception as e:
        print("Erreur globale lors du traitement des données générées par l'IA :", e)



def fetch_questions():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM questions")
    rows = c.fetchall()
    
    for row in rows:
        print(row)
    
    conn.close()

# Fonction pour supprimer les questions avec un ID inférieur ou égal à 62
def delete_questions_with_id_leq_62():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()

    # Supprimer les questions avec un ID inférieur ou égal à 62
    c.execute('''
    DELETE FROM questions
    WHERE id <= 176
    ''')

    conn.commit()
    conn.close()

# Appeler pour vérifier
fetch_questions()


# Appeler la fonction principale
create_db()
generate_and_store_qcm()
#delete_questions_with_id_leq_62()