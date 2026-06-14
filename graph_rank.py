"""GraphRank hidden opportunity discovery for Opportunity Radar.

This module builds a small typed graph of interests, careers, organizers, and
opportunities, then runs a personalized PageRank-style algorithm to surface
bridge opportunities that keyword matching alone can miss.
"""

import career_model
import matcher


DAMPING = 0.85


def normalize(value):
    """Return a stable lower-case graph key."""
    return value.strip().lower()


def node(kind, key):
    """Return a typed graph node."""
    return kind + ":" + normalize(key)


def add_edge(graph, first, second, weight=1.0):
    """Add a weighted undirected edge."""
    if first not in graph:
        graph[first] = {}
    if second not in graph:
        graph[second] = {}

    graph[first][second] = graph[first].get(second, 0.0) + weight
    graph[second][first] = graph[second].get(first, 0.0) + weight


def opportunity_node(opportunity):
    """Return the node id for an opportunity."""
    return node("opportunity", opportunity.id)


def build_graph(opportunities):
    """Build the Opportunity Radar discovery graph."""
    graph = {}

    for opportunity in opportunities:
        opp_node = opportunity_node(opportunity)
        graph.setdefault(opp_node, {})

        for interest in opportunity.interests:
            add_edge(graph, opp_node, node("interest", interest), 1.6)

        add_edge(graph, opp_node, node("organizer", opportunity.organizer), 0.6)
        add_edge(graph, opp_node, node("type", opportunity.type), 0.4)

    for career_name, skills in career_model.CAREER_PATHS.items():
        career_node = node("career", career_name)
        graph.setdefault(career_node, {})
        for skill, weight in skills.items():
            add_edge(graph, career_node, node("interest", skill), weight)

    return graph


def normalize_weights(weights):
    """Return weights normalized to sum to 1 across existing positive entries."""
    total = 0.0
    normalized = {}

    for key, value in weights.items():
        if value > 0:
            normalized[key] = value
            total = total + value

    if total == 0:
        return normalized

    for key in normalized:
        normalized[key] = normalized[key] / total

    return normalized


def personalization(graph, student, career_name=None):
    """Return personalized restart weights for PageRank."""
    weights = {}

    for interest in student.interests:
        interest_node = node("interest", interest)
        if interest_node in graph:
            weights[interest_node] = weights.get(interest_node, 0.0) + 1.0

    if career_name is not None:
        career_node = node("career", career_name)
        if career_node in graph:
            weights[career_node] = weights.get(career_node, 0.0) + 2.0

    if len(weights) == 0:
        for graph_node in graph:
            weights[graph_node] = 1.0

    return normalize_weights(weights)


def personalized_pagerank(graph, restart_weights, iterations=35, damping=DAMPING):
    """Run weighted personalized PageRank over the graph."""
    if len(graph) == 0:
        return {}

    scores = {}
    for graph_node in graph:
        scores[graph_node] = restart_weights.get(graph_node, 0.0)

    if sum(scores.values()) == 0:
        equal = 1.0 / len(graph)
        for graph_node in graph:
            scores[graph_node] = equal

    for _ in range(iterations):
        next_scores = {}
        for graph_node in graph:
            next_scores[graph_node] = (1 - damping) * restart_weights.get(
                graph_node,
                0.0,
            )

        dangling = 0.0
        for graph_node, neighbors in graph.items():
            if len(neighbors) == 0:
                dangling = dangling + scores.get(graph_node, 0.0)
                continue

            total_weight = sum(neighbors.values())
            if total_weight == 0:
                continue

            for neighbor, weight in neighbors.items():
                next_scores[neighbor] = next_scores.get(neighbor, 0.0) + (
                    damping * scores.get(graph_node, 0.0) * weight / total_weight
                )

        if dangling > 0:
            for graph_node, restart_weight in restart_weights.items():
                next_scores[graph_node] = next_scores.get(graph_node, 0.0) + (
                    damping * dangling * restart_weight
                )

        scores = next_scores

    return scores


def display_node(graph_node, opportunities_by_id):
    """Return a readable label for a graph node."""
    kind, key = graph_node.split(":", 1)
    if kind == "opportunity":
        opportunity = opportunities_by_id.get(key)
        if opportunity is not None:
            return opportunity.title
    return key


def shortest_path(graph, starts, target, max_depth=4):
    """Return a short path from any start node to target, or an empty list."""
    queue = []
    seen = set()

    for start in starts:
        if start in graph:
            queue.append([start])
            seen.add(start)

    while len(queue) > 0:
        path = queue.pop(0)
        current = path[-1]

        if current == target:
            return path

        if len(path) > max_depth:
            continue

        for neighbor in graph.get(current, {}):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(path + [neighbor])

    return []


def bridge_path_text(path, opportunities):
    """Return a readable graph path explanation."""
    opportunities_by_id = {}
    for opportunity in opportunities:
        opportunities_by_id[normalize(opportunity.id)] = opportunity

    labels = []
    for graph_node in path:
        labels.append(display_node(graph_node, opportunities_by_id))

    return " -> ".join(labels)


def rank_hidden_opportunities(opportunities, student, career_name=None, limit=5,
                              today=None):
    """Return graph-ranked hidden bridge opportunities for a student."""
    graph = build_graph(opportunities)
    restart_weights = personalization(graph, student, career_name)
    scores = personalized_pagerank(graph, restart_weights)
    starts = list(restart_weights.keys())
    path_starts = starts
    if career_name is not None:
        career_start = node("career", career_name)
        if career_start in graph:
            path_starts = [career_start]

    rows = []
    for opportunity in opportunities:
        if not matcher.is_eligible_and_open(opportunity, student, today):
            continue

        opp_node = opportunity_node(opportunity)
        shared = matcher.find_shared_interests(student, opportunity)
        relevance = 0.0
        if career_name is not None:
            relevance = career_model.opportunity_relevance(career_name, opportunity)

        if len(shared) > 1 and relevance < 0.20:
            continue

        path = shortest_path(graph, path_starts, opp_node)
        if len(path) == 0:
            continue

        hidden_bonus = 1 + max(0, 2 - len(shared)) * 0.35
        hidden_score = (scores.get(opp_node, 0.0) * hidden_bonus) + (
            relevance * 0.03
        )

        rows.append({
            "opportunity": opportunity,
            "graph_score": scores.get(opp_node, 0.0),
            "hidden_score": hidden_score,
            "shared_interests": shared,
            "career_relevance": relevance,
            "path": path,
            "path_text": bridge_path_text(path, opportunities),
        })

    rows.sort(
        key=lambda row: (
            row["hidden_score"],
            row["career_relevance"],
            -len(row["shared_interests"]),
        ),
        reverse=True,
    )
    return rows[:limit]
