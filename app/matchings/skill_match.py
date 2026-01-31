def skill_score(resume_skills, jd_skills):
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)

    matched = resume_set & jd_set
    missing = jd_set - resume_set

    score = len(matched) / max(len(jd_set), 1)

    return {
        "score": score,
        "matched": list(matched),
        "missing": list(missing)
    }
