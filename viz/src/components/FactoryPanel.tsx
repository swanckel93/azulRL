import { RETRO_COLOR_PALLET } from "../constants/colors.ts"
import FactoryCard from "./FactoryCard.tsx"
import "./FactoryPanel.css"
RETRO_COLOR_PALLET


export default function FactoryPanel() {

    return (
        <div className="factory-panel">
            Factories
            {[0, 1, 2, 3, 4].map((factoryIndex) => (
                <FactoryCard key={factoryIndex} index={factoryIndex} />
            ))}
        </div>
    )
}