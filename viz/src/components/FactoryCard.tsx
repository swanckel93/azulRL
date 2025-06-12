import { useState } from 'react';
import useStore from '../stores/GameStore';
import { RETRO_COLOR_PALLET } from '../constants/colors';
import { TilePlaceholderType, type TilePlaceHolder } from '../types/TilePlaceholder';
import './FactoryCard.css';
import TilePlaceholderComponent from './TilePlaceholder';
import { TileComponent } from './TileComponent';
import type { Tile } from '../types/Tile';
import { TileType } from '../types/Tile';

interface FactoryCard {
    index: number
}

export default function FactoryCard(props: FactoryCard) {
    const getFactoryByIndex = useStore(state => state.getFactoryByIndex)
    const partialAction = useStore(state => state.partialAction)
    const selectTileFromFactory = useStore(state => state.selectTileFromFactory)

    // Local hover state per factory
    const [hoveredTileType, setHoveredTileType] = useState<TileType | null>(null)

    const factory = getFactoryByIndex(props.index)

    const n_total_elements = 5
    const tiles: Tile[] = factory?.tiles ? [...factory.tiles] : []
    const placeholders_needed = n_total_elements - tiles.length

    const placeholders: TilePlaceHolder[] = Array.from(
        { length: placeholders_needed },
        (_, i) => ({ type: TilePlaceholderType.GENERIC, id: i })
    )

    const handleTileClick = (tileType: TileType) => {
        selectTileFromFactory(tileType, props.index)
    }

    const handleTileMouseEnter = (tileType: TileType) => {
        setHoveredTileType(tileType)
    }

    const handleTileMouseLeave = () => {
        setHoveredTileType(null)
    }

    const isSelected = (tileType: TileType) => {
        return partialAction.tileType === tileType && partialAction.factoryId === props.index
    }

    const isHovered = (tileType: TileType) => {
        return hoveredTileType === tileType
    }

    return (
        <div className="factory-card" style={{ backgroundColor: RETRO_COLOR_PALLET.dark_vanilla }}>
            <div className='tile-placeholders-container'>
                {tiles.map((tile, index) => (
                    <div
                        key={`tile-${index}`}
                        className={`tile-wrapper ${isHovered(tile.type) ? 'hovered' : ''} ${isSelected(tile.type) ? 'selected' : ''}`}
                        onMouseEnter={() => handleTileMouseEnter(tile.type)}
                        onMouseLeave={handleTileMouseLeave}
                        onClick={() => handleTileClick(tile.type)}
                    >
                        <TileComponent {...tile} />
                    </div>
                ))}
                {placeholders.map((placeholder, index) => (
                    <TilePlaceholderComponent
                        key={`placeholder-${index}`}
                        {...placeholder}
                    />
                ))}
            </div>
        </div>
    )
}