from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get("")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "azul-game-api"}