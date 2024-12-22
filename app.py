from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'vedicmathgame'

# Level configurations with Vedic math explanations and Sanskrit names
LEVELS = {
    1: {
        "name": "Squares of numbers ending in 5",
        "sanskrit": "Ekādhikena Pūrvena",
        "description": "Square numbers ending in 5 using Ekādhikena Pūrvena: Multiply the first digit by its successor and append 25."
    },
    2: {
        "name": "Vertically and Crosswise multiplication",
        "sanskrit": "Urdhva-Tiryagbhyām",
        "description": "Multiply 2-digit numbers using Urdhva-Tiryagbhyām by crosswise and vertically multiplying digits."
    },
    3: {
        "name": "Division using Nikhilam Sutra",
        "sanskrit": "Nikhilam Navataścarama Daśataḥ",
        "description": "Simplify division using the complement of numbers close to the base."
    },
    4: {
        "name": "Quick subtraction using complements",
        "sanskrit": "Parāvartya Yojayet",
        "description": "Subtract numbers quickly by complementing the subtrahend."
    },
    5: {
        "name": "Patterns in multiplication",
        "sanskrit": "Anurūpyena",
        "description": "Discover multiplication patterns by analyzing proximity to bases like 10 or 100."
    }
}

@app.route('/matching-game', methods=['GET', 'POST'])
def matching_game():
    # Define the list of sutras and their definitions
    sutras_and_defs = [
        {"sutra": "Ekādhikena Pūrvena", "definition": "Multiply the first digit by its successor and append 25."},
        {"sutra": "Urdhva-Tiryagbhyām", "definition": "Multiply 2-digit numbers using crosswise and vertical multiplication."},
        {"sutra": "Nikhilam Navataścarama Daśataḥ", "definition": "Simplify division using the complement of numbers close to the base."},
        {"sutra": "Parāvartya Yojayet", "definition": "Subtract numbers quickly by complementing the subtrahend."},
        {"sutra": "Anurūpyena", "definition": "Discover multiplication patterns by analyzing proximity to bases like 10 or 100."}
    ]

    # Initialize session variables if not already set
    if 'current_index' not in session:
        session['current_index'] = 0
        session['score'] = 0

    # Get the current index
    current_index = session['current_index']

    # End the game if all sutras have been processed
    if current_index >= len(sutras_and_defs):
        return redirect(url_for('results'))

    # Get the current sutra and definitions
    current_sutra = sutras_and_defs[current_index]
    definitions = [sutra["definition"] for sutra in sutras_and_defs]  # Keep definitions in order

    feedback = None

    # Handle form submission
    if request.method == 'POST':
        selected_definition = request.form.get('definition')
        correct_definition = current_sutra["definition"]

        if selected_definition == correct_definition:
            session['score'] += 10
            session['current_index'] += 1 
            feedback = "Correct! Moving to the next Sutra."
            if session['current_index'] >= len(sutras_and_defs):
                return redirect(url_for('results'))
            return redirect(url_for('matching_game')) 
        else:
            feedback = f"Incorrect. The correct definition was: {correct_definition}"

    return render_template(
        'matching_game.html',
        sutra=current_sutra["sutra"],
        definitions=definitions,
        feedback=feedback
    )


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['player_name'] = request.form.get('player_name', 'Guest')  # Use player_name
        session['score'] = 0  # Initialize score
        return redirect(url_for('start_game'))  # Redirect to game start

    game = request.form.get('game')
    if game == 'matching':
        return redirect(url_for('start_matching_game'))
    elif game == 'calculating':
        return redirect(url_for('start_calculating_game'))
    return render_template('home.html')


@app.route('/start-matching')
def start_matching_game():
    session.clear()  # Clear session to reset the matching game
    session['score'] = 0
    session['current_index'] = 0  # Reset the current index for the matching game
    session['matching_game_score'] = 0
    return redirect(url_for('matching_game'))  # Redirect to the matching game

@app.route('/start-calculating')
def start_calculating_game():
    session.clear()  # Clear session to reset the calculating game
    session['score'] = 0
    session['level'] = 1  # Start from the first level
    return redirect(url_for('play_level'))  # Redirect to the calculating game



@app.route('/level', methods=['GET', 'POST'])
def play_level():
    level = session.get('level', 1)
    if level > len(LEVELS):
        return redirect(url_for('results'))

    level_info = LEVELS[level]

    if request.method == 'POST':
        answer = request.form.get('answer')
        correct_answer = session.get('correct_answer', None)
        feedback = ""

        if correct_answer is not None and str(answer) == str(correct_answer):
            session['score'] += 10
            session['level'] += 1
            return redirect(url_for('play_level'))
        else:
            feedback = f"Incorrect! The correct answer was {correct_answer}. "
            feedback += f"Sutra: {level_info['sanskrit']} - {level_info['description']}"
            session['feedback'] = feedback

    # Generate problem
    problem, correct_answer = generate_problem(level)
    session['correct_answer'] = correct_answer

    return render_template(
        'level.html',
        level=level,
        level_info=level_info,
        problem=problem,
        feedback=session.pop('feedback', None)
    )

@app.route('/results')
def results():
    score = session.get('score', 0)
    matching_game_score = session.get('matching_game_score', 0)
    return render_template('results.html', score=score, matching_game_score=matching_game_score)

def generate_problem(level):
    if level == 1:
        num = random.choice(range(10, 90, 10)) + 5
        problem = f"Find the square of {num}"
        correct_answer = (num // 10) * (num // 10 + 1) * 100 + 25
    elif level == 2:
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        problem = f"Multiply {num1} x {num2}"
        correct_answer = num1 * num2
    elif level == 3:
        num1 = random.randint(100, 999)
        num2 = random.randint(2, 9)
        problem = f"Divide {num1} by {num2} (Round to 2 decimals)"
        correct_answer = round(num1 / num2, 2)
    elif level == 4:
        num1 = random.randint(100, 999)
        num2 = random.randint(10, 99)
        problem = f"Subtract {num2} from {num1}"
        correct_answer = num1 - num2
    elif level == 5:
        num = random.randint(11, 99)
        problem = f"Multiply {num} x 11"
        correct_answer = num * 11
    else:
        problem = "Invalid level"
        correct_answer = None
    return problem, correct_answer

if __name__ == '__main__':
    app.run(debug=True)
