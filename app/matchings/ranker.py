from app.matchings.scorer import score_candidate

def rank_candidates(resumes: list, jd: dict):
    results = []

    for resume in resumes:
        score = score_candidate(resume, jd)
        results.append({
            "candidate_id": resume["id"],
            "score": score
        })

    results.sort(
        key=lambda x: x["score"]["final_score"],
        reverse=True
    )

    return results
