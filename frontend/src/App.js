export function App() {
    const app = document.createElement('div');
    app.className = 'app-container';
    
    app.innerHTML = `
        <header class="app-header">
            <h1>🚢 ShipDB</h1>
            <p class="subtitle">Instant Cloud Database Deployment</p>
        </header>
        
        <main id="main-content" class="main-content">
            <div class="welcome-section">
                <h2>Welcome to ShipDB</h2>
                <p>Deploy PostgreSQL or DynamoDB in minutes with AI-powered schema generation.</p>
                <button id="start-btn" class="btn btn-primary">Start New Project</button>
            </div>
        </main>
        
        <footer class="app-footer">
            <p>Built with FastAPI & Lovable</p>
        </footer>
    `;
    
    // Add event listener for start button
    const startBtn = app.querySelector('#start-btn');
    startBtn.addEventListener('click', () => {
        // For now, just show an alert - this will be replaced with proper routing
        alert('Project creation feature coming soon! Make sure to configure your API keys in the backend .env file.');
    });
    
    return app;
}
