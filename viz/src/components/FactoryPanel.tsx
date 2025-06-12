import FactoryCard from "./FactoryCard.tsx"
import "./FactoryPanel.css"

export default function FactoryPanel() {
    return (
        <div className="factory-panel">
            <h2>Factories</h2>
            {[0, 1, 2, 3, 4].map((factoryIndex) => (
                <FactoryCard key={factoryIndex} index={factoryIndex} />
            ))}
        </div>
    )
}