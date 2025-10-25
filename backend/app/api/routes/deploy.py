from fastapi import APIRouter

router = APIRouter()


@router.post("/{project_id}")
async def deploy_project(project_id: str):
    """Deploy database to AWS"""
    return {"message": f"Deployment for project {project_id} coming soon"}
