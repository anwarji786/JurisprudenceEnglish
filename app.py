import streamlit as st
from docx import Document
import random

# ====================== LOAD FLASHCARDS ======================
def load_flashcards(doc_path):
    try:
        doc = Document(doc_path)
        cards = []
        question = None
        answer = None
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if text.startswith("QUESTION:"):
                if question and answer:
                    cards.append((question, answer))
                question = text[len("QUESTION:"):].strip()
                answer = None
            elif text.startswith("ANSWER:") and question:
                answer = text[len("ANSWER:"):].strip()
        if question and answer:
            cards.append((question, answer))
        return cards
    except Exception as e:
        st.error(f"❌ Error loading document: {e}")
        return []

# ====================== INITIALIZE ======================
if "cards" not in st.session_state:
    st.session_state.cards = load_flashcards("Law Preparation.docx")
    if st.session_state.cards:
        st.session_state.deck = list(range(len(st.session_state.cards)))
        random.shuffle(st.session_state.deck)

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

# ====================== FLASHCARDS ======================
def show_flashcards():
    st.title("📚 LLB Flashcards")
    
    if not st.session_state.cards:
        st.warning("No flashcards found.")
        st.info("Expected format in your .docx:\n\nQUESTION: ...\nANSWER: ...")
        return

    idx = st.session_state.deck[st.session_state.current_index]
    question, answer = st.session_state.cards[idx]
    
    st.subheader(f"Q: {question}")
    
    if st.session_state.show_answer:
        st.markdown(f"<div style='padding:15px; background:#f0f8ff; border-left:4px solid #4CAF50; margin:10px 0;'><strong>A:</strong><br>{answer}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Show Answer", on_click=lambda: st.session_state.update(show_answer=True))
    with col2:
        st.button("Next Card", on_click=lambda: st.session_state.update(
            current_index=(st.session_state.current_index + 1) % len(st.session_state.deck),
            show_answer=False
        ))
    
    st.write(f"Card {st.session_state.current_index + 1} of {len(st.session_state.deck)}")

# ====================== QUIZ ======================
def start_quiz(num_questions):
    if len(st.session_state.cards) < 4:
        st.error("Need at least 4 flashcards for a quiz.")
        return
    selected = random.sample(st.session_state.cards, min(num_questions, len(st.session_state.cards)))
    quiz_q = []
    for q, a in selected:
        # Collect 3 wrong answers
        wrong_pool = [c[1] for c in st.session_state.cards if c[1] != a]
        wrong = random.sample(wrong_pool, k=min(3, len(wrong_pool)))
        options = [a] + wrong
        random.shuffle(options)
        quiz_q.append((q, a, options))
    st.session_state.quiz_questions = quiz_q
    st.session_state.user_answers = {}
    st.session_state.quiz_index = 0
    st.session_state.quiz_active = True

def show_quiz():
    st.title("📝 LLB Quiz ")
    
    if not st.session_state.cards:
        st.warning("No flashcards loaded. Go to Flashcards tab first.")
        return

    if not st.session_state.quiz_active:
        st.write("Test your knowledge!")
        num = st.slider("Number of questions", 3, min(10, len(st.session_state.cards)), 5)
        if st.button("🚀 Start Quiz"):
            start_quiz(num)
    else:
        total = len(st.session_state.quiz_questions)
        idx = st.session_state.quiz_index
        if idx >= total:
            # Show results
            correct = 0
            for i, (q, correct_ans, opts) in enumerate(st.session_state.quiz_questions):
                if st.session_state.user_answers.get(i) == correct_ans:
                    correct += 1
            score = (correct / total) * 100
            st.balloons()
            st.success("🎉 Quiz Completed!")
            st.metric("Score", f"{score:.1f}%")
            if score >= 80:
                st.success("🏆 Excellent!")
            elif score >= 60:
                st.info("👍 Good job!")
            else:
                st.warning("📚 Keep practicing!")
            if st.button("🔁 Retry Quiz"):
                st.session_state.quiz_active = False
                st.rerun()
        else:
            q, correct_ans, options = st.session_state.quiz_questions[idx]
            st.subheader(f"Question {idx + 1} of {total}")
            st.write(f"**{q}**")
            choice = st.radio("Choose your answer:", options, index=None)
            if st.button("✅ Submit"):
                st.session_state.user_answers[idx] = choice
                if choice == correct_ans:
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect")
                    st.info(f"**Correct answer:** {correct_ans}")
                if idx + 1 < total:
                    st.button("➡️ Next", on_click=lambda: st.session_state.update(quiz_index=idx + 1))
                else:
                    st.button("🏁 Finish", on_click=lambda: st.session_state.update(quiz_index=idx + 1))

# ====================== MAIN ======================
st.set_page_config(page_title="LLB Flashcards & Quiz", page_icon="📚")

tab1, tab2 = st.tabs(["🎴 Flashcards", "📝 Quiz"])

with tab1:
    show_flashcards()

with tab2:

    show_quiz()
