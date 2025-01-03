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
            question_text = question['question']
            st.write(f"**{question_text}**")

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
                        key=f"diagram_{part_name}_{question_text}_{label_id}"
                    )
                user_answers[question_text] = diagram_labels

            elif 'options' in question:
                # Multiple Choice Questions
                user_answers[question_text] = st.radio(
                    "Select your answer:",
                    question['options'],
                    key=f"mcq_{part_name}_{question_text}"
                )

            elif 'matches' in question:
                # Collect all unique options from matches
                unique_options = []
                for match in question['matches']:
                    options = [
                        match.get('facility'),
                        match.get('work'),
                        match.get('benefit'),
                        match.get('description'),
                    ]
                    unique_options.extend(filter(None, options))  # Add only non-None options

                # Dropdown for each matching pair
                match_answers = {}
                for match in question['matches']:
                    left_item = (
                        match.get('apartment')
                        or match.get('person')
                        or match.get('strategy')
                        or match.get('feature')
                    )

                    if left_item:
                        match_answers[left_item] = st.selectbox(
                            f"Match for {left_item}:",
                            unique_options,
                            key=f"match_{part_name}_{question_text}_{left_item}",
                        )

                user_answers[question_text] = match_answers

            else:
                # Fill in the Blanks Questions
                user_answers[question_text] = st.text_input(
                    "Your answer:", key=f"fill_{part_name}_{question_text}"
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
                question_text = question['question']
                if question.get('type') == 'diagram':
                    correct_labels = {label['id']: label['correct_label'] for label in question['labels']}
                    user_labels = user_answers.get(question_text, {})
                    if user_labels == correct_labels:
                        correct_count += 1
                        result_status = "Correct"
                    elif not user_labels:
                        unanswered_count += 1
                        result_status = "Unanswered"
                    else:
                        incorrect_count += 1
                        result_status = "Incorrect"
                    
                    # Add detailed feedback for diagrams
                    results.append({
                        "question": question_text,
                        "your_answer": user_labels,
                        "correct_answer": correct_labels,
                        "status": result_status
                    })
                elif 'matches' in question:
                    # Initialize counts for this question
                    total_matches = 0
                    correct_matches = 0

                    # Evaluate all types of matches
                    match_results = []
                    for match in question['matches']:
                        left_item = (
                            match.get('apartment')
                            or match.get('person')
                            or match.get('strategy')
                            or match.get('feature')
                        )
                        correct_answer = (
                            match.get('facility')
                            or match.get('work')
                            or match.get('benefit')
                            or match.get('description')
                        )

                        user_answer = user_answers.get(question_text, {}).get(left_item)

                        if user_answer is None:
                            result_status = "Unanswered"
                        elif user_answer.strip().lower() == correct_answer.strip().lower():
                            correct_matches += 1
                            result_status = "Correct"
                        else:
                            result_status = "Incorrect"

                        # Store result for each individual match
                        match_results.append({
                            "pair": f"{left_item} -> {correct_answer}",
                            "your_answer": user_answer,
                            "status": result_status
                        })
                        total_matches += 1

                    # Count correct, incorrect, and unanswered matches for this question
                    correct_count += correct_matches
                    unanswered_count += total_matches - correct_matches - len([
                        match for match in match_results if match["status"] == "Incorrect"
                    ])
                    incorrect_count += len([
                        match for match in match_results if match["status"] == "Incorrect"
                    ])

                    # Add detailed feedback for matches
                    results.append({
                        "question": question_text,
                        "details": match_results
                    })
                else:
                    correct_answer = question['answer']
                    user_answer = user_answers.get(question_text, None)
                    if user_answer is None or user_answer.strip() == "":
                        unanswered_count += 1
                        result_status = "Unanswered"
                    elif user_answer.strip().lower() == correct_answer.strip().lower():
                        correct_count += 1
                        result_status = "Correct"
                    else:
                        incorrect_count += 1
                        result_status = "Incorrect"
                    
                    # Add detailed feedback for other questions
                    results.append({
                        "question": question_text,
                        "your_answer": user_answer,
                        "correct_answer": correct_answer,
                        "status": result_status
                    })

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

    st.subheader("Detailed Feedback")
    for result in results:
        st.write(f"**Question:** {result['question']}")
        if "details" in result:
            for match_result in result['details']:
                st.write(f"Pair: {match_result['pair']}")
                st.write(f"Your Answer: {match_result['your_answer']} ({match_result['status']})")
            st.write("---")
        else:
            st.write(f"Your Answer: {result['your_answer']} ({result['status']})")
            st.write(f"Correct Answer: {result['correct_answer']}")
            st.write("---")
