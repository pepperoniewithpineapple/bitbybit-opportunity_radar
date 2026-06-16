import asyncio

from typing import Literal
from datetime import datetime
from dataclasses import dataclass

from humanize import naturaltime
from nicegui import ui, app

import core
import utils
import models
import storage
import intelligence

from theme import *
from webscrapers.cordy import scrape_cordy
from webscrapers.devpost import scrape_devpost


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
    return opportunities


SEARCH_DEBOUNCE = 400 #  milliseconds
SORT_OPTIONS = ("Deadline (Soonest)", "Alphabetical (A-Z)", "Type")
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
            self.profile = models.Student(name="", level="", interests=[], career_goals=[], applied_for=[])


@dataclass
class SearchState:
    def __init__(self) -> None:
        self.query = ""
        self.sort_by: SortOptions = "Alphabetical (A-Z)"


app_state = AppState()
state = SearchState()


def sort_opportunities(opportunities: list[models.Opportunity], sort_by: SortOptions) -> list[models.Opportunity]:
    match sort_by:
        case "Deadline (Soonest)":
            return sorted(opportunities, key=lambda x: x.deadline) #  Since deadline is formatted as YYYY-MM-DD, this works
        case "Alphabetical (A-Z)":
            return sorted(opportunities, key=lambda x: x.title)
        case "Type":
            return sorted(opportunities, key=lambda x: x.type)
        case _:
            return opportunities


@ui.refreshable
def render_opportunities():
    #  Search check

    query = state.query or ""

    if query.strip(): #  Search query is not empty
        opportunities = [x["opportunity"] for x in intelligence.search_opportunities(query, app_state.opportunities)]
    else:
        opportunities = app_state.opportunities

    opportunities = sort_opportunities(opportunities, state.sort_by)

    with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2"):
        for opp in opportunities:
            render_opportunity_card(opp)


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
            options=list(utils.ACADEMIC_LEVELS), label="Academic Level",
            value=student_profile.level
        ).classes("w-full").props("outlined dense color=brown")
        interests_input = ui.input(
            "Interests", placeholder="Enter your interests (comma-separated, e.g. artificial intelligence, design, cybersecurity)",
            value=", ".join(student_profile.interests)
        ).classes("w-full").props("outlined dense color=brown")

        def save_profile():
            student_profile.name = name_input.value
            student_profile.level = level_select.value
            student_profile.interests = [i.strip() for i in interests_input.value.split(",") if i.strip()]
            storage.save_student(student_profile)
            dialog.close()
            ui.notify("Profile updated", type="positive")
            main.refresh()
            
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Save", on_click=save_profile).classes(f"px-6 py-2 bg-[{SUBTEXT}] text-white rounded font-bold")
            
    return dialog


@app.on_connect
def apply_custom_styles():
    #  Inject system-wide design specs matching your theme.py layer
    ui.add_head_html("""
        <style>
            body {{ 
                background-color: {canvas}; 
                font-family: 'DM Sans', sans-serif;
            }}
            .opp-card {{
                background-color: {card};
                border: 1px solid {card_border};
                border-radius: 12px;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .opp-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(140, 123, 105, 0.1);
            }}
        </style>
    """.format(canvas=CANVAS, card=CARD, card_border=CARD_BORDER))

def render_opportunity_card(opp: models.Opportunity):
    #  Handles the opportunity Apply button functions
    def apply_opportunity():
        if opp.id not in app_state.profile.applied_for:
            app_state.profile.applied_for.append(opp.id)
            ui.notify("Labelled as Applied!", type="positive")
            applying_button.props("color=green icon=check")
            applying_button.text = "Applied!"
        else:
            app_state.profile.applied_for.remove(opp.id)
            ui.notify("Removed from Applications!", type="negative")
            applying_button.props("color=blue", remove="icon")
            applying_button.text = "I'm Applying!"

        storage.save_student(app_state.profile)

    def apply_button_hover(is_hovered: bool):
        if opp.id in app_state.profile.applied_for:
            if is_hovered:
                applying_button.props("color=red icon=close")
                applying_button.text = "Undo"
            else:
                applying_button.props("color=green icon=check")
                applying_button.text = "Applied!"

    #  Encapsulate single element rendering logic
    with ui.card().classes("opp-card p-6 w-full gap-2").props("flat"):
        with ui.row().classes("w-full justify-between items-start"):
            with ui.column().classes("gap-0"):
                ui.label(opp.title).classes(f"text-lg font-bold text-[{TITLE_TEXT}]")
                ui.label(opp.organizer).classes(f"text-sm text-[{SUBTEXT}]")
            
            #  Badge treatment
            ui.label(opp.type.upper()).classes(
                f"text-xs font-bold tracking-wider px-2 py-1 rounded bg-[{TAG}] text-[{TAG_TEXT}]"
            )
            ui.button("View Details", icon="arrow_forward", on_click=lambda: ui.navigate.to(opp.url, new_tab=True)).props("flat color=brown").classes("text-xs font-bold")
            
        ui.element("q-separator").props("color=amber-2").classes("my-1")

        #  Reformat deadline date
        date_obj = datetime.strptime(opp.deadline, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")
        
        #  Deadline and Apply button
        with ui.row().classes("w-full justify-between items-center mt-2"):
            ui.label(f"Deadline: {formatted_date}").classes(f"text-xs font-bold text-[{DEADLINE}]")

            applying_button = ui.button("I'm Applying!", on_click=apply_opportunity).props("color=blue").classes(f"w-32 text-xs font-bold !text-[{GOLD}] transition-colors duration-200 ease-in-out")
            if opp.id in app_state.profile.applied_for:
                applying_button.props("color=green icon=check")
                applying_button.text = "Applied!"
            applying_button.on("mouseenter", lambda: apply_button_hover(True))
            applying_button.on("mouseleave", lambda: apply_button_hover(False))




def refresh(refresh_button: ui.button) -> None:
    if app_state.is_refreshing: #  Ignore multiple requests if one is already processing
        return

    app_state.is_refreshing = True
    refresh_button.classes("animate-spin")
    asyncio.create_task(refresh_task(refresh_button))


async def refresh_task(refresh_button: ui.button):
    try:
        app_state.opportunities = await pull_opportunities()
    finally:
        app_state.is_refreshing = False
        refresh_button.classes(remove="animate-spin")
        render_opportunities.refresh()
        main.refresh()


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
            
            # This timer updates the text on screen every 200ms to show scraper progress
            ui.label("Fetching data...").classes('text-lg text-grey-7 mt-4 font-medium')
            
            # ui.markdown('*Fetching data...*').classes('text-xs text-grey-5 mt-2')
        
        return

    # Main display

    #  Load student profile
    profile = app_state.profile

    profile_modal = create_profile_dialog(profile)


    with ui.column().classes("max-w-6xl mx-auto px-4 py-8 w-full gap-6"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-1"):
                ui.label("Explore Opportunities").classes(f"text-3xl font-serif font-bold text-[{TITLE_TEXT}]")
                ui.label("Personalized pipeline matching current demand vectors.").classes(f"text-sm text-[{SUBTEXT}]")

            with ui.column().classes("gap-1 items-start"):
                ui.button(f"Profile: {profile.name or 'Not set'}", icon="person", on_click=profile_modal.open).props("flat color=brown").classes("font-bold")
                ui.html(f"- <b>Academic Level</b>: {profile.level or 'Not set'}").classes(f"text-sm text-[{SUBTEXT}] ml-6")
                ui.html(f"- <b>Interests</b>: {', '.join(profile.interests) or 'Not set'}").classes(f"text-sm text-[{SUBTEXT}] ml-6")
            
        with ui.row().classes(f"w-full items-center justify-between gap-4 bg-[{CARD}] p-4 rounded-xl border border-[{CARD_BORDER}]"):
            #  Search input with Quasar native text entry debounce configuration (500ms delay)
            ui.input(
                label="Search Opportunities", 
                placeholder="Type to filter...",
                on_change=render_opportunities.refresh
            ).bind_value_to(state, "query").classes("w-full md:w-128").props(f"outlined dense clearable color=brown text-sm debounce={SEARCH_DEBOUNCE}")
            
            #  Sorting parameter criteria dropdown selector
            ui.select(
                options=list(SORT_OPTIONS), 
                value=state.sort_by,
                label="Sort By",
                on_change=render_opportunities.refresh
            ).bind_value_to(state, "sort_by").classes("w-full md:w-48").props("outlined dense color=brown text-sm")

            last_updated_timestamp = storage.load_last_updated_timestamp()
            ui.label(f"Last updated: {naturaltime(datetime.now()-datetime.fromtimestamp(last_updated_timestamp))}").classes(f"text-sm text-[{SUBTEXT}]")
            refresh_button = ui.button(
                icon="refresh", 
                on_click=lambda: refresh(refresh_button)
            ).props("outlined color=brown square").classes("h-[40px] w-[40px] shadow-none bg-transparent")
            refresh_button.tooltip("Pull fresh opportunities listings")

        render_opportunities()


@ui.page('/')
def index_page() -> None:
    main()

    if app_state.status == "booting":
        asyncio.create_task(init_app())


if __name__ in {"__main__", "__mp_main__"}:
    # app.on_startup(init_app)

    ui.run(title="Opportunity Tracker")