// ShipDB Frontend Application
const API_BASE_URL = 'http://localhost:8000';

class ShipDBApp {
    constructor() {
        this.currentSession = null;
        this.currentProject = null;
        this.conversationStep = 0;
    }

    createApp() {
        const app = document.createElement('div');
        app.className = 'app-container';
        
        app.innerHTML = `
            <header class="app-header">
                <h1>🚢 ShipDB</h1>
                <p class="subtitle">Instant Cloud Database Deployment</p>
            </header>
            
            <main id="main-content" class="main-content">
                <div id="welcome-section" class="welcome-section">
                    <h2>Welcome to ShipDB</h2>
                    <p>Deploy PostgreSQL or DynamoDB in minutes with AI-powered schema generation.</p>
                    <button id="start-btn" class="btn btn-primary">Start New Project</button>
                </div>
                
                <div id="project-form" class="project-form" style="display: none;">
                    <h2>Create New Project</h2>
                    <form id="project-form-element">
                        <div class="form-group">
                            <label for="project-name">Project Name:</label>
                            <input type="text" id="project-name" name="name" required placeholder="My Awesome Project">
                        </div>
                        <div class="form-group">
                            <label for="project-description">Description:</label>
                            <textarea id="project-description" name="description" placeholder="Describe your project..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Start AI Conversation</button>
                    </form>
                </div>
                
                <div id="conversation-section" class="conversation-section" style="display: none;">
                    <h2>AI Conversation</h2>
                    <div id="conversation-log" class="conversation-log"></div>
                    <div class="conversation-input">
                        <input type="text" id="user-input" placeholder="Type your answer here...">
                        <button id="send-answer" class="btn btn-primary">Send</button>
                    </div>
                    <button id="finish-conversation" class="btn btn-secondary" style="display: none;">Finish & Generate Schema</button>
                </div>
                
                <div id="results-section" class="results-section" style="display: none;">
                    <h2>Generated Schema</h2>
                    <div id="schema-results"></div>
                </div>
            </main>
            
            <footer class="app-footer">
                <p>Built with FastAPI & Lovable</p>
            </footer>
        `;
        
        this.setupEventListeners(app);
        return app;
    }

    setupEventListeners(app) {
        // Start project button
        const startBtn = app.querySelector('#start-btn');
        startBtn.addEventListener('click', () => {
            this.showProjectForm();
        });

        // Project form submission
        const projectForm = app.querySelector('#project-form-element');
        projectForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startProject();
        });

        // Send answer button
        const sendBtn = app.querySelector('#send-answer');
        sendBtn.addEventListener('click', () => {
            this.sendAnswer();
        });

        // Enter key in input
        const userInput = app.querySelector('#user-input');
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendAnswer();
            }
        });

        // Finish conversation button
        const finishBtn = app.querySelector('#finish-conversation');
        finishBtn.addEventListener('click', () => {
            this.finishConversation();
        });
    }

    showProjectForm() {
        document.getElementById('welcome-section').style.display = 'none';
        document.getElementById('project-form').style.display = 'block';
    }

    async startProject() {
        const name = document.getElementById('project-name').value;
        const description = document.getElementById('project-description').value;

        // Store project name globally for deployment
        window.currentProjectName = name;

        try {
            const response = await fetch(`${API_BASE_URL}/api/projects/new_project/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, description })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentSession = result.session_id;
            this.showConversation(result.prompt);
        } catch (error) {
            alert(`Error starting project: ${error.message}`);
        }
    }

    showConversation(initialPrompt) {
        document.getElementById('project-form').style.display = 'none';
        document.getElementById('conversation-section').style.display = 'block';
        
        const log = document.getElementById('conversation-log');
        log.innerHTML = `<div class="ai-message">🤖 ${initialPrompt}</div>`;
        
        document.getElementById('user-input').focus();
    }

    async sendAnswer() {
        const input = document.getElementById('user-input');
        const answer = input.value.trim();
        
        if (!answer) return;

        // Add user message to log
        const log = document.getElementById('conversation-log');
        log.innerHTML += `<div class="user-message">👤 ${answer}</div>`;
        input.value = '';

        try {
            const response = await fetch(`${API_BASE_URL}/api/projects/new_project/next`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    answer: answer
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Add AI response to log
            log.innerHTML += `<div class="ai-message">🤖 ${result.prompt}</div>`;
            
            if (result.done) {
                // Show finish options but don't disable input - allow continued conversation
                document.getElementById('finish-conversation').style.display = 'block';
                
                // Keep input enabled for continued conversation
                document.getElementById('user-input').disabled = false;
                document.getElementById('send-answer').disabled = false;
                
                // Add a subtle indicator that the AI thinks it's done
                const messages = log.querySelectorAll('.ai-message');
                const lastMessage = messages[messages.length - 1];
                lastMessage.innerHTML = `🤖 ${result.prompt} <span style="color: #10b981; font-size: 0.9em;">(AI thinks conversation is complete - you can continue or finish)</span>`;
            }
            
            // Scroll to bottom
            log.scrollTop = log.scrollHeight;
        } catch (error) {
            alert(`Error sending answer: ${error.message}`);
        }
    }

    async finishConversation() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/projects/new_project/finish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSession
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentProject = result.project_id;
            
            // Generate schema
            await this.generateSchema(result.spec);
        } catch (error) {
            alert(`Error finishing conversation: ${error.message}`);
        }
    }

    async generateSchema(spec) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/schema/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(spec)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const artifacts = await response.json();
            this.showResults(artifacts);
        } catch (error) {
            alert(`Error generating schema: ${error.message}`);
        }
    }

    showResults(artifacts) {
        document.getElementById('conversation-section').style.display = 'none';
        document.getElementById('results-section').style.display = 'block';
        
        const resultsDiv = document.getElementById('schema-results');
        resultsDiv.innerHTML = `
            <div class="schema-section">
                <h3>📝 PostgreSQL SQL</h3>
                <pre><code>${artifacts.postgres_sql || 'No SQL generated'}</code></pre>
            </div>
            
            <div class="schema-section">
                <h3>📋 JSON Schema</h3>
                <pre><code>${JSON.stringify(artifacts.json_schema, null, 2)}</code></pre>
            </div>
            
            <div class="schema-section">
                <h3>⚡ DynamoDB Tables</h3>
                <pre><code>${JSON.stringify(artifacts.dynamodb_tables, null, 2)}</code></pre>
            </div>
            
            <div class="actions">
                <button onclick="location.reload()" class="btn btn-primary">Start New Project</button>
            </div>
        `;
    }
}

// Initialize the app with error handling
try {
    const app = new ShipDBApp();
    const appContainer = document.getElementById('app');
    if (appContainer) {
        appContainer.appendChild(app.createApp());
    } else {
        console.error('App container not found');
    }
} catch (error) {
    console.error('Error initializing app:', error);
    // Fallback: show basic content
    const appContainer = document.getElementById('app');
    if (appContainer) {
        appContainer.innerHTML = `
            <div class="app-container">
                <header class="app-header">
                    <h1>🚢 ShipDB</h1>
                    <p class="subtitle">Instant Cloud Database Deployment</p>
                </header>
                <main class="main-content">
                    <div class="welcome-section">
                        <h2>Welcome to ShipDB</h2>
                        <p>There was an error loading the application. Please check the console for details.</p>
                        <p>Error: ${error.message}</p>
                        <button onclick="location.reload()" class="btn btn-primary">Reload Page</button>
                    </div>
                </main>
                <footer class="app-footer">
                    <p>Built with FastAPI & Lovable</p>
                </footer>
            </div>
        `;
    }
}
