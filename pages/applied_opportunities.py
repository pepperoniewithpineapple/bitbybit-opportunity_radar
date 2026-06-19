import asyncio

from typing import Literal
from datetime import datetime

from nicegui import ui, app

import models
import storage

from theme import *


app_state = None #  Set once my_opportunities is called


@ui.refreshable
def render_my_opportunities(on_complete=None):
    # with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2"):
    my_opportunities = storage.load_my_opportunities()
    for opp in sorted(my_opportunities, key=lambda x: x.deadline):
        render_opportunity_card(opp, on_complete)


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


def get_status_classes(status: Literal["pending", "rejected", "ongoing", "completed"]) -> str:
    if status == "completed":
        return "bg-green-100 text-green-800"
    elif status in {"ongoing", "pending"}:
        return "bg-amber-100 text-amber-800"
    else:
        return "bg-red-100 text-red-800"


def render_opportunity_card(opportunity: models.AppliedOpportunity, on_complete=None):
    def remove_opportunity():
        storage.remove_applied_opportunity(opportunity.id)
        render_my_opportunities.refresh()
        ui.notify(f"Opportunity removed")
    
    def set_opportunity_status(status: Literal["pending", "rejected", "ongoing", "completed"]):
        storage.set_applied_status(opportunity.id, status)
        status_select.classes(replace=f"w-50 {get_status_classes(status)} rounded-full px-4 border-none")
        ui.notify(f"Status updated to {status.title()}")
        if status == "completed":
            on_complete()

    def set_notes():
        storage.set_notes(opportunity.id, notes_input.value)
        ui.notify("Notes updated")

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

        notes_input = ui.input(label="Notes", value=opportunity.notes).classes("w-full").on(
            "blur", set_notes
        ).on(
            'keydown.enter', set_notes
        )


@ui.page("/my_opportunities")
def my_opportunities(app_state_, on_complete=None) -> None:
    global app_state
    app_state = app_state_
    render_my_opportunities(on_complete)
