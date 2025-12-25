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
            if text.startswith("Q:"):
                if question and answer:
                    cards.append((question, answer))
                question = text[2:].strip()
                answer = None
            elif text.startswith("A (English):") and question:
                answer = text[len("A (English):"):].strip()
        if question and answer:
            cards.append((question, answer))
        return cards
    except Exception as e:
        st.error(f"Error loading document: {e}")
        return []

# ====================== INITIALIZE ======================
if "cards" not in st.session_state:
    st.session_state.cards = load_flashcards("Law Preparation.docx")
    if st.session_state.cards:
        st.session_state.deck = list(range(len(st.session_state.cards)))
        random.shuffle(st.session_state.deck)
    else:
        st.session_state.deck = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "quiz_current" not in st.session_state:
    st.session_state.quiz_current = 0

# ====================== FLASHCARDS ======================
def show_flashcards():
    st.title("📚 LLB Flashcards (English Only)")
    
    if not st.session_state.cards:
        st.warning("No flashcards found. Ensure your document uses Q: and A (English): lines.")
        st.code("Example:\nQ: What is law?\nA (English): Law is a system of rules...")
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
        st.button("Next Card", on_click=lambda: (
            st.session_state.update(
                current_index=(st.session_state.current_index + 1) % len(st.session_state.deck),
                show_answer=False
            )
        ))

    # Navigation
    st.markdown("---")
    st.write(f"Card {st.session_state.current_index + 1} of {len(st.session_state.deck)}")
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        st.button("⏮️ First", on_click=lambda: st.session_state.update(current_index=0, show_answer=False))
    with nav2:
        st.button("⏪ Prev", on_click=lambda: st.session_state.update(
            current_index=(st.session_state.current_index - 1) % len(st.session_state.deck),
            show_answer=False
        ))
    with nav3:
        st.button("⏩ Next", on_click=lambda: st.session_state.update(
            current_index=(st.session_state.current_index + 1) % len(st.session_state.deck),
            show_answer=False
        ))

# ====================== QUIZ ======================
def start_quiz(num_questions):
    if len(st.session_state.cards) < 4:
        st.error("Need at least 4 flashcards for a quiz.")
        return
    selected = random.sample(st.session_state.cards, min(num_questions, len(st.session_state.cards)))
    quiz_q = []
    for q, a in selected:
        # Generate 3 wrong answers
        wrong = random.sample([c[1] for c in st.session_state.cards if c[1] != a], k=min(3, len(st.session_state.cards)-1))
        options = [a] + wrong
        random.shuffle(options)
        quiz_q.append((q, a, options))
    st.session_state.quiz_questions = quiz_q
    st.session_state.user_answers = {}
    st.session_state.quiz_current = 0
    st.session_state.quiz_started = True

def show_quiz():
    st.title("📝 LLB Quiz (English Only)")
    
    if not st.session_state.cards:
        st.warning("No flashcards loaded. Go to Flashcards tab first.")
        return

    if not st.session_state.quiz_started:
        st.write("Test your knowledge!")
        num = st.slider("Number of questions", 3, min(10, len(st.session_state.cards)), 5)
        if st.button("🚀 Start Quiz"):
            start_quiz(num)
    else:
        total = len(st.session_state.quiz_questions)
        current = st.session_state.quiz_current
        if current >= total:
            # Show results
            correct = 0
            for i, (q, correct_ans, opts) in enumerate(st.session_state.quiz_questions):
                user_ans = st.session_state.user_answers.get(i)
                if user_ans == correct_ans:
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
                st.session_state.quiz_started = False
                st.rerun()
        else:
            q, correct_ans, options = st.session_state.quiz_questions[current]
            st.subheader(f"Question {current + 1} of {total}")
            st.write(f"**{q}**")
            choice = st.radio("Choose your answer:", options, index=None)
            if st.button("✅ Submit"):
                st.session_state.user_answers[current] = choice
                if choice == correct_ans:
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect")
                    st.info(f"**Correct answer:** {correct_ans}")
                st.button("➡️ Next", on_click=lambda: st.session_state.update(quiz_current=current + 1))

# ====================== MAIN ======================
st.set_page_config(page_title="LLB Flashcards & Quiz", page_icon="📚", layout="centered")

tab1, tab2 = st.tabs(["🎴 Flashcards", "📝 Quiz"])

with tab1:
    show_flashcards()

with tab2:
    show_quiz()