from fastapi import APIRouter, Depends

from ..dependencies import answer_service, require_database
from ..schemas import AnswerRequest, CodoAnswerOut
from ..services.answers import AnswerService

router = APIRouter(prefix="/v1/ai", tags=["codo-ai"])


@router.post("/answer", response_model=CodoAnswerOut)
async def answer(request: AnswerRequest, _: None = Depends(require_database), service: AnswerService = Depends(answer_service)) -> CodoAnswerOut:
    return await service.answer(request)
