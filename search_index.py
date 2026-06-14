"""Optional generated opportunity search index.

JSON remains the source of truth. This module can build a temporary SQLite FTS5
index for fast search, then falls back to pure-Python TF-IDF if FTS5 is not
available in the local Python build.
"""

import math
import sqlite3

import spam_model


def opportunity_document(opportunity):
    """Return searchable text for one opportunity."""
    fields = [
        opportunity.title,
        opportunity.organizer,
        opportunity.type,
        opportunity.cost,
        opportunity.deadline,
        opportunity.url,
    ]
    fields.extend(opportunity.interests)
    fields.extend(opportunity.eligible_levels)
    return " ".join(fields)


def sqlite_fts_available():
    """Return True when SQLite FTS5 works in this Python runtime."""
    try:
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE VIRTUAL TABLE test_fts USING fts5(body)")
        connection.close()
        return True
    except sqlite3.Error:
        return False


def sanitized_query(query):
    """Return a conservative token query for FTS/TF-IDF."""
    return " ".join(spam_model.tokenize(query))


def sqlite_fts_search(opportunities, query, limit=5):
    """Search opportunities using an in-memory SQLite FTS5 index."""
    clean_query = sanitized_query(query)
    if clean_query == "":
        return []

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE opportunity_fts "
            "USING fts5(opp_id, title, organizer, body)"
        )

        by_id = {}
        for opportunity in opportunities:
            by_id[opportunity.id] = opportunity
            connection.execute(
                "INSERT INTO opportunity_fts(opp_id, title, organizer, body) "
                "VALUES (?, ?, ?, ?)",
                (
                    opportunity.id,
                    opportunity.title,
                    opportunity.organizer,
                    opportunity_document(opportunity),
                ),
            )

        rows = connection.execute(
            "SELECT opp_id, bm25(opportunity_fts) AS rank "
            "FROM opportunity_fts WHERE opportunity_fts MATCH ? "
            "ORDER BY rank LIMIT ?",
            (clean_query, limit),
        ).fetchall()

        results = []
        for opp_id, rank in rows:
            results.append({
                "opportunity": by_id[opp_id],
                "score": -rank,
                "engine": "sqlite-fts5",
            })
        return results
    finally:
        connection.close()


def build_tfidf_index(opportunities):
    """Build a small TF-IDF index in Python dictionaries."""
    documents = []
    document_frequency = {}

    for opportunity in opportunities:
        tokens = spam_model.tokenize(opportunity_document(opportunity))
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1

        documents.append({
            "opportunity": opportunity,
            "counts": counts,
            "length": max(1, len(tokens)),
        })

        for token in counts:
            document_frequency[token] = document_frequency.get(token, 0) + 1

    return {
        "documents": documents,
        "document_frequency": document_frequency,
        "document_count": len(documents),
    }


def inverse_document_frequency(index, token):
    """Return smoothed IDF for a token."""
    document_count = index["document_count"]
    frequency = index["document_frequency"].get(token, 0)
    return math.log((document_count + 1) / (frequency + 1)) + 1


def tfidf_search(opportunities, query, limit=5):
    """Search opportunities using pure-Python TF-IDF."""
    query_tokens = spam_model.tokenize(query)
    if len(query_tokens) == 0:
        return []

    index = build_tfidf_index(opportunities)
    results = []

    for document in index["documents"]:
        score = 0.0
        for token in query_tokens:
            term_frequency = document["counts"].get(token, 0) / document["length"]
            score = score + (
                term_frequency * inverse_document_frequency(index, token)
            )

        if score > 0:
            results.append({
                "opportunity": document["opportunity"],
                "score": score,
                "engine": "python-tfidf",
            })

    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:limit]


def search_opportunities(opportunities, query, limit=5, force_fallback=False):
    """Search with SQLite FTS5 when available, otherwise TF-IDF fallback."""
    if force_fallback or not sqlite_fts_available():
        return tfidf_search(opportunities, query, limit)

    try:
        return sqlite_fts_search(opportunities, query, limit)
    except sqlite3.Error:
        return tfidf_search(opportunities, query, limit)
