"""Trainable spam-risk model for sender submissions.

This is a small Multinomial Naive Bayes classifier built with the Python
standard library. It learns from labeled text examples, then estimates whether
a submitted opportunity looks legitimate or spammy before manual review.
"""

import math
import re


SPAM = "spam"
LEGIT = "legit"
LABELS = [SPAM, LEGIT]

HIGH_RISK_THRESHOLD = 0.78
MEDIUM_RISK_THRESHOLD = 0.55

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
REJECTION_SPAM_TERMS = ["spam", "scam", "prize", "click", "crypto"]

DEFAULT_TRAINING_EXAMPLES = [
    {
        "label": LEGIT,
        "text": "JC AI for public good sprint school innovation lab workshop coding AI free beginner friendly application official information",
    },
    {
        "label": LEGIT,
        "text": "National cybersecurity olympiad competition students official registration deadline coding security learning challenge",
    },
    {
        "label": LEGIT,
        "text": "Research attachment programme university lab science mentorship application professor official student opportunity",
    },
    {
        "label": LEGIT,
        "text": "Scholarship briefing financial aid information session school careers office free eligible students apply official",
    },
    {
        "label": LEGIT,
        "text": "Robotics workshop beginner friendly hands on polytechnic engineering students free registration official",
    },
    {
        "label": LEGIT,
        "text": "Volunteering programme community service youth leadership public good nonprofit sign up official",
    },
    {
        "label": LEGIT,
        "text": "Data science bootcamp weekend workshop python statistics machine learning students limited seats official",
    },
    {
        "label": SPAM,
        "text": "guaranteed scholarship prize win money fast click now limited offer crypto rewards whatsapp telegram",
    },
    {
        "label": SPAM,
        "text": "earn cash from home no experience urgent sign up today referral bonus lucky draw winner",
    },
    {
        "label": SPAM,
        "text": "free iphone giveaway claim prize now suspicious link bit ly tinyurl winners only",
    },
    {
        "label": SPAM,
        "text": "investment opportunity double your money crypto trading secret formula guaranteed profit",
    },
    {
        "label": SPAM,
        "text": "paid certificate instant approval no application no deadline exclusive deal limited time",
    },
    {
        "label": SPAM,
        "text": "miracle admission guaranteed top university pay deposit today agent contact whatsapp",
    },
    {
        "label": SPAM,
        "text": "urgent winner selected click link claim cash bonus promotional prize now",
    },
]


def tokenize(text):
    """Return lower-case tokens for Naive Bayes training and prediction."""
    if text is None:
        return []

    tokens = []
    for token in TOKEN_PATTERN.findall(text.lower()):
        if len(token) > 1 and not token.isdigit():
            tokens.append(token)
    return tokens


def opportunity_text(opportunity):
    """Build the classifier text for one Opportunity-like object."""
    fields = [
        opportunity.title,
        opportunity.organizer,
        opportunity.type,
        opportunity.cost,
        "beginner friendly" if opportunity.beginner_friendly else "not beginner friendly",
        opportunity.deadline,
        opportunity.url,
    ]
    fields.extend(opportunity.interests)
    fields.extend(opportunity.eligible_levels)
    return " ".join(fields)


def train(examples):
    """Train a Naive Bayes model from labeled examples."""
    label_counts = {}
    token_counts = {}
    total_tokens = {}
    vocabulary = set()

    for label in LABELS:
        label_counts[label] = 0
        token_counts[label] = {}
        total_tokens[label] = 0

    for example in examples:
        label = example["label"]
        if label not in LABELS:
            raise ValueError("unknown training label: " + str(label))

        tokens = tokenize(example["text"])
        if len(tokens) == 0:
            continue

        label_counts[label] = label_counts[label] + 1
        for token in tokens:
            vocabulary.add(token)
            token_counts[label][token] = token_counts[label].get(token, 0) + 1
            total_tokens[label] = total_tokens[label] + 1

    for label in LABELS:
        if label_counts[label] == 0:
            raise ValueError("training data must include " + label + " examples")

    return {
        "labels": list(LABELS),
        "label_counts": label_counts,
        "token_counts": token_counts,
        "total_tokens": total_tokens,
        "vocabulary": sorted(vocabulary),
        "example_count": sum(label_counts.values()),
    }


def train_default_model():
    """Train and return the built-in spam model."""
    return train(DEFAULT_TRAINING_EXAMPLES)


def review_history_examples(submissions):
    """Return labeled examples learned from reviewer decisions."""
    examples = []

    for submission in submissions:
        status = submission.get("status", "")
        opportunity = submission.get("opportunity")
        if opportunity is None:
            continue

        if status == "approved":
            examples.append({
                "label": LEGIT,
                "text": opportunity_text(opportunity),
            })
            continue

        if status == "rejected":
            note = submission.get("review_note", "")
            note_tokens = set(tokenize(note))
            should_learn_spam = False
            for term in REJECTION_SPAM_TERMS:
                if term in note_tokens:
                    should_learn_spam = True
                    break

            if should_learn_spam:
                examples.append({
                    "label": SPAM,
                    "text": opportunity_text(opportunity) + " " + note,
                })

    return examples


def combined_training_examples(submissions):
    """Return seed examples plus reviewer-history examples."""
    return list(DEFAULT_TRAINING_EXAMPLES) + review_history_examples(submissions)


def train_adaptive_model(submissions):
    """Train a spam model from seed examples and reviewer history."""
    return train(combined_training_examples(submissions))


def token_log_probability(model, label, token):
    """Return smoothed log P(token | label)."""
    vocabulary_size = max(1, len(model["vocabulary"]))
    token_count = model["token_counts"][label].get(token, 0)
    denominator = model["total_tokens"][label] + vocabulary_size
    return math.log((token_count + 1) / denominator)


def label_log_prior(model, label):
    """Return smoothed log P(label)."""
    label_count = model["label_counts"][label]
    total_examples = model["example_count"]
    return math.log((label_count + 1) / (total_examples + len(LABELS)))


def predict_text(model, text):
    """Predict spam risk for free text."""
    tokens = tokenize(text)
    log_scores = {}

    for label in LABELS:
        score = label_log_prior(model, label)
        for token in tokens:
            score = score + token_log_probability(model, label, token)
        log_scores[label] = score

    max_score = max(log_scores.values())
    exp_scores = {}
    total = 0.0
    for label in LABELS:
        exp_score = math.exp(log_scores[label] - max_score)
        exp_scores[label] = exp_score
        total = total + exp_score

    spam_probability = exp_scores[SPAM] / total
    legit_probability = exp_scores[LEGIT] / total
    if spam_probability >= legit_probability:
        predicted_label = SPAM
    else:
        predicted_label = LEGIT

    return {
        "predicted_label": predicted_label,
        "spam_probability": spam_probability,
        "legit_probability": legit_probability,
        "risk_level": risk_level(spam_probability),
        "tokens": tokens,
    }


def predict_opportunity(model, opportunity):
    """Predict spam risk for an Opportunity-like object."""
    return predict_text(model, opportunity_text(opportunity))


def risk_level(spam_probability):
    """Return LOW, MEDIUM, or HIGH from a spam probability."""
    if spam_probability >= HIGH_RISK_THRESHOLD:
        return "HIGH"
    if spam_probability >= MEDIUM_RISK_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def spam_signal_tokens(model, text, limit=5):
    """Return tokens that most strongly push the prediction toward spam."""
    seen = set()
    signals = []

    for token in tokenize(text):
        if token in seen:
            continue
        seen.add(token)

        spam_log = token_log_probability(model, SPAM, token)
        legit_log = token_log_probability(model, LEGIT, token)
        weight = spam_log - legit_log
        if weight > 0:
            signals.append({
                "token": token,
                "weight": weight,
            })

    signals.sort(key=lambda signal: signal["weight"], reverse=True)
    return signals[:limit]


def assess_opportunity(opportunity, model=None):
    """Return a full spam-risk assessment for one opportunity."""
    if model is None:
        model = train_default_model()

    text = opportunity_text(opportunity)
    prediction = predict_text(model, text)
    signals = spam_signal_tokens(model, text)

    return {
        "predicted_label": prediction["predicted_label"],
        "spam_probability": prediction["spam_probability"],
        "legit_probability": prediction["legit_probability"],
        "risk_level": prediction["risk_level"],
        "signals": signals,
        "training_examples": model["example_count"],
    }


def top_spam_tokens(model, limit=8):
    """Return tokens with the strongest learned spam-vs-legit weight."""
    signals = []

    for token in model["vocabulary"]:
        spam_log = token_log_probability(model, SPAM, token)
        legit_log = token_log_probability(model, LEGIT, token)
        weight = spam_log - legit_log
        if weight > 0:
            signals.append({
                "token": token,
                "weight": weight,
            })

    signals.sort(key=lambda signal: signal["weight"], reverse=True)
    return signals[:limit]


def model_health(submissions):
    """Return a training audit for the adaptive spam model."""
    history_examples = review_history_examples(submissions)
    examples = combined_training_examples(submissions)
    model = train(examples)

    spam_count = 0
    legit_count = 0
    for example in examples:
        if example["label"] == SPAM:
            spam_count = spam_count + 1
        if example["label"] == LEGIT:
            legit_count = legit_count + 1

    return {
        "model": model,
        "seed_examples": len(DEFAULT_TRAINING_EXAMPLES),
        "history_examples": len(history_examples),
        "total_examples": len(examples),
        "spam_examples": spam_count,
        "legit_examples": legit_count,
        "leave_one_out_accuracy": leave_one_out_accuracy(examples),
        "top_spam_tokens": top_spam_tokens(model),
    }


def leave_one_out_accuracy(examples):
    """Return leave-one-out accuracy for the labeled training examples."""
    if len(examples) < 2:
        return 0.0

    correct = 0
    total = 0

    for index, held_out in enumerate(examples):
        training = examples[:index] + examples[index + 1:]
        model = train(training)
        prediction = predict_text(model, held_out["text"])
        if prediction["predicted_label"] == held_out["label"]:
            correct = correct + 1
        total = total + 1

    return correct / total
