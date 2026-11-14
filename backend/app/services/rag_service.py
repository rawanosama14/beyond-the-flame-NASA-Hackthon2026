from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.services.llm_service import LLMService
from app.services.retrieval import ResearchRetriever

PARTIAL_GRAVITY_RULE = (
    "The supplied PSI corpus does not include direct partial-gravity combustion experiment data. "
    "Do not treat E-FIELD Flames as partial gravity: electric-field effects are an analogue, not lunar/Martian gravity. "
    "Microgravity and normal-gravity evidence may bound intermediate-gravity behavior, but do not establish it."
)
ROCKET_SCOPE_RULE = "Rocket and propellant fire safety is outside this project's scope."


def _is_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06ff]", text or ""))


def _source_citation(doc: Dict[str, Any]) -> Dict[str, str]:
    url = doc.get("source_url")
    if not url or not str(url).startswith("https://"):
        return {}
    return {"title": doc.get("title", doc.get("source_file", "Research source")), "url": url}


class RAGService:
    def __init__(self, retriever: ResearchRetriever, llm: LLMService):
        self.retriever = retriever
        self.llm = llm

    def _prompt(self, question: str, scenario: str, docs: List[Dict[str, Any]]) -> str:
        context = []
        for i, doc in enumerate(docs, 1):
            context.append(
                f"[S{i}] Title: {doc['title']}\nFile: {doc['source_file']}\nPage: {doc['page_number']}\n"
                f"Evidence type: {doc.get('evidence_type','not specified')}\nText: {doc['text'][:2600]}"
            )
        return (
            "Research scenario: " + scenario + "\nQuestion: " + question + "\n\n"
            "Answer in the same language as the question. Only use the evidence below. Cite every factual claim with [S#]. "
            "Never invent numerical values, fuels, oxygen ranges, airflow, sensors, or hardware. Distinguish measured findings from objectives, hypotheses, models, and reviews. "
            "If evidence is missing, say 'not found in the data' (Arabic: غير موجود في البيانات المتاحة). "
            "Do not claim direct lunar/Martian partial-gravity combustion data; E-FIELD is an electric-field analogue only. "
            "Do not answer rocket/propellant fire questions; this is out of scope. Do not convert challenge-context assumptions into test results.\n\n"
            + PARTIAL_GRAVITY_RULE + "\n" + ROCKET_SCOPE_RULE + "\n\nRetrieved evidence:\n" + "\n\n".join(context)
        )

    @staticmethod
    def _extractive_answer(question: str, docs: List[Dict[str, Any]]) -> str:
        ar = _is_arabic(question)
        if not docs:
            return "لم أجد إجابة مباشرة في النصوص البحثية المتاحة." if ar else "Not found in the supplied research data."
        top = docs[:3]
        if ar:
            parts = ["الإجابة مبنية على المقاطع المسترجعة فقط؛ لا تمثل تقييمًا معتمدًا لمخاطر الحريق."]
            for i, d in enumerate(top, 1):
                excerpt = re.sub(r"\s+", " ", d["text"]).strip()
                excerpt = excerpt[:680]
                parts.append(f"الدليل {i}: {excerpt} [Source: {d['title']}, p. {d['page_number']}]")
            parts.append("أي قيمة أو شرط غير ظاهر في المقتطفات يُعد غير محدد في البيانات المتاحة.")
        else:
            parts = ["Extractive answer from the retrieved research corpus only; this is not a certified fire-risk assessment."]
            for i, d in enumerate(top, 1):
                excerpt = re.sub(r"\s+", " ", d["text"]).strip()[:680]
                parts.append(f"Evidence {i}: {excerpt} [Source: {d['title']}, p. {d['page_number']}]")
            parts.append("Any value or condition not visible in these excerpts is not specified in the supplied data.")
        return "\n\n".join(parts)

    async def answer(self, question: str, scenario: str, top_k: int = 5) -> Dict[str, Any]:
        lower = question.casefold()
        if any(x in lower for x in ["rocket", "propellant", "launch vehicle", "صاروخ", "الصاروخ", "الصواريخ", "وقود الصواريخ", "وقود دافع", "مادة دافعة"]):
            msg = "هذا الموضوع خارج نطاق المشروع؛ النطاق هنا هو سلامة الحرائق داخل مساكن وموائل الطاقم، وليس الصواريخ أو المواد الدافعة." if _is_arabic(question) else ROCKET_SCOPE_RULE
            return {"answer": msg, "citations": [], "mode": "scope_guard", "retrieved": 0}
        filters = {}
        scenario_terms = {
            "moon base": "habitat material flammability oxygen-enriched atmosphere fire safety",
            "space station": "spacecraft fire flame spread smoke aerosol detection",
            "mars habitat": "habitat material flammability oxygen-enriched atmosphere fire safety",
            "pressurized rover": "confined vehicle smoke aerosol detection fire safety",
        }
        retrieval_query = question + " " + scenario_terms.get(scenario.casefold(), scenario)
        docs = self.retriever.retrieve(retrieval_query, top_k=top_k, filters=filters, strategy="hybrid")
        # Treat direct partial-gravity questions cautiously; never extrapolate as measured results.
        partial_q = any(x in lower for x in [
            "partial gravity", "lunar gravity", "mars gravity", "جاذبية جزئية",
            "الجاذبية الجزئية", "جاذبية القمر", "الجاذبية القمرية",
            "جاذبية المريخ", "الجاذبية المريخية",
        ])
        prompt = self._prompt(question, scenario, docs)
        generated = await self.llm.generate(prompt)
        all_markers = set(re.findall(r"\[S(\d+)\]", generated or ""))
        valid_markers = {m for m in all_markers if 1 <= int(m) <= len(docs)}
        marker_citations = {
            marker: _source_citation(docs[int(marker) - 1])
            for marker in valid_markers
        }
        generated_is_citable = bool(
            generated and valid_markers and len(valid_markers) == len(all_markers)
            and all(marker_citations.values())
        )
        citations: List[Dict[str, str]] = []
        if generated_is_citable:
            answer = generated.strip()
            citations = [marker_citations[m] for m in sorted(valid_markers, key=lambda x: int(x))]
        else:
            answer = self._extractive_answer(question, docs)
            citations = [_source_citation(d) for d in docs[:3]]
            citations = [c for c in citations if c]
        if partial_q:
            guard = PARTIAL_GRAVITY_RULE
            if _is_arabic(question):
                guard = "تنبيه علمي: لا تتضمن مجموعة بيانات PSI المرفقة قياسات احتراق مباشرة في الجاذبية الجزئية. تأثير E-FIELD الكهربائي ليس تجربة جاذبية قمرية أو مريخية. يمكن استخدام نتائج microgravity و1g كحدود مقارنة فقط، لا كنتائج مثبتة للجاذبية الوسيطة."
            if guard not in answer:
                answer += "\n\n" + guard
        mode = "llm_grounded" if generated_is_citable else "extractive_fallback"
        return {"answer": answer, "citations": citations, "mode": mode, "retrieved": len(docs), "sources": [
            {"title": d["title"], "source_file": d["source_file"], "page": d["page_number"], "score": d["score"], "source_url": d.get("source_url")}
            for d in docs
        ]}
