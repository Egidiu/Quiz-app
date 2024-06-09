import streamlit as st
import pandas as pd
import random

# Funcție pentru încărcarea datelor din Excel
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Funcție pentru configurarea paginii de setări a quizului
def config_page():
    st.title("Configurare Quiz")
    
    # Verificăm dacă există deja un fișier încărcat anterior
    if "uploaded_file" in st.session_state:
        uploaded_file = st.session_state.uploaded_file
        st.session_state.data = load_data(uploaded_file)
        st.session_state.categories = st.session_state.data["Categorie"].unique()

    # Încărcare fișier Excel
    uploaded_file = st.file_uploader("Încarcă fișierul Excel cu întrebări", type=["xlsx"])
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.data = load_data(uploaded_file)
        st.session_state.categories = st.session_state.data["Categorie"].unique()

    # Selectare categorie
    if "categories" in st.session_state:
        category = st.selectbox("Alege categoria", st.session_state.categories, 
                                index=st.session_state.categories.tolist().index(st.session_state.selected_category) if "selected_category" in st.session_state else 0)
        st.session_state.selected_category = category

    # Setare număr de întrebări
    num_questions = st.number_input("Setează numărul de întrebări", min_value=1, 
                                    value=st.session_state.num_questions if "num_questions" in st.session_state else 3)
    st.session_state.num_questions = num_questions

    if st.button("Salvează și Continuă"):
        st.session_state.page = "welcome"

# Funcție pentru pagina de bun venit
def welcome_page():
    st.title("Bun venit la Quiz!")
    st.write("Apasă pe butonul de mai jos pentru a începe testul.")
    if st.button("Începe testul"):
        selected_category = st.session_state.selected_category
        questions_in_category = st.session_state.data[st.session_state.data["Categorie"] == selected_category]
        st.session_state.questions = questions_in_category.sample(st.session_state.num_questions).to_dict('records')
        st.session_state.page = 1

# Funcție pentru pagina de întrebări
def question_page(page):
    question_data = st.session_state.questions[page - 1]
    options = [question_data[f"Varianta {chr(97+i)}"] for i in range(6) if pd.notna(question_data[f"Varianta {chr(97+i)}"])]
    
    st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)  # Linie groasă neagră
    
    st.markdown("<h3 style='text-align: center;'>{}</h3>".format(question_data['Enunt']), unsafe_allow_html=True)  # Text întrebare mai mare și centrat

    st.write("")  # Spațiu între întrebare și opțiuni

    user_answer = st.radio("Alegeți un răspuns:", options, key=page)

    # Verificăm apăsarea butonului pentru următoarea întrebare
    if st.button("Următoarea întrebare"):
        st.session_state.responses[page] = user_answer
        if page < st.session_state.num_questions:
            st.session_state.page = page + 1
        else:
            st.session_state.page = "results"

# Funcție pentru pagina de rezultate
def results_page():
    st.title("Rezultate")

    score = 0
    for i, question_data in enumerate(st.session_state.questions):
        correct_option_index = [question_data[f"Stare Varianta {chr(97+j)}"] for j in range(6)].index(1)
        correct_answer = question_data[f"Varianta {chr(97+correct_option_index)}"]
        user_answer = st.session_state.responses.get(i + 1)
        if user_answer == correct_answer:
            score += 1

        st.write(f"Întrebarea {i + 1}: {question_data['Enunt']}")
        
        for j in range(6):
            option = question_data[f"Varianta {chr(97+j)}"]
            if pd.notna(option):
                if option == correct_answer:
                    st.markdown(f'<div style="background-color: lightgreen; padding: 10px; border-radius: 5px;">{option} (corect)</div>', unsafe_allow_html=True)
                elif option == user_answer:
                    st.markdown(f'<div style="background-color: lightcoral; padding: 10px; border-radius: 5px;">{option} (greșit)</div>', unsafe_allow_html=True)
                else:
                    st.write(option)
        
        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)  # Linie sub fiecare întrebare

    st.write("")  # Spațiu după secțiunea de întrebări și răspunsuri

    st.markdown("Scorul tău este: {}/{}".format(score, st.session_state.num_questions))

    st.write("")

    st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)  # Linie groasă neagră

    col1, col2 = st.columns(2)

    if col1.button("Reconfigurare Quiz"):
        st.session_state.page = "config"
    if col2.button("Restart Quiz"):
        # Alegem alte întrebări random și resetăm răspunsurile
        selected_category = st.session_state.selected_category
        questions_in_category = st.session_state.data[st.session_state.data["Categorie"] == selected_category]
        st.session_state.questions = questions_in_category.sample(st.session_state.num_questions).to_dict('records')
        st.session_state.responses = {}
        st.session_state.page = 1

# Controlăm navigarea între pagini
if "page" not in st.session_state:
    st.session_state.page = "config"
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "data" not in st.session_state:
    st.session_state.data = None
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 3

# Redirecționăm la pagina curentă
if st.session_state.page == "config":
    config_page()
elif st.session_state.page == "welcome":
    welcome_page()
elif isinstance(st.session_state.page, int):
    question_page(st.session_state.page)
elif st.session_state.page == "results":
    results_page()
