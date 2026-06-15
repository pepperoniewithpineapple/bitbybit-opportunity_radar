from nicegui import ui

import core
import utils
import models
import storage
import intelligence

from theme import *

#  Mock data representing database collections
SAMPLE_OPPORTUNITIES = [
    models.Opportunity(id="1", title="AI Research Assistant", type="research", interests=["ai", "research"], eligible_levels=["undergraduate", "masters"], cost="free", beginner_friendly=False, deadline="2026-07-01", url="http://example.com/ai-research", organizer="National Lab"),
    models.Opportunity(id="2", title="Global Hackathon 2026", type="hackathon", interests=["tech", "coding"], eligible_levels=["high school", "undergraduate"], cost="300", beginner_friendly=True, deadline="2026-08-15", url="http://example.com/hackathon", organizer="Tech Corp"),
    models.Opportunity(id="3", title="UI/UX Design Intensive", type="workshop", interests=["design", "ui/ux"], eligible_levels=["undergraduate", "postgraduate"], cost="free", beginner_friendly=True, deadline="2026-06-30", url="http://example.com/ux-workshop", organizer="Design Studio")
]
opportunities = SAMPLE_OPPORTUNITIES


SEARCH_DEBOUNCE = 400 #  milliseconds


class SearchState:
    def __init__(self) -> None:
        self.query = ""
        self.sort_by = "Alphabetical (A-Z)"


state = SearchState()


def filter_opportunities(query: str, sort_by: str) -> list[models.Opportunity]:
    # TODO: Replace with actual filtering logic.
    return opportunities


@ui.refreshable
def render_opportunities():
    filtered_list = filter_opportunities(state.query, state.sort_by)

    #  Search check
    if state.query.strip(): #  Search query is not empty
        search_token = state.query.lower().strip()
        #  TODO

    with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2"):
        for opp in filtered_list:
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
            options=list(utils.ACADEMIC_LEVELS), label="Acadmic Level",
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
            
        ui.element("q-separator").props("color=amber-2").classes("my-1")
        
        with ui.row().classes("w-full justify-between items-center mt-2"):
            ui.label(f"Deadline: {opp.deadline}").classes(f"text-xs font-bold text-[{DEADLINE}]")
            ui.button("View Details", icon="arrow_forward", on_click=lambda: ui.navigate.to(opp.url, new_tab=True)).props("flat color=brown").classes("text-xs font-bold")


@ui.refreshable
def main() -> None:
    #  Load student profile
    profile = storage.load_student()
    if profile is None:
        profile = models.Student(name="", level="", interests=[])

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
                placeholder="Type to filter..."
            ).bind_value_to(state, "query").on(
                "value-change", render_opportunities.refresh
            ).classes("w-full md:w-128").props(f"outlined dense clearable color=brown text-sm debounce={SEARCH_DEBOUNCE}")
            
            #  Sorting parameter criteria dropdown selector
            ui.select(
                options=["Deadline (Soonest)", "Alphabetical (A-Z)", "Type"], 
                value=state.sort_by,
                label="Sort By"
            ).bind_value_to(state, "sort_by").on(
                "value-change", render_opportunities.refresh
            ).classes("w-full md:w-48").props("outlined dense color=brown text-sm")

            ui.button(
                icon="refresh", 
                on_click=render_opportunities.refresh
            ).props("outlined color=brown square").classes("h-[40px] w-[40px] shadow-none bg-transparent text-[#bd5d3a] border-[#e9dcc7]")

        render_opportunities()


if __name__ in {"__main__", "__mp_main__"}:
    apply_custom_styles()

    main()

    ui.run(title="Opportunity Tracker")