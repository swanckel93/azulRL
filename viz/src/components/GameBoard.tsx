import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Header } from "./Header";
import { PlayerBoard } from "./PlayerBoard";
import { BoardCenter } from "./BoardCenter";
import FactoryPanel from "./FactoryPanel";
import useStore from "../stores/GameStore";

export function GameBoard() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const currentSessionId = useStore(state => state.sessionId);
  const restoreSession = useStore(state => state.restoreSession);
  const gameState = useStore(state => state.gameState);

  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      // Page was refreshed or navigated to with a session ID
      console.log(`Restoring session: ${sessionId}`);
      restoreSession(sessionId).catch(() => {
        // Session restoration failed, redirect to home
        navigate('/');
      });
    }
  }, [sessionId, currentSessionId, restoreSession, navigate]);

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
            {gameState.players?.map((_, index) => (
              <PlayerBoard key={index} playerIndex={index} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}