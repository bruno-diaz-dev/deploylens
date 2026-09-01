from fastapi import APIRouter, HTTPException

from models import Deployment
from repositories.deployments import (
    get_all_deployments,
    create_deployment,
    update_deployment,
    delete_deployment
)

router = APIRouter(
    prefix="/api/deployments",
    tags=["deployments"]
)

@router.get("")
def get_deployments():
    return get_all_deployments()

@router.post("")
def create_new_deployment(deployment: Deployment):
    return create_deployment(deployment)

@router.put("/{deployment_id}")
def update_existing_deployment(
    deployment_id: int,
    deployment: Deployment
):
    updated_deployment = update_deployment(
        deployment_id,
        deployment
    )

    if updated_deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return updated_deployment

@router.delete("/{deployment_id}")
def delete_existing_deployment(deployment_id: int):
    deleted = delete_deployment(deployment_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    return {
        "message": "Deployment deleted",
        "id": deployment_id
    }