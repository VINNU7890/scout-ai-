from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

from backend.app.schemas import Finding, SourceItem


def extract_citation_indices(text: str) -> List[int]:
    """Extracts all citation indices like [1], [2], [1, 3] from a markdown text."""
    matches = re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", text)
    indices: Set[int] = set()
    for m in matches:
        parts = m.split(",")
        for p in parts:
            p_strip = p.strip()
            if p_strip.isdigit():
                indices.add(int(p_strip))
    return sorted(list(indices))


def build_source_catalog(findings: List[Finding]) -> Tuple[List[SourceItem], Dict[str, int]]:
    """
    Builds a list of SourceItem with unique 1-based IDs from a list of findings.
    Returns (sources_list, source_key_to_id_mapping).
    """
    sources: List[SourceItem] = []
    source_key_to_id: Dict[str, int] = {}

    for f in findings:
        key = (
            f.source_url
            if f.source_type == "web" and f.source_url
            else f"{f.doc_name}#p{f.page or 1}"
        )
        if not key:
            continue

        if key not in source_key_to_id:
            new_id = len(sources) + 1
            source_key_to_id[key] = new_id

            domain = None
            if f.source_type == "web" and f.source_url:
                try:
                    domain = urlparse(f.source_url).netloc
                except Exception:
                    domain = None

            title = (
                f.doc_name if f.source_type == "doc" else (domain or f.source_url or "Web Source")
            )

            sources.append(
                SourceItem(
                    id=new_id,
                    title=title,
                    url=f.source_url,
                    doc_name=f.doc_name,
                    page=f.page,
                    domain=domain,
                    source_type=f.source_type,
                    retrieved_at=f.retrieved_at,
                    supported_claims=[f.claim],
                )
            )
        else:
            existing_id = source_key_to_id[key]
            item = next(s for s in sources if s.id == existing_id)
            if f.claim not in item.supported_claims:
                item.supported_claims.append(f.claim)

    return sources, source_key_to_id
