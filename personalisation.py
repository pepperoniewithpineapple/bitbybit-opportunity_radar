import os
import threading
from queue import Queue

from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

import models
import storage


load_dotenv()


SYSTEM_INSTRUCTIONS = """\
Task: Maintain a dense, clinical, 3-4 sentence narrative preference summary of the student's profile.

STRICT RULES:
1. Do not speak to the user. No 'Hello' or 'Sure'. Pure output not conversational.
2. Output only raw 3-4 sentences of the summary text. No markdown or any kind of formatting.
3. Incorporate new event logs into background summary by identifying shifting technical trajectories (e.g., specific libraries, fields, or constraints).
4. If event logs state the user explicitly dislikes or skipped something, mention what they avoid."""


personalisation_engine = ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.15
)


class InterestMatcher:
    def __init__(self):
        self.vectoriser = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self.is_trained = False

    def train_vocabulary(self, opportunities: list[models.Opportunity]) -> None:
        """
        Trains the vectorizer vocabulary on all unique interest strings from the scraped data

        Args:
            opportunities (list[models.Opportunity]): list of opps to extract vocabular from
        """
        vocab = [str(opp) for opp in opportunities]
        self.vectoriser.fit(vocab)
        self.is_trained = True

    def score_opportunities(self, opportunities: list[models.Opportunity]) -> list[models.Opportunity]:
        """
        Scores each opportunity using the LLM's response and TF-IDF vectorising

        Args:
            opportunities (list[models.Opportunity]): All opportunities

        Returns:
            list[models.Opportunity]: list of opportunities sorted by personalised score
        """
        if not self.is_trained:
            self.train_vocabulary(opportunities)

        student: models.Student = storage.load_student()
        student_profile: str = student.personalisation_profile

        student_vector = self.vectoriser.transform([student_profile])
        opportunities_text = [str(opp) for opp in opportunities]
        opportunities_matrix = self.vectoriser.transform(opportunities_text)

        scores = cosine_similarity(X=student_vector, Y=opportunities_matrix)[0]

        for opportunity, score in zip(opportunities, scores):
            opportunity.personalisation_score = score

        return sorted(opportunities, key=lambda x: x.personalisation_score, reverse=True)


interest_matcher = InterestMatcher()


class InteractionManager:
    def __init__(self) -> None:
        self.batch_buildups = {
            "apply|view": 0,
            "search": 0,
            "profile": 0
        }
        self.MAX_BATCH_SIZES = {
            "apply|view": 3,
            "search": 2,
            "profile": 1
        }
        self.batch_payloads = {
            "apply|view": "",
            "search": "",
            "profile": ""
        }
        self._queue = Queue()
        self._worker = threading.Thread(target=self._queue_manager, daemon=True)
        self._worker.start()

    def _queue_manager(self) -> None:
        while True:
            message = self._queue.get()
            self.send_batched_payload(message)
            self._queue.task_done()


    def _check_batch(self, type_key: Literal["apply|view", "search", "profile"]) -> bool:
        """
        Check if batch threshold reached for a specific type
        """
        return self.batch_buildups[type_key] >= self.MAX_BATCH_SIZES[type_key]
            
    def _increment_batch(self, type_key: Literal["apply|view", "search", "profile"]) -> None:
        """
        Increment batch counter for a specific type
        """
        self.batch_buildups[type_key] += 1

    def _reset_batch(self, type_key: Literal["apply|view", "search", "profile"]) -> None:
        self.batch_payloads[type_key] = ""
        self.batch_buildups[type_key] = 0

    def _append_payload(self, type_key: Literal["apply|view", "search", "profile"], content: str) -> None:
        self._increment_batch(type_key)
        self.batch_payloads[type_key] += content
        if self._check_batch(type_key):
            self._queue.put(type_key)

    def log_apply(self, opportunity: models.Opportunity) -> None:
        """ User clicked "I'm Applying! """
        self._append_payload(
            type_key="apply|view",
            content=(
                ("\n\n" if self.batch_payloads["apply|view"] else "") + 
                "[EVENT] APPLYING for Opportunity"
                f"\nOpportunity: {opportunity.title}"
                f"\nInterests: {', '.join(opportunity.interests)}"
                f"\nEligible Levels: {', '.join(opportunity.eligible_levels)}"
                f"\nBeginner Friendly: {opportunity.beginner_friendly}"
            )
        )
        
    def log_view(self, opportunity: models.Opportunity) -> None:
        """ User clicked "View Details" """
        self._append_payload(
            type_key="apply|view",
            content=(
                ("\n\n" if self.batch_payloads["apply|view"] else "") + 
                "[EVENT] viewed Opportunity details"
                f"\nOpportunity: {opportunity.title}"
                f"\nInterests: {', '.join(opportunity.interests)}"
                f"\nEligible Levels: {', '.join(opportunity.eligible_levels)}"
                f"\nBeginner Friendly: {opportunity.beginner_friendly}"
            )
        )
        
    def log_search(self, query: str) -> None:
        """ User used the search bar """
        self._append_payload(
            type_key="search",
            content=(
                ("\n\n" if self.batch_payloads["search"] else "") + 
                "[EVENT] Search"
                f"\nQuery: {query}"
            )
        )
        
    def log_profile(self, student: models.Student) -> None:
        """ User updated their profile """
        self._append_payload(
            type_key="profile",
            content=(
                ("\n\n" if self.batch_payloads["profile"] else "") + 
                "[EVENT] Updated Profile"
                f"\nLevel: {student.level}"
                f"\nInterests: {', '.join(student.interests)}"
                f"\nCareer Goals: {', '.join(student.career_goals)}"
            )
        )
        
    def send_batched_payload(self, type_key: Literal["apply|view", "search", "profile"]) -> None:
        """ Send to LLM """
        print("Sending payload to LLM...") #  DEBUG
        message = self.batch_payloads[type_key]
        self._reset_batch(type_key)

        student: models.Student = storage.load_student()
        current_profile = student.personalisation_profile or "(No prior summary yet)"

        response: AIMessage = personalisation_engine.invoke([
            SystemMessage(content=SYSTEM_INSTRUCTIONS),
            HumanMessage(content=(
                f"Current Background Summary:\n{current_profile}"
                "\n\n"
                f"New Event Log Payload:\n{message}"
                "\n\n"
                "Updated Preference Summary:"
            ))
        ])

        student.personalisation_profile = response.content.strip()
        storage.save_student(student)
        