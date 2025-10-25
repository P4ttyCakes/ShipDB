from fastapi import APIRouter

router = APIRouter()


@router.get("/erd/{project_id}")
async def get_erd(project_id: str):
    """Generate ERD diagram"""
    return {"message": f"ERD for project {project_id} coming soon"}
