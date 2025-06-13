import { Header } from "./Header";
import "./HomePage.css";

export function HomePage() {
  return (
    <div className="app">
      <Header />
      
      <div className="home-content">
        <div className="welcome-section">
          <h1>Welcome to Azul</h1>
          <p>Start a new game or join an existing session by clicking "Start New Game" above.</p>
          
          <div className="game-info">
            <h2>How to Play</h2>
            <ul>
              <li>Select tiles from factories or the center</li>
              <li>Place tiles in your pattern lines</li>
              <li>Complete pattern lines to move tiles to your wall</li>
              <li>Score points for completed rows, columns, and tile sets</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}