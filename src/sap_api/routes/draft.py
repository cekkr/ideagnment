from __future__ import annotations

from fastapi import APIRouter, Depends

from sap_api.deps import get_con
from sap_core.domain.models import AlignmentReport, DraftAnalyzeRequest, DraftRenderRequest, DraftRenderResponse
from sap_core.pipelines.draft_analyze import analyze_draft
from sap_core.pipelines.draft_render import render_draft
from sap_core.retrieval.retrieve import retrieve_bundle

router = APIRouter(prefix="/v1/draft", tags=["draft"])

_llm = None


@router.post("/analyze", response_model=AlignmentReport)
def analyze(req: DraftAnalyzeRequest, con=Depends(get_con)) -> AlignmentReport:
    report = analyze_draft(
        con=con,
        workspace_id=req.workspace_id,
        draft_text=req.draft_text,
        recipients=req.recipients,
        recipient_lenses=req.recipient_lenses,
        mode=req.mode,
        query_vec=None,
    )
    return report


@router.post("/render", response_model=DraftRenderResponse)
def render(req: DraftRenderRequest, con=Depends(get_con)) -> DraftRenderResponse:
    capsules = retrieve_bundle(con, req.workspace_id, query=req.draft_text[:600], query_vec=None)
    out = render_draft(
        llm=_llm,
        draft=req.draft_text,
        capsules=capsules,
        target_lens=req.target_lens,
        max_added_chars=req.max_added_chars,
    )
    return DraftRenderResponse(**out)
