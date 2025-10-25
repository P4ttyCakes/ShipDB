from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_schema():
    """Generate database schema"""
    return {"message": "Schema generation coming soon"}
