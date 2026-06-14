"""Advanced intelligence layers for Opportunity Radar."""

from __future__ import annotations

import math
import re
import sqlite3
from graphlib import CycleError, TopologicalSorter

from core import Opportunity, Student, days_until, is_open_to, normalize, score_opportunity


CAREER_PATHS = {
    "software engineer": {
        "coding": 3.0,
        "algorithms": 2.4,
        "web development": 2.0,
        "AI": 1.3,
        "data science": 1.0,
        "problem solving": 2.0,
        "engineering": 1.2,
    },
    "cybersecurity analyst": {
        "cybersecurity": 3.0,
        "coding": 2.0,
        "problem solving": 1.8,
        "defence tech": 1.6,
        "algorithms": 1.2,
        "AI": 0.8,
    },
    "data analyst": {
        "data science": 3.0,
        "AI": 2.0,
        "coding": 1.7,
        "math": 1.6,
        "research": 1.3,
        "business": 1.2,
        "public good": 0.8,
    },
    "research scientist": {
        "research": 3.0,
        "science": 2.4,
        "math": 1.8,
        "presentation": 1.2,
        "AI": 1.0,
        "biotech": 1.8,
        "engineering": 1.2,
    },
    "startup founder": {
        "entrepreneurship": 3.0,
        "business": 2.4,
        "marketing": 1.7,
        "public good": 1.4,
        "social impact": 1.4,
        "coding": 1.1,
        "design": 1.0,
    },
    "product designer": {
        "design": 3.0,
        "UI/UX": 2.4,
        "graphic design": 1.6,
        "public good": 1.0,
        "entrepreneurship": 0.9,
        "coding": 0.8,
        "presentation": 1.1,
    },
}

TYPE_MULTIPLIERS = {
    "internship": 1.35,
    "research": 1.25,
    "competition": 1.20,
    "hackathon": 1.15,
    "olympiad": 1.10,
    "workshop": 1.00,
    "programme": 1.00,
    "scholarship": 0.95,
    "volunteering": 0.90,
}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
SPAM = "spam"
LEGIT = "legit"
LABELS = [SPAM, LEGIT]
SPAM_TERMS = {"spam", "scam", "prize", "click", "crypto"}

DEFAULT_TRAINING = [
    (LEGIT, "official school workshop coding ai free beginner friendly application"),
    (LEGIT, "cybersecurity olympiad competition official registration students challenge"),
    (LEGIT, "research attachment programme university lab mentorship official"),
    (LEGIT, "scholarship briefing financial aid school careers office apply"),
    (LEGIT, "robotics workshop engineering students official registration"),
    (LEGIT, "volunteering programme community service youth leadership nonprofit"),
    (LEGIT, "data science bootcamp python statistics machine learning students"),
    (SPAM, "guaranteed scholarship prize win money fast click crypto whatsapp"),
    (SPAM, "earn cash from home urgent referral bonus lucky draw winner"),
    (SPAM, "free iphone giveaway claim prize now suspicious link bit ly"),
    (SPAM, "investment double your money crypto trading guaranteed profit"),
    (SPAM, "paid certificate instant approval no deadline exclusive deal"),
    (SPAM, "miracle admission guaranteed pay deposit agent whatsapp"),
    (SPAM, "urgent winner selected click cash bonus promotional prize"),
]


def career_names() -> list[str]:
    return sorted(CAREER_PATHS)


def tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if len(token) > 1 and not token.isdigit()]


def opportunity_text(opportunity: Opportunity) -> str:
    fields = [
        opportunity.title,
        opportunity.organizer,
        opportunity.type,
        opportunity.cost,
        "beginner friendly" if opportunity.beginner_friendly else "advanced",
        opportunity.deadline,
        opportunity.url,
    ]
    fields.extend(opportunity.interests)
    fields.extend(opportunity.eligible_levels)
    return " ".join(fields)


def review_examples(submissions: list[dict]) -> list[tuple[str, str]]:
    examples: list[tuple[str, str]] = []
    for submission in submissions:
        record = submission.get("opportunity")
        if not isinstance(record, dict):
            continue
        opportunity = Opportunity(**record)
        if submission.get("status") == "approved":
            examples.append((LEGIT, opportunity_text(opportunity)))
        elif submission.get("status") == "rejected":
            note = submission.get("review_note", "")
            if SPAM_TERMS & set(tokenize(note)):
                examples.append((SPAM, opportunity_text(opportunity) + " " + note))
    return examples


def train_spam_model(submissions: list[dict] | None = None) -> dict:
    examples = list(DEFAULT_TRAINING)
    if submissions:
        examples.extend(review_examples(submissions))

    label_counts = {SPAM: 0, LEGIT: 0}
    token_counts = {SPAM: {}, LEGIT: {}}
    total_tokens = {SPAM: 0, LEGIT: 0}
    vocabulary: set[str] = set()

    for label, text in examples:
        label_counts[label] += 1
        for token in tokenize(text):
            vocabulary.add(token)
            token_counts[label][token] = token_counts[label].get(token, 0) + 1
            total_tokens[label] += 1

    return {
        "examples": examples,
        "label_counts": label_counts,
        "token_counts": token_counts,
        "total_tokens": total_tokens,
        "vocabulary": sorted(vocabulary),
    }


def token_log_probability(model: dict, label: str, token: str) -> float:
    vocab_size = max(1, len(model["vocabulary"]))
    count = model["token_counts"][label].get(token, 0)
    return math.log((count + 1) / (model["total_tokens"][label] + vocab_size))


def predict_spam(opportunity: Opportunity, submissions: list[dict] | None = None) -> dict:
    model = train_spam_model(submissions)
    tokens = tokenize(opportunity_text(opportunity))
    scores: dict[str, float] = {}
    total_examples = len(model["examples"])

    for label in LABELS:
        score = math.log((model["label_counts"][label] + 1) / (total_examples + len(LABELS)))
        for token in tokens:
            score += token_log_probability(model, label, token)
        scores[label] = score

    max_score = max(scores.values())
    spam_exp = math.exp(scores[SPAM] - max_score)
    legit_exp = math.exp(scores[LEGIT] - max_score)
    probability = spam_exp / (spam_exp + legit_exp)
    risk = "HIGH" if probability >= 0.78 else "MEDIUM" if probability >= 0.55 else "LOW"
    return {
        "probability": probability,
        "risk": risk,
        "signals": spam_signal_tokens(opportunity, model),
        "model": model,
    }


def spam_signal_tokens(opportunity: Opportunity, model: dict, limit: int = 5) -> list[str]:
    signals = []
    seen = set()
    for token in tokenize(opportunity_text(opportunity)):
        if token in seen:
            continue
        seen.add(token)
        weight = token_log_probability(model, SPAM, token) - token_log_probability(model, LEGIT, token)
        if weight > 0:
            signals.append((token, weight))
    signals.sort(key=lambda item: item[1], reverse=True)
    return [token for token, _ in signals[:limit]]


def model_health(submissions: list[dict]) -> dict:
    model = train_spam_model(submissions)
    examples = model["examples"]
    correct = 0
    for index, held_out in enumerate(examples):
        training = examples[:index] + examples[index + 1:]
        temp_model = train_spam_model([])
        temp_model["examples"] = training
        # Re-train cleanly from tuples.
        label_counts = {SPAM: 0, LEGIT: 0}
        token_counts = {SPAM: {}, LEGIT: {}}
        total_tokens = {SPAM: 0, LEGIT: 0}
        vocabulary: set[str] = set()
        for label, text in training:
            label_counts[label] += 1
            for token in tokenize(text):
                vocabulary.add(token)
                token_counts[label][token] = token_counts[label].get(token, 0) + 1
                total_tokens[label] += 1
        temp_model = {
            "examples": training,
            "label_counts": label_counts,
            "token_counts": token_counts,
            "total_tokens": total_tokens,
            "vocabulary": sorted(vocabulary),
        }
        fake = SimpleTextOpportunity(held_out[1])
        prediction = predict_text_with_model(temp_model, fake.text)
        correct += prediction == held_out[0]

    top_tokens = []
    for token in model["vocabulary"]:
        weight = token_log_probability(model, SPAM, token) - token_log_probability(model, LEGIT, token)
        if weight > 0:
            top_tokens.append((token, weight))
    top_tokens.sort(key=lambda item: item[1], reverse=True)

    return {
        "total": len(examples),
        "seed": len(DEFAULT_TRAINING),
        "history": len(review_examples(submissions)),
        "spam": model["label_counts"][SPAM],
        "legit": model["label_counts"][LEGIT],
        "accuracy": correct / max(1, len(examples)),
        "top_tokens": top_tokens[:8],
    }


class SimpleTextOpportunity:
    def __init__(self, text: str):
        self.text = text


def predict_text_with_model(model: dict, text: str) -> str:
    tokens = tokenize(text)
    scores = {}
    total_examples = len(model["examples"])
    for label in LABELS:
        score = math.log((model["label_counts"][label] + 1) / (total_examples + len(LABELS)))
        for token in tokens:
            score += token_log_probability(model, label, token)
        scores[label] = score
    return SPAM if scores[SPAM] >= scores[LEGIT] else LEGIT


def review_flags(opportunity: Opportunity, opportunities: list[Opportunity], submissions: list[dict]) -> list[dict]:
    spam = predict_spam(opportunity, submissions)
    flags = []
    if any(normalize(existing.title) == normalize(opportunity.title) for existing in opportunities):
        flags.append(("BLOCKER", "Duplicate title", "A live opportunity already uses this title."))
    if days_until(opportunity.deadline) < 0:
        flags.append(("BLOCKER", "Closed deadline", "The deadline has already passed."))
    elif days_until(opportunity.deadline) < 7:
        flags.append(("WARNING", "Very close deadline", "Students may not have enough time to apply."))
    if not opportunity.url.lower().startswith(("http://", "https://")):
        flags.append(("WARNING", "URL format", "The link should start with http:// or https://."))
    if opportunity.cost == "paid" and not opportunity.beginner_friendly:
        flags.append(("WARNING", "Access friction", "Paid and not beginner-friendly may narrow access."))
    if spam["risk"] == "HIGH":
        flags.append(("BLOCKER", "ML spam risk", "Spam risk " + str(round(spam["probability"] * 100)) + "%; signals: " + ", ".join(spam["signals"])))
    elif spam["risk"] == "MEDIUM":
        flags.append(("WARNING", "ML spam risk", "Spam risk " + str(round(spam["probability"] * 100)) + "%"))
    return [{"severity": severity, "label": label, "detail": detail} for severity, label, detail in flags]


def skill_weight(career: str, skill: str) -> float:
    wanted = normalize(skill)
    for label, weight in CAREER_PATHS[career].items():
        if normalize(label) == wanted:
            return weight
    return 0.0


def weighted_coverage(career: str, skills: list[str]) -> float:
    weights = CAREER_PATHS[career]
    total = sum(weights.values())
    seen = {normalize(skill) for skill in skills}
    covered = sum(weight for skill, weight in weights.items() if normalize(skill) in seen)
    return covered / total if total else 0


def readiness_score(career: str, skills: list[str], evidence: float = 0) -> float:
    raw = weighted_coverage(career, skills) * 4.2 + evidence - 2.1
    return 1 / (1 + math.exp(-raw)) * 100


def opportunity_relevance(career: str, opportunity: Opportunity) -> float:
    return weighted_coverage(career, opportunity.interests)


def career_impact(career: str, student: Student, opportunity: Opportunity) -> dict:
    before = readiness_score(career, student.interests)
    relevance = opportunity_relevance(career, opportunity)
    multiplier = TYPE_MULTIPLIERS.get(opportunity.type, 0.95)
    gain = min(0.35, relevance * multiplier * 0.25 + (0.03 if opportunity.beginner_friendly else 0))
    penalty = 0 if relevance >= 0.12 else 0.08 + (0.05 if opportunity.cost == "paid" else 0)
    merged = list(dict.fromkeys(student.interests + opportunity.interests))
    after = readiness_score(career, merged, gain - penalty)
    delta = after - before
    return {
        "before": before,
        "after": after,
        "delta": delta,
        "label": "INCREASE" if delta >= 1 else "DECREASE" if delta <= -1 else "NO CHANGE",
        "relevance": relevance,
    }


def rank_career_impacts(career: str, student: Student, opportunities: list[Opportunity]) -> list[dict]:
    rows = []
    for opportunity in opportunities:
        if is_open_to(opportunity, student):
            rows.append({"opportunity": opportunity, **career_impact(career, student, opportunity)})
    rows.sort(key=lambda row: row["delta"], reverse=True)
    return rows[:8]


def starting_line(student: Student, opportunities: list[Opportunity]) -> list[dict]:
    eligible = [opportunity for opportunity in opportunities if is_open_to(opportunity, student)]
    networks = [
        ("Outside network", 0.28),
        ("Average school channels", 0.55),
        ("Connected network", 0.76),
        ("Opportunity Radar", 1.00),
    ]
    rows = []
    for label, reach in networks:
        visible = round(len(eligible) * reach)
        rows.append({"network": label, "visible": visible, "hidden": max(0, len(eligible) - visible)})
    return rows


def fairness_audit(opportunities: list[Opportunity]) -> dict:
    sample = [
        Student("sample", level, [interest])
        for level in ["Secondary", "JC", "Poly", "University"]
        for interest in ["coding", "AI", "cybersecurity", "design", "research", "math"]
    ]
    neutral = []
    weighted = []
    for student in sample:
        eligible = [opportunity for opportunity in opportunities if is_open_to(opportunity, student)]
        if not eligible:
            continue
        neutral_ranked = sorted(
            eligible,
            key=lambda opportunity: score_opportunity(opportunity, student)["breakdown"]["interest_score"]
            + score_opportunity(opportunity, student)["breakdown"]["urgency_score"],
            reverse=True,
        )
        weighted_ranked = [row["opportunity"] for row in sorted(
            [score_opportunity(opportunity, student) for opportunity in eligible],
            key=lambda row: row["score"],
            reverse=True,
        )]
        neutral.append(sum(1 for opportunity in neutral_ranked[:5] if opportunity.cost == "free") / min(5, len(neutral_ranked)))
        weighted.append(sum(1 for opportunity in weighted_ranked[:5] if opportunity.cost == "free") / min(5, len(weighted_ranked)))
    neutral_avg = sum(neutral) / max(1, len(neutral))
    weighted_avg = sum(weighted) / max(1, len(weighted))
    return {"students": len(weighted), "neutral": neutral_avg, "weighted": weighted_avg, "lift": weighted_avg - neutral_avg}


def graph_rank(opportunities: list[Opportunity], student: Student, career: str | None = None) -> list[dict]:
    graph: dict[str, dict[str, float]] = {}

    def add(a: str, b: str, weight: float) -> None:
        graph.setdefault(a, {})[b] = graph.setdefault(a, {}).get(b, 0) + weight
        graph.setdefault(b, {})[a] = graph.setdefault(b, {}).get(a, 0) + weight

    for opportunity in opportunities:
        opp_node = "opp:" + opportunity.id
        graph.setdefault(opp_node, {})
        for interest in opportunity.interests:
            add(opp_node, "interest:" + normalize(interest), 1.6)
        add(opp_node, "organizer:" + normalize(opportunity.organizer), 0.6)

    for career_name, skills in CAREER_PATHS.items():
        career_node = "career:" + normalize(career_name)
        graph.setdefault(career_node, {})
        for skill, weight in skills.items():
            add(career_node, "interest:" + normalize(skill), weight)

    restart = {"interest:" + normalize(interest): 1 for interest in student.interests}
    if career:
        restart["career:" + normalize(career)] = 2
    restart = {node: weight for node, weight in restart.items() if node in graph}
    if not restart:
        return []
    total = sum(restart.values())
    restart = {node: weight / total for node, weight in restart.items()}
    scores = {node: restart.get(node, 0) for node in graph}

    for _ in range(35):
        new_scores = {node: 0.15 * restart.get(node, 0) for node in graph}
        for node, neighbors in graph.items():
            if not neighbors:
                continue
            total_weight = sum(neighbors.values())
            for neighbor, weight in neighbors.items():
                new_scores[neighbor] = new_scores.get(neighbor, 0) + 0.85 * scores.get(node, 0) * weight / total_weight
        scores = new_scores

    starts = ["career:" + normalize(career)] if career else list(restart)
    rows = []
    for opportunity in opportunities:
        if not is_open_to(opportunity, student):
            continue
        opp_node = "opp:" + opportunity.id
        path = shortest_path(graph, starts, opp_node)
        if not path:
            continue
        rows.append({
            "opportunity": opportunity,
            "score": scores.get(opp_node, 0),
            "path": path_text(path, opportunities),
            "direct": len(set(map(normalize, student.interests)) & set(map(normalize, opportunity.interests))),
        })
    rows.sort(key=lambda row: row["score"], reverse=True)
    return rows[:6]


def shortest_path(graph: dict, starts: list[str], target: str) -> list[str]:
    queue = [[start] for start in starts if start in graph]
    seen = set(starts)
    while queue:
        path = queue.pop(0)
        current = path[-1]
        if current == target:
            return path
        if len(path) > 4:
            continue
        for neighbor in graph.get(current, {}):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(path + [neighbor])
    return []


def path_text(path: list[str], opportunities: list[Opportunity]) -> str:
    by_id = {opportunity.id: opportunity.title for opportunity in opportunities}
    labels = []
    for node in path:
        kind, value = node.split(":", 1)
        labels.append(by_id.get(value, value) if kind == "opp" else value)
    return " -> ".join(labels)


STAGE_DEPS = {"foundation": set(), "practice": {"foundation"}, "proof": {"practice"}, "launch": {"proof"}}
STAGE_TYPES = {
    "foundation": ["workshop", "programme", "volunteering"],
    "practice": ["competition", "hackathon", "olympiad"],
    "proof": ["research", "internship"],
    "launch": ["scholarship", "programme", "internship"],
}


def career_pathway(career: str, student: Student, opportunities: list[Opportunity]) -> dict:
    try:
        stages = list(TopologicalSorter(STAGE_DEPS).static_order())
    except CycleError as error:
        raise ValueError("career pathway cycle") from error
    used = set()
    steps = []
    for stage in stages:
        candidates = []
        for opportunity in opportunities:
            if opportunity.id in used or not is_open_to(opportunity, student):
                continue
            score = opportunity_relevance(career, opportunity)
            score += 0.35 if opportunity.type in STAGE_TYPES[stage] else 0
            score += 0.18 if stage == "foundation" and opportunity.beginner_friendly else 0
            score += 0.05 if opportunity.cost == "free" else 0
            if score > 0:
                candidates.append((score, opportunity))
        candidates.sort(key=lambda item: item[0], reverse=True)
        chosen = candidates[0][1] if candidates else None
        if chosen:
            used.add(chosen.id)
        steps.append({"stage": stage.title(), "types": STAGE_TYPES[stage], "opportunity": chosen})
    missing = [
        skill for skill in CAREER_PATHS[career]
        if normalize(skill) not in {normalize(interest) for interest in student.interests}
    ][:5]
    return {"career": career, "readiness": readiness_score(career, student.interests), "missing": missing, "steps": steps}


def search_opportunities(opportunities: list[Opportunity], query: str, force_fallback: bool = False) -> list[dict]:
    tokens = tokenize(query)
    if not tokens:
        return []
    if not force_fallback:
        try:
            connection = sqlite3.connect(":memory:")
            connection.execute("CREATE VIRTUAL TABLE opps USING fts5(opp_id, body)")
            by_id = {opportunity.id: opportunity for opportunity in opportunities}
            for opportunity in opportunities:
                connection.execute("INSERT INTO opps VALUES (?, ?)", (opportunity.id, opportunity_text(opportunity)))
            rows = connection.execute(
                "SELECT opp_id, bm25(opps) AS rank FROM opps WHERE opps MATCH ? ORDER BY rank LIMIT 8",
                (" ".join(tokens),),
            ).fetchall()
            connection.close()
            return [{"opportunity": by_id[opp_id], "score": -rank, "engine": "SQLite FTS5"} for opp_id, rank in rows]
        except sqlite3.Error:
            pass

    docs = []
    df = {}
    for opportunity in opportunities:
        doc_tokens = tokenize(opportunity_text(opportunity))
        counts = {}
        for token in doc_tokens:
            counts[token] = counts.get(token, 0) + 1
        for token in counts:
            df[token] = df.get(token, 0) + 1
        docs.append((opportunity, counts, max(1, len(doc_tokens))))
    results = []
    for opportunity, counts, length in docs:
        score = 0.0
        for token in tokens:
            tf = counts.get(token, 0) / length
            idf = math.log((len(docs) + 1) / (df.get(token, 0) + 1)) + 1
            score += tf * idf
        if score > 0:
            results.append({"opportunity": opportunity, "score": score, "engine": "Python TF-IDF"})
    results.sort(key=lambda row: row["score"], reverse=True)
    return results[:8]
