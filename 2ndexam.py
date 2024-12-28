import streamlit as st
import json

# Load JSON Data
with open('2ndjson.json', 'r') as file:
        data = json.load(file)
    
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

# Streamlit App
st.title("IELTS Listening Exam")

# Audio Player
st.audio(data[0]["audio"], format="audio/mp3")

# Instruction for the audio
st.write("**Instruction:** The audio contains all the parts covered in this exam. Please listen carefully.")

# Instruction for Part 1
# st.subheader("Part 1")
# st.write("**Instruction:** Complete the notes below. Write NO MORE THAN ONE WORD OR A NUMBER for each answer.")

# Collect answers from the user
user_answers = {}

# Render questions dynamically
for part_key, part_content in data[0].items():
    if part_key.startswith("Part"):
        st.header(part_key)

        # Add specific instructions for each part
        if part_key == "Part 1":
            st.write("**Instruction:** Complete the notes below. Write NO MORE THAN ONE WORD OR A NUMBER for each answer.")
        elif part_key == "Part 2":
            st.write("**Instruction:** Choose the correct letter, A, B, or C.")
        elif part_key == "Part 3":
            st.write("**Instruction:** Choose the correct letter, A, B, or C. For questions that ask for two answers, choose TWO letters, A-E.")
        elif part_key == "Part 4":
            st.write("**Instruction:** Complete the flow chart below. Write NO MORE THAN TWO WORDS for each answer.")

        # Render questions for each part
        for q in part_content["questions"]:
            if "options" in q:
                if isinstance(q["answer"], list):
                    user_answers[q["question"]] = st.multiselect(q["question"], q["options"])
                else:
                    user_answers[q["question"]] = st.radio(q["question"], q["options"])
            elif "type" in q and q["type"] == "diagram":
                st.image(q["image"], caption="Label the diagram")
                for label in q["labels"]:
                    user_answers[label["id"]] = st.text_input(f"Label for {label['id']}")
            else:
                user_answers[q["question"]] = st.text_input(q["question"])

# Submit Button
if st.button("Submit"):
    correct_count = 0
    total_questions = 0
    unanswered_count = 0  # To count unanswered questions
    feedback = []

    for part_key, part_content in data[0].items():
        if part_key.startswith("Part"):
            for q in part_content["questions"]:
                total_questions += 1
                user_answer = user_answers.get(q.get("question", ""), None)

                # Handle diagram questions
                if q.get("type") == "diagram":
                    for label in q.get("labels", []):
                        label_id = label.get("id", "")
                        correct_label = label.get("correct_label", "").strip().lower()
                        user_label = user_answers.get(label_id, "").strip().lower() if isinstance(user_answers.get(label_id, ""), str) else ""

                        if not user_label:
                            unanswered_count += 1
                            feedback.append((f"Label for {label_id}", "Unanswered", correct_label, "Unanswered"))
                        elif user_label == correct_label:
                            correct_count += 1
                            feedback.append((f"Label for {label_id}", user_label, correct_label, "Correct"))
                        else:
                            feedback.append((f"Label for {label_id}", user_label, correct_label, "Incorrect"))

                # Handle standard questions (multiple-answer MCQs)
                elif isinstance(user_answer, list):
                    correct_answer = q.get("answer", [])
                    correct_answer = [a.strip().lower() for a in correct_answer]
                    user_answer = [a.split(')')[0].strip().lower() for a in user_answer if ')' in a]

                    if not user_answer:
                        unanswered_count += 1
                        feedback.append((q["question"], "Unanswered", correct_answer, "Unanswered"))
                    elif set(user_answer) == set(correct_answer):
                        correct_count += 1
                        feedback.append((q["question"], user_answer, correct_answer, "Correct"))
                    else:
                        feedback.append((q["question"], user_answer, correct_answer, "Incorrect"))

                # Handle single-answer MCQs
                elif isinstance(user_answer, str):
                    correct_answer = q.get("answer", "").strip().lower()
                    user_answer_normalized = user_answer.split(')')[0].strip().lower() if ')' in user_answer else user_answer.strip().lower()

                    if not user_answer.strip():
                        unanswered_count += 1
                        feedback.append((q["question"], "Unanswered", correct_answer, "Unanswered"))
                    elif user_answer_normalized == correct_answer:
                        correct_count += 1
                        feedback.append((q["question"], user_answer, correct_answer, "Correct"))
                    else:
                        feedback.append((q["question"], user_answer, correct_answer, "Incorrect"))

    # Calculate Band Score
    band_score = calculate_band_score(correct_count, total_questions)
    band_info = get_band_description(band_score)

    # Display Results
    st.subheader("Results")
    st.write(f"Correct Answers: {correct_count}")
    st.write(f"Incorrect Answers: {total_questions - correct_count - unanswered_count}")
    st.write(f"Unanswered Questions: {unanswered_count}")
    st.write(f"Band Score: {band_score}")
    st.write(f"Skill Level: {band_info['skill_level']}")
    st.write(f"Description: {band_info['description']}")

    # Question Feedback
    st.subheader("Question Feedback")
    for q, ua, ca, status in feedback:
        st.write(f"Question: {q}")
        st.write(f"Your Answer: {ua} ({status})")
        st.write(f"Correct Answer: {ca}")
        st.write("---")
