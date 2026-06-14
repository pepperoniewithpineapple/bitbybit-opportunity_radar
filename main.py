"""NiceGUI app for Opportunity Radar."""

from __future__ import annotations

from dataclasses import dataclass, field

from nicegui import ui

import core
import intelligence
from theme import (apply_theme, badge, stat_card, section_card, inner_card, page_container, primary_button, soft_button, danger_button, hero)


@dataclass
class RadarState:
    """Runtime state shared by the NiceGUI page."""

    opportunities: list[core.Opportunity] = field(default_factory=list)
    applications: list[core.Application] = field(default_factory=list)
    submissions: list[dict] = field(default_factory=list)
    student: core.Student | None = None
    last_results: list[dict] = field(default_factory=list)

    def reload(self) -> None:
        self.opportunities = core.load_opportunities()
        self.applications = core.load_applications()
        self.submissions = core.load_submissions()
        self.student = core.load_student()


STATE = RadarState()
STATE.reload()


def refresh_all() -> None:
    """Reload persisted state and refresh visible sections."""
    STATE.reload()
    metrics.refresh()
    profile_panel.refresh()
    applications_panel.refresh()
    equity_panel.refresh()
    career_panel.refresh()
    sender_panel.refresh()


def short(text: str, limit: int = 70) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def opportunity_card(result: dict, show_track: bool = True):
    opportunity = result["opportunity"]
    breakdown = result["breakdown"]
    days_left = result["days_left"]
    with ui.card().classes("opp-card"):
        with ui.row().classes("items-start justify-between gap-4 w-full"):
            with ui.column().classes("gap-1"):
                ui.label(opportunity.title).classes("text-lg font-semibold text-slate-950")
                ui.label(opportunity.organizer + " | " + opportunity.type).classes(
                    "text-sm text-slate-500"
                )
            with ui.row().classes("gap-2"):
                badge("score " + format(result["score"], ".3f"), "info")
                badge(str(days_left) + "d", "warn" if days_left < 7 else "good")
        ui.label(", ".join(opportunity.interests)).classes("text-sm text-slate-600")
        with ui.row().classes("gap-2"):
            badge(opportunity.cost, "good" if opportunity.cost == "free" else "warn")
            badge("beginner" if opportunity.beginner_friendly else "advanced", "good" if opportunity.beginner_friendly else "neutral")
            badge("open to " + ", ".join(opportunity.eligible_levels), "neutral")
        with ui.expansion("Transparent scoring").classes("w-full"):
            ui.markdown(
                f"""
                - Shared interests: **{', '.join(result['shared']) or 'none'}**
                - Interest score: **{breakdown['interest_score']:.3f}**
                - Urgency score: **{breakdown['urgency_score']:.3f}**
                - Access boost: **{breakdown['access_score']:.3f}**
                - Total: **{breakdown['total']:.3f}**
                """
            ).classes("text-sm")
        with ui.row().classes("gap-2"):
            ui.link("Open link", opportunity.url, new_tab=True).classes("soft-button")
            if show_track:
                primary_button("Track", icon="bookmark_add", on_click=lambda opp=opportunity: track_opportunity(opp))


def track_opportunity(opportunity: core.Opportunity) -> None:
    if core.add_application(STATE.applications, opportunity):
        ui.notify("Added to tracker", type="positive")
    else:
        ui.notify("Already tracked", type="warning")
    refresh_all()


@ui.refreshable
def metrics():
    stats = core.opportunity_stats(STATE.opportunities, STATE.student)
    pending = len(core.pending_submissions(STATE.submissions))
    demand = sum(core.demand_counts().values())
    with ui.row().classes("grid grid-cols-1 md:grid-cols-4 gap-4 w-full"):
        stat_card("Open opportunities", str(stats["open"]), "curated and approved")
        stat_card("Free access", str(stats["free"]), "no-cost opportunities")
        stat_card("Demand signals", str(demand), "anonymous student searches")
        stat_card("Pending review", str(pending), "sender submissions")


@ui.refreshable
def profile_panel():
    with section_card("Student profile"):
        student = STATE.student or core.demo_student()
        name = ui.input("Name", value=student.name).classes("w-full")
        level = ui.select(core.LEVELS, label="Level", value=student.level).classes("w-full")
        interests = ui.input(
            "Interests",
            value=", ".join(student.interests),
            placeholder="AI, coding, public good",
        ).classes("w-full")

        def save_profile() -> None:
            parsed = core.parse_interests(interests.value or "")
            if not name.value or not parsed:
                ui.notify("Please add a name and at least one interest.", type="warning")
                return
            core.save_student(core.Student(name.value.strip(), level.value, parsed))
            STATE.last_results = []
            ui.notify("Profile saved", type="positive")
            refresh_all()

        with ui.row().classes("gap-2"):
            primary_button("Save profile", icon="save", on_click=save_profile)
            soft_button(
                "Load demo",
                icon="auto_awesome",
                on_click=lambda: (core.save_student(core.demo_student()), ui.notify("Demo student loaded", type="positive"), refresh_all()),
            )


def render_results(container, results: list[dict]) -> None:
    container.clear()
    with container:
        if not results:
            ui.label("No matching open opportunities yet. Try broader filters.").classes("empty-state")
            return
        tips = core.suggest_interests(STATE.opportunities, STATE.student) if STATE.student else []
        if tips:
            ui.label("Try adding: " + ", ".join([tip[0] for tip in tips])).classes("text-sm text-slate-500")
        for result in results[:10]:
            opportunity_card(result)


def build_discover_tab():
    with ui.row().classes("items-stretch gap-5 w-full flex-wrap"):
        with ui.column().classes("side-panel"):
            profile_panel()
            with section_card("Filters"):
                cost = ui.select(["all", "free", "paid"], value="all", label="Cost").classes("w-full")
                opp_type = ui.select(["all"] + core.OPPORTUNITY_TYPES, value="all", label="Type").classes("w-full")
                keyword = ui.input("Keyword").classes("w-full")
                max_days = ui.number("Deadline within days", value=None, min=0).classes("w-full")
                sort = ui.select(["score", "deadline", "title"], value="score", label="Sort").classes("w-full")
                primary_button("Run discovery", icon="radar", on_click=lambda: run_search()).classes("w-full")
                soft_button("Closing this week", icon="timer", on_click=lambda: show_closing()).classes("w-full")

        results_area = ui.column().classes("content-panel")

    def run_search() -> None:
        if not STATE.student:
            ui.notify("Save or load a student profile first.", type="warning")
            return
        core.log_search(STATE.student)
        STATE.last_results = core.rank_opportunities(
            STATE.opportunities,
            STATE.student,
            cost=cost.value,
            opp_type=opp_type.value,
            keyword=keyword.value or "",
            max_days=int(max_days.value) if max_days.value is not None else None,
            sort=sort.value,
        )
        ui.notify("Anonymous demand signal saved", type="positive")
        render_results(results_area, STATE.last_results)
        metrics.refresh()

    def show_closing() -> None:
        if not STATE.student:
            ui.notify("Save or load a profile first.", type="warning")
            return
        closing = [
            {"opportunity": opportunity, **core.score_opportunity(opportunity, STATE.student)}
            for opportunity in core.closing_this_week(STATE.opportunities, STATE.student)
        ]
        render_results(results_area, closing)

    render_results(results_area, STATE.last_results)


@ui.refreshable
def applications_panel():
    with section_card("My applications and sharing"):
        if not STATE.applications:
            ui.label("No tracked applications yet. Add one from Discover.").classes("empty-state")
        by_id = {opportunity.id: opportunity for opportunity in STATE.opportunities}
        for application in STATE.applications:
            opportunity = by_id.get(application.opp_id)
            if not opportunity:
                continue
            with inner_card():
                ui.label(opportunity.title).classes("font-semibold text-slate-900")
                with ui.row().classes("gap-2 items-end"):
                    status = ui.select(
                        ["interested", "applying", "submitted", "accepted", "declined"],
                        value=application.status,
                        label="Status",
                    )
                    notes = ui.input("Notes", value=application.notes)
                    soft_button("Save", on_click=lambda app=application, s=status, n=notes: save_app(app, s.value, n.value))
                    danger_button("Remove", on_click=lambda app=application: remove_app(app))
        with ui.row().classes("gap-2"):
            soft_button("Export calendar", icon="event", on_click=export_calendar)
            soft_button("Write weekly digest", icon="article", on_click=write_digest)


def save_app(application: core.Application, status: str, notes: str) -> None:
    core.update_application(STATE.applications, application.opp_id, status, notes or "")
    ui.notify("Application updated", type="positive")
    refresh_all()


def remove_app(application: core.Application) -> None:
    core.remove_application(STATE.applications, application.opp_id)
    ui.notify("Removed from tracker", type="positive")
    refresh_all()


def export_calendar() -> None:
    path = core.export_calendar(STATE.applications, STATE.opportunities)
    ui.notify("Calendar written to " + str(path.name), type="positive")


def write_digest() -> None:
    if not STATE.student:
        ui.notify("Save or load a profile first.", type="warning")
        return
    results = STATE.last_results or core.rank_opportunities(STATE.opportunities, STATE.student)
    path = core.weekly_digest(results, STATE.student)
    ui.notify("Digest written to " + str(path.name), type="positive")


@ui.refreshable
def equity_panel():
    if not STATE.student:
        ui.label("Save or load a profile to see the equity views.").classes("empty-state")
        return
    with ui.grid(columns=2).classes("radar-grid-2 gap-5 w-full"):
        with section_card("Invisible starting line"):
            rows = intelligence.starting_line(STATE.student, STATE.opportunities)
            for row in rows:
                with ui.row().classes("justify-between w-full"):
                    ui.label(row["network"]).classes("text-slate-700")
                    ui.label(f"{row['visible']} visible | {row['hidden']} hidden").classes("font-semibold")
        with section_card("Bias self-audit"):
            audit = intelligence.fairness_audit(STATE.opportunities)
            ui.label(f"{audit['students']} synthetic students tested").classes("text-slate-500")
            ui.label(f"Neutral free share: {audit['neutral'] * 100:.1f}%")
            ui.label(f"Access-weighted free share: {audit['weighted'] * 100:.1f}%")
            ui.label(f"Measured lift: {audit['lift'] * 100:.1f} percentage points").classes("font-semibold text-emerald-700")
    with section_card("Opportunity-gap statistics"):
        stats = core.opportunity_stats(STATE.opportunities, STATE.student)
        with ui.row().classes("gap-2"):
            badge(f"{stats['open']} open", "info")
            badge(f"{stats['urgent']} urgent", "warn")
            badge(f"{stats['free']} free", "good")
        ui.label("Supply by interest").classes("mt-3 font-semibold")
        for interest, count in stats["supply"]:
            ui.linear_progress(min(count / 6, 1), show_value=False).props("instant-feedback").classes("w-full")
            ui.label(f"{interest}: {count}").classes("text-xs text-slate-500")


@ui.refreshable
def career_panel():
    if not STATE.student:
        ui.label("Save or load a profile to use career intelligence.").classes("empty-state")
        return
    career = ui.select(intelligence.career_names(), value="cybersecurity analyst", label="Career goal").classes("max-w-md")
    container = ui.column().classes("w-full gap-4")

    def render() -> None:
        container.clear()
        with container:
            ui.label("Career impact").classes("section-title")
            for row in intelligence.rank_career_impacts(career.value, STATE.student, STATE.opportunities)[:5]:
                with inner_card():
                    ui.label(row["opportunity"].title).classes("font-semibold")
                    badge(row["label"] + " " + format(row["delta"], "+.1f"), "good" if row["delta"] > 0 else "warn")
                    ui.label(f"Before {row['before']:.1f}/100 | After {row['after']:.1f}/100").classes("text-sm text-slate-500")
            ui.separator()
            ui.label("GraphRank hidden discovery").classes("section-title")
            for row in intelligence.graph_rank(STATE.opportunities, STATE.student, career.value)[:5]:
                with inner_card():
                    ui.label(row["opportunity"].title).classes("font-semibold")
                    ui.label(row["path"]).classes("text-sm text-slate-500")
            ui.separator()
            ui.label("Career pathway").classes("section-title")
            plan = intelligence.career_pathway(career.value, STATE.student, STATE.opportunities)
            ui.label(f"Starting readiness: {plan['readiness']:.1f}/100").classes("text-slate-600")
            ui.label("Top missing skills: " + (", ".join(plan["missing"]) or "none")).classes("text-slate-600")
            for step in plan["steps"]:
                opportunity = step["opportunity"]
                with inner_card():
                    ui.label(step["stage"]).classes("font-semibold text-slate-900")
                    ui.label(", ".join(step["types"])).classes("text-xs text-slate-500")
                    ui.label(opportunity.title if opportunity else "No live fit yet").classes("text-slate-700")

    primary_button("Build career intelligence view", icon="psychology", on_click=render)
    render()


def build_help_tab():
    with ui.grid(columns=2).classes("radar-grid-2 gap-5 w-full"):
        with section_card("First-timer guides"):
            for title, bullets in core.first_timer_guides().items():
                with ui.expansion(title.title()).classes("w-full"):
                    for bullet in bullets:
                        ui.label("- " + bullet).classes("text-sm text-slate-600")
        with section_card("Optional search index"):
            query = ui.input("Search opportunities").classes("w-full")
            result_box = ui.column().classes("w-full")

            def run_search() -> None:
                result_box.clear()
                with result_box:
                    for row in intelligence.search_opportunities(STATE.opportunities, query.value or ""):
                        ui.label(row["opportunity"].title + " | " + row["engine"]).classes("text-sm")

            soft_button("Search", icon="search", on_click=run_search)


@ui.refreshable
def sender_panel():
    counts = core.status_counts(STATE.submissions)
    with ui.row().classes("gap-2 mb-4"):
        badge(f"{counts['pending']} pending", "warn")
        badge(f"{counts['approved']} approved", "good")
        badge(f"{counts['rejected']} rejected", "bad")
    with ui.tabs().classes("clean-tabs").props("inline-label") as sender_tabs:
        gaps = ui.tab("Demand", icon="insights")
        submit = ui.tab("Submit", icon="post_add")
        review = ui.tab("Review", icon="rule")
        live = ui.tab("Live", icon="campaign")
        diagnostics = ui.tab("Diagnostics", icon="monitoring")
    with ui.tab_panels(sender_tabs, value=gaps).classes("w-full bg-transparent").props(
        'transition-prev="fade" transition-next="fade" transition-duration="300"'
    ):
        with ui.tab_panel(gaps):
            with section_card("Demand gap radar"):
                for row in core.gap_rows(STATE.opportunities):
                    with ui.row().classes("justify-between w-full border-b border-slate-100 py-2"):
                        ui.label(row["interest"]).classes("font-medium")
                        ui.label(f"demand {row['demand']} | supply {row['supply']} | gap {row['gap']}")
        with ui.tab_panel(submit):
            submit_form()
        with ui.tab_panel(review):
            review_queue()
        with ui.tab_panel(live):
            live_opportunities()
        with ui.tab_panel(diagnostics):
            model_audit()


def submit_form():
    with section_card("Submit opportunity for review"):
        title = ui.input("Title").classes("w-full")
        organizer = ui.input("Organizer").classes("w-full")
        opp_type = ui.select(core.OPPORTUNITY_TYPES, value="workshop", label="Type").classes("w-full")
        interests = ui.input("Interests", placeholder="AI, coding, public good").classes("w-full")
        levels = {level: ui.checkbox(level, value=level in ["JC", "Poly"]) for level in core.LEVELS}
        cost = ui.select(["free", "paid"], value="free", label="Cost").classes("w-full")
        beginner = ui.switch("Beginner-friendly", value=True)
        deadline = ui.input("Deadline", value="2026-08-20", placeholder="YYYY-MM-DD").classes("w-full")
        url = ui.input("URL", value="https://example.com").classes("w-full")

        def submit() -> None:
            selected_levels = [level for level, checkbox in levels.items() if checkbox.value]
            parsed = core.parse_interests(interests.value or "")
            if not title.value or not organizer.value or not parsed or not selected_levels:
                ui.notify("Please fill title, organizer, interests, and levels.", type="warning")
                return
            opportunity = core.Opportunity(
                "draft",
                title.value.strip(),
                opp_type.value,
                parsed,
                selected_levels,
                cost.value,
                bool(beginner.value),
                deadline.value.strip(),
                url.value.strip(),
                organizer.value.strip(),
            )
            preview = core.submission_preview(opportunity, STATE.opportunities)
            core.create_submission(STATE.submissions, opportunity)
            ui.notify(f"Submitted for review | access {preview['access_score']}/100", type="positive")
            refresh_all()

        primary_button("Submit for review", icon="send", on_click=submit)


def review_queue():
    pending = core.pending_submissions(STATE.submissions)
    if not pending:
        ui.label("No pending submissions.").classes("empty-state")
        return
    for submission in pending:
        opportunity = core.submission_opportunity(submission)
        preview = core.submission_preview(opportunity, STATE.opportunities)
        spam = intelligence.predict_spam(opportunity, STATE.submissions)
        flags = intelligence.review_flags(opportunity, STATE.opportunities, STATE.submissions)
        with ui.card().classes("opp-card"):
            ui.label(opportunity.title).classes("text-lg font-semibold")
            ui.label(opportunity.organizer + " | " + opportunity.deadline).classes("text-sm text-slate-500")
            with ui.row().classes("gap-2"):
                badge(f"access {preview['access_score']}/100", "info")
                badge(f"demand {preview['demand_matches']}", "neutral")
                badge(f"spam {round(spam['probability'] * 100)}%", "bad" if spam["risk"] == "HIGH" else "warn" if spam["risk"] == "MEDIUM" else "good")
            for flag in flags:
                badge(flag["severity"] + ": " + flag["label"], "bad" if flag["severity"] == "BLOCKER" else "warn")
                ui.label(flag["detail"]).classes("text-xs text-slate-500")
            note = ui.input("Rejection note", placeholder="spam/scam/prize/click/crypto teaches the model").classes("w-full")
            with ui.row().classes("gap-2"):
                primary_button("Approve", icon="check", on_click=lambda s=submission: approve(s))
                danger_button("Reject", icon="close", on_click=lambda s=submission, n=note: reject(s, n.value))


def approve(submission: dict) -> None:
    opportunity = core.submission_opportunity(submission)
    flags = intelligence.review_flags(opportunity, STATE.opportunities, STATE.submissions)
    if any(flag["severity"] == "BLOCKER" for flag in flags):
        ui.notify("Cannot approve while a blocker is present.", type="negative")
        return
    if core.approve_submission(STATE.submissions, STATE.opportunities, submission["submission_id"]):
        ui.notify("Approved and published", type="positive")
        refresh_all()


def reject(submission: dict, note: str) -> None:
    if core.reject_submission(STATE.submissions, submission["submission_id"], note or "Rejected by reviewer."):
        ui.notify("Rejected", type="positive")
        refresh_all()


def live_opportunities():
    for opportunity in [opp for opp in STATE.opportunities if core.days_until(opp.deadline) >= 0][:12]:
        with inner_card():
            ui.label(opportunity.title).classes("font-semibold")
            ui.label(opportunity.organizer + " | " + opportunity.deadline).classes("text-sm text-slate-500")
            soft_button("Write announcement", on_click=lambda opp=opportunity: write_announcement(opp))


def write_announcement(opportunity: core.Opportunity) -> None:
    path = core.save_announcement(opportunity)
    ui.notify("Announcement written to " + path.name, type="positive")


def model_audit():
    health = intelligence.model_health(STATE.submissions)
    with section_card("Reviewer diagnostics"):
        ui.label("Adaptive Naive Bayes spam-risk model").classes("text-slate-600")
        with ui.row().classes("gap-2"):
            badge(f"{health['total']} examples", "info")
            badge(f"{health['history']} from review history", "neutral")
            badge(f"{health['accuracy'] * 100:.1f}% leave-one-out accuracy", "good")
        ui.label("Top learned spam tokens").classes("mt-4 font-semibold")
        for token, weight in health["top_tokens"]:
            ui.label(f"{token}: {weight:.2f}").classes("text-sm text-slate-600")


@ui.page("/")
def index():
    apply_theme()
    ui.dark_mode(False)
    with page_container():
        hero("Opportunity Radar", "A two-sided access system for students and opportunity organizers.", "Built with Python · NiceGUI")
        metrics()
        with ui.tabs().classes("clean-tabs").props("inline-label") as tabs:
            discover = ui.tab("Discover", icon="travel_explore")
            applications = ui.tab("Applications", icon="fact_check")
            equity = ui.tab("Equity", icon="balance")
            career = ui.tab("Career", icon="trending_up")
            sender = ui.tab("Sender", icon="move_to_inbox")
            help_tab = ui.tab("Help", icon="help_outline")

        with ui.tab_panels(tabs, value=discover).classes("w-full bg-transparent").props(
            'transition-prev="fade" transition-next="fade" transition-duration="300"'
        ):
            with ui.tab_panel(discover).classes("p-0"):
                build_discover_tab()
            with ui.tab_panel(applications).classes("p-0"):
                applications_panel()
            with ui.tab_panel(equity).classes("p-0"):
                equity_panel()
            with ui.tab_panel(career).classes("p-0"):
                career_panel()
            with ui.tab_panel(sender).classes("p-0"):
                sender_panel()
            with ui.tab_panel(help_tab).classes("p-0"):
                build_help_tab()


def main() -> None:
    ui.run(title="Opportunity Radar", host="127.0.0.1", port=8080, reload=False)


if __name__ in {"__main__", "__mp_main__"}:
    main()
