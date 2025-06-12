import { Header } from "./components/Header";
import { PlayerBoard } from "./components/PlayerBoard";
import { BoardCenter } from "./components/BoardCenter";
import FactoryPanel from "./components/FactoryPanel.tsx";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <Header />
      
      <div className="game-layout">
        <div className="left-section">
          <FactoryPanel />
          <BoardCenter />
        </div>
        
        <div className="right-section">
          <div className="player-boards">
            <PlayerBoard playerIndex={0} />
            <PlayerBoard playerIndex={1} />
          </div>
        </div>
      </div>
    </div>
  )
}
