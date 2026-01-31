from app.embeddings.embedder import get_embedding
from app.matchings.similarity import cosine_similarity
from app.matchings.skill_match import skill_score


def build_resume_text(resume: dict) -> str:
    return f"""
    Skills: {", ".join(resume.get("skills", []))}
    Roles: {", ".join(resume.get("roles", []))}
    Education: {resume.get("education", "")}
    Tools: {", ".join(resume.get("tools", []))}
    Experience: {resume.get("years_of_experience", 0)} years
    """


def build_jd_text(jd: dict) -> str:
    return f"""
    Role: {jd.get("role", "")}
    Required Skills: {", ".join(jd.get("skills", []))}
    Minimum Experience: {jd.get("min_experience", 0)} years
    """


def score_candidate(resume: dict, jd: dict):
    resume_text = build_resume_text(resume)
    jd_text = build_jd_text(jd)

    resume_embedding = get_embedding(resume_text)
    jd_embedding = get_embedding(jd_text)

    semantic_similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )

    skill_result = skill_score(
        resume.get("skills", []),
        jd.get("skills", [])
    )

    experience_score = min(
        resume.get("years_of_experience", 0) / max(jd.get("min_experience", 1), 1),
        1.0
    )

    final_score = (
        0.6 * semantic_similarity +
        0.3 * skill_result["score"] +
        0.1 * experience_score
    )

    return {
        "final_score": round(final_score * 100, 2),
        "semantic_similarity": round(semantic_similarity, 3),
        "skill_match": skill_result,
        "experience_score": round(experience_score, 2)
    }
