let username = '';
let currentRound = 0;
let score = 0;
let totalTime = 0;
let wrongAnswers = [];
let startTime;
let timerInterval;

let leaderboard = [];
let questions = [];

// Read backend API base URL from environment variable or default
const BACKEND_API_BASE = window.BACKEND_API_BASE || (typeof process !== 'undefined' && process.env && process.env.BACKEND_API_BASE) || '/backend/api.php';

const welcomeScreen = document.getElementById('welcome-screen');
const gameScreen = document.getElementById('game-screen');
const scoreScreen = document.getElementById('score-screen');
const playBtn = document.getElementById('play-btn');
const nextBtn = document.getElementById('next-btn');
const quitBtn = document.getElementById('quit-btn');
const spinner = document.getElementById('spinner');
const optionsForm = document.getElementById('options-form');
const imageContainer = document.getElementById('image-container');

playBtn.onclick = async () => {
    username = document.getElementById('username').value.trim();
    if (!username) {
        alert('Please enter your name');
        return;
    }
    welcomeScreen.style.display = 'none';
    gameScreen.style.display = 'block';
    startTime = Date.now();
    currentRound = 1;
    score = 0;
    wrongAnswers = [];
    // Fetch questions from backend
    spinner.style.display = 'block';
    try {
        const res = await fetch(`${BACKEND_API_BASE}?endpoint=questions`);
        const data = await res.json();
        questions = data.questions || [];
    } catch (e) {
        alert('Failed to load questions from server.');
        spinner.style.display = 'none';
        return;
    }
    spinner.style.display = 'none';
    showQuestion();
    // Start timer
    const timerSpan = document.getElementById('timer');
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if (timerSpan) {
            timerSpan.textContent = `Time: ${Math.floor((Date.now() - startTime) / 1000)}s`;
        }
    }, 1000);
};

nextBtn.onclick = () => {
    nextBtn.disabled = true;
    spinner.style.display = 'block';
    setTimeout(() => {
        spinner.style.display = 'none';
        nextBtn.disabled = false;
        // Check if an answer was selected before moving to next question
        const selected = document.querySelector('input[name="option"]:checked');
        const q = questions[currentRound - 1];
        if (selected && q) {
            if (parseInt(selected.value) === q.answer) {
                score++;
            } else {
                wrongAnswers.push([q.opt1, q.opt2, q.opt3, q.opt4][selected.value-1]);
            }
        }
        currentRound++;
        showQuestion();
        // Show current score after moving to next question
        const scoreSpan = document.getElementById('current-score');
        if (scoreSpan) scoreSpan.textContent = `Score: ${score}`;
    }, 800);
};

quitBtn.onclick = () => {
    totalTime = Math.floor((Date.now() - startTime) / 1000);
    gameScreen.style.display = 'none';
    scoreScreen.style.display = 'block';
    if (timerInterval) clearInterval(timerInterval);
    // Save user and score to backend
    (async () => {
        let userId = null;
        try {
            const userRes = await fetch(`${BACKEND_API_BASE}?endpoint=save_user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: username })
            });
            const userData = await userRes.json();
            userId = userData.user_id;
        } catch (e) {
            console.error('Failed to save user:', e);
        }
        if (userId) {
            try {
                await fetch(`${BACKEND_API_BASE}?endpoint=save_scores`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        rounds: questions.length,
                        score: score,
                        total_time: totalTime
                    })
                });
            } catch (e) {
                console.error('Failed to save score:', e);
            }
        }
    })();
    // Add current session to leaderboard
    const session = {
        name: username,
        date: new Date().toLocaleString(),
        score: score
    };
    leaderboard.push(session);
    localStorage.setItem('leaderboard', JSON.stringify(leaderboard));
    // Show score value
    document.getElementById('score-value').innerHTML = `<p>Name: ${username}</p><p>Score: ${score}</p><p>Wrong Answers: ${wrongAnswers.join(', ')}</p><p>Total Time: ${totalTime}s</p>`;
    // Render leaderboard
    renderLeaderboard();
};
function renderLeaderboard() {
    const tbody = document.getElementById('leaderboard-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    fetch(`${BACKEND_API_BASE}?endpoint=scores`)
        .then(res => res.json())
        .then(data => {
            const scores = data.scores || [];
            scores.slice(-10).reverse().forEach(entry => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-4 py-2 border-b border-blue-200 font-mono">${entry.name}</td>
                    <td class="px-4 py-2 border-b border-blue-200 font-mono">${entry.datetime}</td>
                    <td class="px-4 py-2 border-b border-blue-200 font-mono">${entry.score}</td>
                    <td class="px-4 py-2 border-b border-blue-200 font-mono">${entry.total_time ? entry.total_time + 's' : ''}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function showQuestion() {
    // Update header with current score and progress
    const scoreSpan = document.getElementById('current-score');
    const progressSpan = document.getElementById('quiz-progress');
    if (scoreSpan) scoreSpan.textContent = `Score: ${score}`;
    if (progressSpan) progressSpan.textContent = `Quiz: ${currentRound}/${questions.length}`;

    // Show question from DB
    const q = questions[currentRound - 1];
    if (!q) {
        quitBtn.onclick();
        return;
    }
    imageContainer.innerHTML = `<img src="./posters_blurred_east/${q.image}" alt="Movie Poster" style="max-width:100%;border-radius:8px;">`;
    optionsForm.innerHTML = '';
    const options = [q.opt1, q.opt2, q.opt3, q.opt4];
    options.forEach((opt, idx) => {
        const label = document.createElement('label');
        label.className = 'flex items-center mb-2 cursor-pointer w-full px-2 py-2 rounded-lg hover:bg-pink-100 transition';
        label.htmlFor = `option${idx+1}`;
        label.innerHTML = `
            <input id="option${idx+1}" type="radio" name="option" value="${idx+1}" class="accent-pink-500 w-5 h-5 mr-3 cursor-pointer align-middle">
            <span class="font-mono text-lg text-blue-900 select-none align-middle">${opt}</span>
        `;
        optionsForm.appendChild(label);
    });
    optionsForm.onsubmit = (e) => {
        e.preventDefault();
        const selected = document.querySelector('input[name="option"]:checked');
        if (!selected) return alert('Select an option');
        if (parseInt(selected.value) === q.answer) {
            score++;
            console.log(`User selected RIGHT answer: ${options[selected.value-1]}`);
        } else {
            wrongAnswers.push(options[selected.value-1]);
            console.log(`User selected WRONG answer: ${options[selected.value-1]}, correct was: ${options[q.answer-1]}`);
        }
        // Always show updated score after answering
        if (scoreSpan) scoreSpan.textContent = `Score: ${score}`;
        if (progressSpan) progressSpan.textContent = `Quiz: ${currentRound}/${questions.length}`;
        if (currentRound >= questions.length) quitBtn.onclick();
    };
}

// Add event listener for Play Again button to return to welcome screen
document.addEventListener('DOMContentLoaded', function() {
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.addEventListener('click', function() {
            document.getElementById('score-screen').style.display = 'none';
            document.getElementById('welcome-screen').style.display = '';
        });
    }
    // Render leaderboard on load (if any)
    renderLeaderboard();
});
