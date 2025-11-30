let tasks = [];
let nextId = 1;

function renderTasksList() {
    const ul = document.getElementById('tasks-list');
    ul.innerHTML = '';
    tasks.forEach(t => {
        const li = document.createElement('li');
        li.textContent = `${t.title} (due: ${t.due_date || 'N/A'}, hours: ${t.estimated_hours ?? 'N/A'}, importance: ${t.importance})`;
        ul.appendChild(li);
    });
}

document.getElementById('task-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const title = document.getElementById('task-title').value.trim();
    const dueDate = document.getElementById('task-due-date').value;
    const hoursRaw = document.getElementById('task-hours').value;
    const importanceRaw = document.getElementById('task-importance').value;

    if (!title || !importanceRaw) {
        alert('Title and importance are required.');
        return;
    }

    const importance = Number(importanceRaw);
    if (importance < 1 || importance > 10) {
        alert('Importance must be between 1 and 10.');
        return;
    }

    const task = {
        id: String(nextId++),
        title,
        importance,
        dependencies: []
    };
    if (dueDate) task.due_date = dueDate;
    if (hoursRaw) task.estimated_hours = Number(hoursRaw);

    tasks.push(task);
    renderTasksList();
    e.target.reset();
});

document.getElementById('suggest-btn').addEventListener('click', async function () {
    const status = document.getElementById('status-text');
    const resultsDiv = document.getElementById('results');
    const strategy = document.getElementById('strategy-select').value;

    if (tasks.length === 0) {
        alert('Add at least one task first.');
        return;
    }

    status.textContent = 'Analyzing...';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch('http://127.0.0.1:8000/api/tasks/analyze/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                strategy: strategy,
                tasks: tasks
            })
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(text || 'Request failed');
        }

        const data = await response.json();
        const top = data.slice(0, 3); // top 3 suggested
        status.textContent = `Suggested ${top.length} task(s)`;

        top.forEach(task => {
            const div = document.createElement('div');
            div.className = 'result-item';
            div.innerHTML = `
                <strong>${task.title}</strong> (score: ${task.score})<br>
                Due: ${task.due_date || 'N/A'}, Hours: ${task.estimated_hours ?? 'N/A'}, Importance: ${task.importance}<br>
                <small>${task.explanation}</small>
            `;
            resultsDiv.appendChild(div);
        });
    } catch (err) {
        console.error(err);
        status.textContent = 'Error during analysis';
        alert('Error calling API: ' + err.message);
    }
});

// initial render
renderTasksList();
