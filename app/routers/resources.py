from fastapi import APIRouter, Depends

from dependencies import require_permission
from schemas import MockResourceOut

router = APIRouter(prefix="/resources", tags=["resources"])


DOCUMENTS = [
    {"id": 1, "title": "Contract draft"},
    {"id": 2, "title": "Architecture note"},
]

REPORTS = [
    {"id": 1, "name": "Quarterly finance"},
    {"id": 2, "name": "Security audit"},
]


@router.get("/documents", response_model=MockResourceOut)
def read_documents(user=Depends(require_permission("documents", "read"))):
    return MockResourceOut(resource="documents", action="read", data=DOCUMENTS)


@router.post("/documents", response_model=MockResourceOut)
def create_document(user=Depends(require_permission("documents", "create"))):
    return MockResourceOut(
        resource="documents",
        action="create",
        data=[{"id": 3, "title": "New document created"}],
    )


@router.patch("/documents", response_model=MockResourceOut)
def update_document(user=Depends(require_permission("documents", "update"))):
    return MockResourceOut(
        resource="documents",
        action="update",
        data=[{"id": 1, "title": "Contract draft updated"}],
    )


@router.delete("/documents", response_model=MockResourceOut)
def delete_document(user=Depends(require_permission("documents", "delete"))):
    return MockResourceOut(
        resource="documents",
        action="delete",
        data=[{"id": 2, "title": "Architecture note deleted"}],
    )


@router.get("/reports", response_model=MockResourceOut)
def read_reports(user=Depends(require_permission("reports", "read"))):
    return MockResourceOut(resource="reports", action="read", data=REPORTS)