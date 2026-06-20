import asyncio

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from nicegui import ui

import models
import storage

from webscrapers.cordy import scrape_cordy
from webscrapers.devpost import scrape_devpost
from pages.explore import explore
from pages.applied_opportunities import my_opportunities, render_my_opportunities
from pages.portfolio import portfolio, render_portfolio
from personalisation import interest_matcher, InteractionManager
from theme import *


interaction_manager = InteractionManager()


async def pull_opportunities() -> list[models.Opportunity]:
    await asyncio.to_thread(storage.save_last_updated_timestamp)

    results = await asyncio.gather(
        asyncio.to_thread(asyncio.run, scrape_cordy()),
        asyncio.to_thread(asyncio.run, scrape_devpost())
    )

    opportunities = []
    for result in results:
        opportunities.extend(result)

    await asyncio.to_thread(storage.save_opportunities, opportunities)

    return interest_matcher.score_opportunities(opportunities)


SEARCH_DEBOUNCE = 400 #  milliseconds
SORT_OPTIONS = ("Recommended", "Deadline (Soonest)", "Alphabetical (A-Z)", "Type")
SortOptions = Literal[*SORT_OPTIONS]
CACHE_EXPIRATION_HOURS = 12 #  When to run scrapers automatically


@dataclass
class AppState:
    def __init__(self) -> None:
        is_empty = not storage.load_opportunities()
        cache_expired = (datetime.now().timestamp() - storage.load_last_updated_timestamp()) > CACHE_EXPIRATION_HOURS*60*60
        
        if is_empty or cache_expired:
            self.status: Literal["booting", "ready"] = "booting"
        else:
            self.status: Literal["booting", "ready"] = "ready"
        self.is_refreshing = False

        self.opportunities: list[models.Opportunity] = storage.load_opportunities()

        self.profile = storage.load_student()
        if self.profile is None:
            self.profile = models.Student(name="John Smith", level="JC", interests=[], career_goals=[])


@dataclass
class SearchState:
    def __init__(self) -> None:
        self.query = ""
        self.sort_by: SortOptions = "Recommended"


app_state = AppState()
search_state = SearchState()


def create_profile_dialog(student_profile: models.Student) -> ui.dialog:
    with ui.dialog() as dialog, ui.card().classes(f"p-6 w-full bg-[{CARD}] border border-[{CARD_BORDER}]"):
        with ui.row().classes("w-full justify-between items-centre mb-4"):
            ui.label("Edit Profile").classes(f"text-2xl font-serif font-bold text-[{TITLE_TEXT}]")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense color=brown")

        name_input = ui.input(
            "Name", placeholder="Enter your name...", 
            value=student_profile.name
        ).classes("w-full").props("outlined dense color=brown")
        level_select = ui.select(
            options=list(models.ACADEMIC_LEVELS), label="Academic Level",
            value=student_profile.level
        ).classes("w-full").props("outlined dense color=brown")
        interests_input = ui.input(
            "Interests", placeholder="Enter your interests (comma-separated, e.g. artificial intelligence, design, cybersecurity)",
            value=", ".join(student_profile.interests)
        ).classes("w-full").props("outlined dense color=brown")
        career_goals_input = ui.input(
            "Career Goals", placeholder="Enter your career goals (comma-separated, e.g. software engineer, data analyst)",
            value=", ".join(student_profile.career_goals)
        ).classes("w-full").props("outlined dense color=brown")

        def save_profile():
            student_profile.name = name_input.value
            student_profile.level = level_select.value
            student_profile.interests = [i.strip() for i in interests_input.value.split(",") if i.strip()]
            student_profile.career_goals = [i.strip() for i in career_goals_input.value.split(",") if i.strip()]
            storage.save_student(student_profile)
            dialog.close()
            ui.notify("Profile updated", type="positive")
            interaction_manager.log_profile(student_profile)
            main.refresh()
            
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Save", on_click=save_profile).classes(f"px-6 py-2 bg-[{SUBTEXT}] text-white rounded font-bold")
            
    return dialog


async def init_app():
    if app_state.status == "booting":
        app_state.opportunities = await pull_opportunities()
    app_state.status = "ready"
    main.refresh()


@ui.refreshable
def main() -> None:
    #  Initial fetch
    if app_state.status == "booting":
        with ui.column().classes('w-full items-center justify-center q-pa-xl').style('min-height: 80vh'):
            ui.spinner(size='lg', color='primary')
            
            ui.label("Fetching data...").classes('text-lg text-grey-7 mt-4 font-medium')
                    
        return

    # Main display
    #  Load student profile
    profile = app_state.profile

    profile_modal = create_profile_dialog(profile)

    #  Different pages
    with ui.tabs().classes(f"w-full rounded-xl") as tabs:
        ui.tab("explore", label="Discover", icon="travel_explore")
        ui.tab("tracker", label="My Opportunities", icon="fact_check")
        ui.tab("portfolio", label="My Portfolio", icon="dashboard_customize")

    with ui.column().classes("max-w-6xl mx-auto px-4 py-8 w-full gap-6"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-1"):
                ui.label("Opportunity Radar").classes(f"text-4xl font-serif font-bold text-[{TITLE_TEXT}]")
                ui.label("Portfolio building made easy.").classes(f"text-sm text-[{SUBTEXT}]")

            with ui.column().classes("gap-1 items-start"):
                ui.button(f"Profile: {profile.name or 'Not set'}", icon="person", on_click=profile_modal.open).props("flat color=brown").classes("font-bold")
                ui.html(f"- <b>Academic Level</b>: {profile.level or 'Not set'}").classes(f"text-sm text-[{SUBTEXT}] ml-6")
                ui.html(f"- <b>Interests</b>: {', '.join(profile.interests) or 'Not set'}").classes(f"text-sm text-[{SUBTEXT}] ml-6")
                ui.html(f"- <b>Career Goals</b>: {', '.join(profile.career_goals) or 'Not set'}").classes(f"text-sm text-[{SUBTEXT}] ml-6")

    with ui.tab_panels(tabs, value="explore").classes("w-full"):
        with ui.tab_panel("explore").classes("w-full"):
            app_state.opportunities = interest_matcher.score_opportunities(app_state.opportunities)
            explore(app_state, on_apply_change=render_my_opportunities.refresh)
        with ui.tab_panel("tracker").classes("w-full"):
            render_my_opportunities.refresh()
            my_opportunities(app_state, on_complete=render_portfolio.refresh)
        with ui.tab_panel("portfolio").classes("w-full"):
            render_portfolio.refresh()
            portfolio(app_state)
            


@ui.page('/')
def index_page() -> None:
    main()

    if app_state.status == "booting":
        asyncio.create_task(init_app())
    else:
        app_state.opportunities = interest_matcher.score_opportunities(app_state.opportunities)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Opportunity Radar")