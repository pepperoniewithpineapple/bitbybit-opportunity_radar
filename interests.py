"""Recursive interest taxonomy for Opportunity Radar."""

import json
import os


def load_interest_tree(path):
    """Load the interest taxonomy tree from a JSON file and return it as a dict."""
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def expand_interest(tree, name):
    """Recursively expand a named node into all its leaf interests.

    This function is RECURSIVE. When a node has child nodes, it calls itself
    on each child to collect all leaf interests at any depth. This is necessary
    because the interest tree can be arbitrarily deep — for example:
      Technology > coding > competitive programming
    A flat loop would only find one level; recursion handles every depth.

    Returns a list of leaf interest name strings found under the named node.
    Returns an empty list if the name is not found anywhere in the tree.
    """
    if name in tree:
        subtree = tree[name]
        if len(subtree) == 0:
            # Leaf node — return just this interest name as a single-element list.
            return [name]
        # Interior node — recurse into every child and collect all their leaves.
        result = []
        for child_name in subtree:
            result = result + expand_interest(subtree, child_name)
        return result

    # Not found at this level — search inside each subtree deeper.
    for key in tree:
        subtree = tree[key]
        if len(subtree) > 0:
            found = expand_interest(subtree, name)
            if len(found) > 0:
                return found

    return []


def get_expanded_interests(tree, raw_interests):
    """Return a deduplicated list of leaf interests expanded from raw_interests.

    For each interest in raw_interests, try to expand it through the tree.
    If the interest is a node in the tree, all its leaf descendants are added.
    If it is not in the tree, it is kept as-is (user-defined free-text interest).
    Duplicates are removed while preserving order.
    """
    seen = set()
    expanded = []

    for raw in raw_interests:
        leaves = expand_interest(tree, raw.strip())
        if len(leaves) == 0:
            # Not in tree — treat the raw interest as a leaf itself.
            leaves = [raw.strip()]
        for leaf in leaves:
            key = leaf.strip().lower()
            if key not in seen:
                seen.add(key)
                expanded.append(leaf)

    return expanded
