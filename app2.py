import streamlit as st
import json

# Load IELTS exam data directly
with open('backend/listening2.json', 'r') as file:
    ielts_data = json.load(file)

# Function to calculate band score
def calculate_band_score(correct_count, total_questions):
    if total_questions == 0:
        return 0
    percentage = (correct_count / total_questions) * 100
    if percentage >= 85:
        return 9
    elif percentage >= 75:
        return 8
    elif percentage >= 65:
        return 7
    elif percentage >= 55:
        return 6
    elif percentage >= 45:
        return 5
    elif percentage >= 35:
        return 4
    elif percentage >= 25:
        return 3
    elif percentage >= 15:
        return 2
    elif percentage >= 5:
        return 1
    else:
        return 0

# Function to get band description
def get_band_description(band_score):
    band_descriptions = {
        9: {"skill_level": "Expert user", "description": "Fully operational command of the language: fluent, precise, and well-understood."},
        8: {"skill_level": "Very good user", "description": "Efficient in language use with minor inaccuracies or misunderstandings in unfamiliar contexts."},
        7: {"skill_level": "Good user", "description": "Handles language well with occasional lapses; understands detailed arguments effectively."},
        6: {"skill_level": "Competent user", "description": "Effective in familiar situations but prone to errors in complex language."},
        5: {"skill_level": "Modest user", "description": "Basic command of language, often requiring repetition or clarification for accuracy."},
        4: {"skill_level": "Limited user", "description": "Copes with simple situations but struggles with understanding or expressing detailed meaning."},
        3: {"skill_level": "Extremely limited user", "description": "Communicates basic needs but suffers frequent communication breakdowns."},
        2: {"skill_level": "Intermittent user", "description": "Uses isolated words and phrases to meet immediate needs; struggles with understanding."},
        1: {"skill_level": "Non-user", "description": "Unable to use language beyond isolated words."},
        0: {"skill_level": "Did not attempt test", "description": "No attempt to answer the test questions."}
    }
    return band_descriptions.get(band_score, {"skill_level": "Unknown", "description": "No description available."})

# Streamlit Application
st.title("IELTS Listening Exam")

st.subheader("Exam")
user_answers = {}

# Display exam parts
for part_name, part_data in ielts_data[0].items():
    if part_name.startswith("Part"):
        st.write(f"### {part_name}")

        # Handle audio playback
        if part_data.get('audio'):
            st.audio(part_data['audio'], format="audio/mp3")
        else:
            st.error("Audio file not available for this part.")

        for question in part_data['questions']:
            qid = question['question']
            st.write(f"**{qid}**")

            if question.get('type') == 'diagram':
                # Display diagram
                if question.get('image'):
                    st.image(question['image'], caption="Label the diagram")
                else:
                    st.error("Diagram not available for this question.")

                # Collect labels
                diagram_labels = {}
                for label in question['labels']:
                    label_id = label['id']
                    diagram_labels[label_id] = st.selectbox(
                        f"Label for {label_id}:",
                        question['options'],
                        key=f"diagram_{part_name}_{qid}_{label_id}"
                    )
                user_answers[qid] = diagram_labels

            elif 'options' in question:
                # Multiple Choice Questions
                user_answers[qid] = st.radio(
                    "Select your answer:",
                    question['options'],
                    key=f"mcq_{part_name}_{qid}"
                )

            elif 'matches' in question:
                # Match the Following Questions
                dropdown_answers = {}
                for idx, item in enumerate(question['matches']):
                    # Dynamically determine match type
                    left = item.get('apartment', item.get('person', item.get('strategy', item.get('feature'))))
                    options = item.get('facility', item.get('work', item.get('benefit', item.get('description'))))

                    dropdown_answers[left] = st.selectbox(
                        f"Match for {left}:",
                        [options],
                        key=f"match_{part_name}_{qid}_{idx}"
                    )
                user_answers[qid] = dropdown_answers

            else:
                # Fill in the Blanks Questions
                user_answers[qid] = st.text_input(
                    "Your answer:", key=f"fill_{part_name}_{qid}"
                )

# Submit and evaluate answers
if st.button("Submit Exam"):
    results = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    for part_name, part_data in ielts_data[0].items():
        if part_name.startswith("Part"):
            for question in part_data['questions']:
                qid = question['question']
                if question.get('type') == 'diagram':
                    correct_labels = {label['id']: label['correct_label'] for label in question['labels']}
                    user_labels = user_answers.get(qid, {})
                    if user_labels == correct_labels:
                        correct_count += 1
                    elif not user_labels:
                        unanswered_count += 1
                    else:
                        incorrect_count += 1
                elif 'matches' in question:
                    correct_matches = {item.get('apartment', item.get('person')): item.get('facility', item.get('work')) for item in question['matches']}
                    user_matches = user_answers.get(qid, {})
                    if user_matches == correct_matches:
                        correct_count += 1
                    elif not user_matches:
                        unanswered_count += 1
                    else:
                        incorrect_count += 1
                else:
                    correct_answer = question['answer']
                    user_answer = user_answers.get(qid, None)
                    if user_answer is None or user_answer.strip() == "":
                        unanswered_count += 1
                    elif user_answer.strip().lower() == correct_answer.strip().lower():
                        correct_count += 1
                    else:
                        incorrect_count += 1

    total_questions = correct_count + incorrect_count + unanswered_count
    band_score = calculate_band_score(correct_count, total_questions)
    band_description = get_band_description(band_score)

    st.subheader("Results")
    st.write(f"**Correct:** {correct_count}")
    st.write(f"**Incorrect:** {incorrect_count}")
    st.write(f"**Unanswered:** {unanswered_count}")
    st.write(f"**Band Score:** {band_score}")
    st.write(f"**Skill Level:** {band_description['skill_level']}")
    st.write(f"**Description:** {band_description['description']}")
