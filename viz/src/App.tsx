import { Routes, Route } from "react-router-dom";
import { HomePage } from "./components/HomePage";
import { GameBoard } from "./components/GameBoard";
import "./App.css";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/game/:sessionId" element={<GameBoard />} />
    </Routes>
  )
}
