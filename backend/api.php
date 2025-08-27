<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204); // Explicitly return 204 No Content
    exit;
}

// SQLite connection Local
// $db = new PDO('sqlite:../database/triviaimage.db');
// SQLite connection Production
$db = new PDO('sqlite:/var/www/html/database/triviaimage.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Create tables if not exist
$db->exec('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)');
$db->exec('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, image TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT, answer INTEGER)');
$db->exec('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime TEXT, user_id INTEGER, rounds INTEGER, score INTEGER, total_time INTEGER)');

// Seed database with sample user and scores if not present
$questionCheck = $db->query("SELECT COUNT(*) FROM questions")->fetchColumn();
if ($questionCheck == 0) {
    $db->exec("INSERT INTO users (name) VALUES ('SampleUser')");
    $userId = $db->lastInsertId();
    $now = date('Y-m-d H:i:s');
    $db->exec("INSERT INTO scores (datetime, user_id, rounds, score, total_time) VALUES ('$now', $userId, 5, 3, 42)");
    $db->exec("INSERT INTO scores (datetime, user_id, rounds, score, total_time) VALUES ('$now', $userId, 5, 4, 38)");
}

// Simple router
$endpoint = $_GET['endpoint'] ?? '';
if ($endpoint === 'stats') {
    $stmt = $db->query('SELECT users.name, COUNT(scores.id) as total_rounds, SUM(scores.score) as total_score, MAX(scores.score) as best_score FROM users LEFT JOIN scores ON users.id = scores.user_id GROUP BY users.id');
    $stats = $stmt->fetchAll(PDO::FETCH_ASSOC);
    header('Content-Type: application/json');
    echo json_encode(['stats' => $stats]);
    exit;
}
if ($endpoint === 'save_scores') {
    error_log('API: Received request for save_scores endpoint');
    $input = json_decode(file_get_contents('php://input'), true);
    $user_id = $input['user_id'] ?? null;
    $rounds = $input['rounds'] ?? null;
    $score = $input['score'] ?? null;
    $total_time = $input['total_time'] ?? null;
    $datetime = date('Y-m-d H:i:s');
    if (!$user_id || !$rounds || $score === null || $total_time === null) {
        error_log('API: Missing score data');
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Missing score data']);
        exit;
    }
    try {
        $stmt = $db->prepare('INSERT INTO scores (datetime, user_id, rounds, score, total_time) VALUES (?, ?, ?, ?, ?)');
        $stmt->execute([$datetime, $user_id, $rounds, $score, $total_time]);
        error_log('API: Saved score for user ' . $user_id);
        header('Content-Type: application/json');
        echo json_encode(['success' => true]);
    } catch (Exception $e) {
        error_log('API: Error saving score - ' . $e->getMessage());
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Failed to save score']);
    }
    exit;
}
if ($endpoint === 'save_user') {
    error_log('API: Received request for save_user endpoint');
    $input = json_decode(file_get_contents('php://input'), true);
    $name = $input['name'] ?? '';
    if (!$name) {
        error_log('API: No name provided');
        header('Content-Type: application/json');
        echo json_encode(['error' => 'No name provided']);
        exit;
    }
    try {
        $stmt = $db->prepare('INSERT INTO users (name) VALUES (?)');
        $stmt->execute([$name]);
        $userId = $db->lastInsertId();
        error_log('API: Saved user ' . $name . ' with ID ' . $userId);
        header('Content-Type: application/json');
        echo json_encode(['user_id' => $userId]);
    } catch (Exception $e) {
        error_log('API: Error saving user - ' . $e->getMessage());
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Failed to save user']);
    }
    exit;
}
if ($endpoint === 'scores') {
    error_log('API: Received request for scores endpoint');
    try {
        $stmt = $db->query('SELECT scores.datetime, users.name, scores.score, scores.total_time FROM scores LEFT JOIN users ON scores.user_id = users.id ORDER BY scores.id DESC');
        $scores = $stmt->fetchAll(PDO::FETCH_ASSOC);
        error_log('API: Fetched ' . count($scores) . ' scores from DB');
        header('Content-Type: application/json');
        echo json_encode(['scores' => $scores]);
    } catch (Exception $e) {
        error_log('API: Error fetching scores - ' . $e->getMessage());
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Failed to fetch scores']);
    }
    exit;
}
if ($endpoint === 'questions') {
    error_log('API: Received request for questions endpoint');
    try {
        $stmt = $db->query('SELECT image, opt1, opt2, opt3, opt4, answer FROM questions');
        $questions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        error_log('API: Fetched ' . count($questions) . ' questions from DB');
        header('Content-Type: application/json');
        echo json_encode(['questions' => $questions]);
    } catch (Exception $e) {
        error_log('API: Error fetching questions - ' . $e->getMessage());
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Failed to fetch questions']);
    }
    exit;
}


if ($endpoint === 'health') {
    $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
    if (strpos($accept, 'text/html') !== false) {
        header('Content-Type: text/plain');
        echo 'triviaimage backend running';
    } else {
        header('Content-Type: application/json');
        echo json_encode(['status' => 'ok', 'message' => 'triviaimage backend running']);
    }
    exit;
}
