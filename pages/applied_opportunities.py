import asyncio

from typing import Literal
from datetime import datetime

from humanize import naturaltime
from nicegui import ui, app

import models
import storage
import intelligence

from theme import *
from webscrapers.cordy import scrape_cordy
from webscrapers.devpost import scrape_devpost
from personalisation import interest_matcher, InteractionManager


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


app_state = None #  Set once my_opportunities is called


@ui.refreshable
def render_my_opportunities():
    # with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2"):
    my_opportunities = storage.load_my_opportunities()
    for opp in sorted(my_opportunities, key=lambda x: x.deadline):
        render_opportunity_card(opp)


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


def view_details(opportunity: models.Opportunity) -> None:
    ui.navigate.to(opportunity.url, new_tab=True)
    interaction_manager.log_view(opportunity)


def get_status_classes(status: Literal["pending", "rejected", "ongoing", "completed"]) -> str:
    if status == "completed":
        return "bg-green-100 text-green-800"
    elif status in {"ongoing", "pending"}:
        return "bg-amber-100 text-amber-800"
    else:
        return "bg-red-100 text-red-800"


def render_opportunity_card(opportunity: models.AppliedOpportunity):
    def remove_opportunity():
        storage.remove_applied_opportunity(opportunity.id)
        render_my_opportunities.refresh()
        ui.notify(f"Opportunity removed")
    
    def set_opportunity_status(status: Literal["pending", "rejected", "ongoing", "completed"]):
        storage.set_applied_status(opportunity.id, status)
        status_select.classes(replace=f"w-50 {get_status_classes(status)} rounded-full px-4 border-none")
        ui.notify(f"Status updated to {status.title()}")

    with ui.card().classes("opp-card p-5 w-full gap-5").props("flat"):
        with ui.row().classes("w-full justify-between items-start gap-4"):
            with ui.column().classes("gap-0 grow"):
                ui.label(opportunity.title).classes(f"text-lg font-bold text-[{TITLE_TEXT}]")
                ui.label(opportunity.organiser).classes(f"text-sm text-[{SUBTEXT}]")
            ui.button(icon="delete", on_click=remove_opportunity).props("flat round color=red")
            

        with ui.row().classes("items-start").tooltip("Categories"):
            ui.icon("tips_and_updates").classes(f"mt-[0.2rem] ml-1 text-[{CAT_TEXT}]")
            for interest in opportunity.interests:
                ui.label(interest).classes(
                    f"text-[11px] font-bold px-2 py-0.5 rounded-full bg-[{CAT_BG}] text-[{CAT_TEXT}]"
                )
            
        with ui.row().classes("w-full justify-between items-center"):
            #  Badge treatment
            if opportunity.type in TYPE_STYLES:
                type_bg, type_text = TYPE_STYLES[opportunity.type]
            else:
                type_bg, type_text = DEFAULT_TYPE_STYLE

            ui.label(opportunity.type.upper()).classes(
                f"text-xs font-bold tracking-wider px-2 py-1 rounded bg-[{type_bg}] text-[{type_text}]"
            )
            ui.button("View Details", icon="arrow_forward", on_click=lambda: view_details(opportunity)).props("flat color=brown").classes("text-xs font-bold")
            
        #  Reformat deadline date
        date_obj = datetime.strptime(opportunity.deadline, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")
        
        #  Deadline and Apply button
        with ui.row().classes("w-full justify-between items-center mt-2"):
            ui.label(f"Deadline: {formatted_date}").classes(f"text-xs font-bold text-[{DEADLINE}]")

            status_select = ui.select(
                options=["Pending", "Rejected", "Ongoing", "Completed"],
                value=opportunity.status.title(),
                on_change=lambda e: set_opportunity_status(e.value.lower())
            ).classes(f"w-50 {get_status_classes(opportunity.status)} rounded-full px-4 border-none")


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
        my_opportunities.refresh()


async def init_app():
    if app_state.status == "booting":
        app_state.opportunities = await pull_opportunities()
    app_state.status = "ready"
    my_opportunities.refresh()


def log_search():
    query = (search_state.query or "").strip()
    if len(query) >= 3:
        interaction_manager.log_search(query)


@ui.page("/my_opportunities")
def my_opportunities(app_state_) -> None:
    global app_state
    app_state = app_state_
    render_my_opportunities()


# @ui.page('/')
# def index_page() -> None:
#     app_state.opportunities = interest_matcher.score_opportunities(app_state.opportunities)
#     my_opportunities()

#     if app_state.status == "booting":
#         asyncio.create_task(init_app())


# if __name__ in {"__my_opportunities__", "__mp_my_opportunities__"}:
#     ui.run(title="Opportunity Tracker")