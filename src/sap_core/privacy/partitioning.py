from __future__ import annotations

from typing import Iterable, List, Set

from sap_core.domain.models import Scope, SkillRecord, SkillView


_VIEW_SCOPES = {
    SkillView.person: {Scope.private, Scope.workspace_local, Scope.org_local, Scope.consortium_shared},
    SkillView.institution: {Scope.workspace_local, Scope.org_local, Scope.consortium_shared},
}


def allowed_scopes(view: SkillView) -> Set[Scope]:
    return _VIEW_SCOPES.get(view, _VIEW_SCOPES[SkillView.person])


def filter_skill_records(records: Iterable[SkillRecord], view: SkillView) -> List[SkillRecord]:
    scopes = allowed_scopes(view)
    filtered = [r for r in records if r.visibility in scopes]
    if view == SkillView.institution:
        return [r.model_copy(update={"evidence": None}) for r in filtered]
    return filtered
