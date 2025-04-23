from SOPReview.fileparser import parser
from SOPReview.reviewer import review_sop
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db,TokenDep,get_current_user

from app.models import User
# from app.schemas import SOPReviewRequest

router = APIRouter(tags=["sop_review"],prefix ="/api/v1")

@router.post("/sop-review")
async def sop_review_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        # Check if the file is a PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        content = await file.read()
        # print(type(content))
        sop_content = parser(content)
        # print(type(sop_content))
        # Review the SOP
        review_result = review_sop(sop_content)

        return JSONResponse(content={"review": review_result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))