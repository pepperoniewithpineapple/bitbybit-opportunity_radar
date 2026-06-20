import os
import uuid

from typing import Literal
from datetime import datetime

from nicegui import ui, app

import models
import storage

from theme import *

from typing import Callable, Optional


SEARCH_DEBOUNCE = 400 #  milliseconds
SORT_OPTIONS = ("Latest", "Alphabetical (A-Z)", "Type")
SortOptions = Literal[*SORT_OPTIONS]
CERTIFICATES_PATH = os.path.join(os.path.dirname(__file__), "../data", "certificates")


app.add_static_files("/certificates", CERTIFICATES_PATH)


class SearchState:
    def __init__(self) -> None:
        self.query = ""
        self.sort_by: SortOptions = "Latest"


search_state = SearchState()
app_state = None #  Set once explore is called


def sort_portfolio(portfolio: list[models.PortfolioItem], sort_by: SortOptions) -> list[models.PortfolioItem]:
    match sort_by:
        case "Latest":
            return sorted(portfolio, key=lambda x: x.end_date) #  Since deadline is formatted as YYYY-MM-DD, this works
        case "Alphabetical (A-Z)":
            return sorted(portfolio, key=lambda x: x.title)
        case "Type":
            return sorted(portfolio, key=lambda x: x.type)
        case _:
            return portfolio


@ui.refreshable
def render_portfolio(on_apply_change: Optional[Callable] = None):
    #  Search check
    query = search_state.query or ""

    portfolio: list[models.PortfolioItem] = storage.load_portfolio()

    if query.strip(): #  Search query is not empty
        portfolio = [x for x in portfolio if query in str(x).lower()]

    portfolio = sort_portfolio(portfolio, search_state.sort_by)

    with ui.row().classes("w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2"):
        for item in portfolio:
            render_item_card(item)


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
    

def validate_dates(s: str) -> tuple[datetime]:
    try:
        if s.count("-") == 2: #  Single date
            datetime.strptime(s.strip(), "%Y-%m-%d")
            return True
        elif s.count("-") == 5: #  Double date
            start, end = s.split(" - ")
            return datetime.strptime(start.strip(), "%Y-%m-%d") <= datetime.strptime(end.strip(), "%Y-%m-%d")
        return False
    except ValueError:
        return False


def ensure_date_format(s: str) -> tuple[None | str, str]:
    if not validate_dates(s):
        raise ValueError("Invalid date format.")
    dates = s.split(" - ")
    if len(dates) == 1:
        return None, dates[0].strip()
    return dates[0].strip(), dates[1].strip()

def render_item_card(item: models.PortfolioItem):
    async def upload_certificate(e) -> None:
        destination = os.path.join(CERTIFICATES_PATH, e.file.name)
        await e.file.save(destination)

        abs_path = os.path.abspath(destination)
        storage.edit_portfolio_item(item.id, "certificate_path", abs_path)
        render_portfolio.refresh()

        ui.notify(f"Saved {e.file.name} at {abs_path}")

    def edit_field(e, attr: Literal["title", "organiser", "type", "dates", "role", "hours", "awards"]) -> None:
        value = e.sender.value
        if attr == "awards":
            value = [x.strip() for x in value.split(",")]

        if attr == "dates":
            if not validate_dates(value):
                ui.notify(f"Invalid date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD - YYYY-MM-DD'", type="negative")
                return
            start, end = ensure_date_format(value)
            storage.edit_portfolio_item(item.id, "start_date", start)
            storage.edit_portfolio_item(item.id, "end_date", end)
        
        else:
            storage.edit_portfolio_item(item.id, attr, value)
        render_portfolio.refresh()
        
        ui.notify(f"Saved {value} to {attr}")

    with ui.card().classes("opp-card p-6 w-full gap-2").props("flat"):
        with ui.row().classes("w-full justify-between items-start"):
            with ui.column().classes("gap-0 min-w-0 flex-1"):
                ui.input(value=item.title).on("blur", lambda e: edit_field(e, "title")).classes("w-full").props(f'borderless input-class="font-bold text-lg text-[{TITLE_TEXT}]"')
                ui.input(value=item.organiser).on("blur", lambda e: edit_field(e, "organiser")).classes("w-full").props(f'borderless input-class="text-sm text-[{SUBTEXT}]"')

        with ui.row().classes("w-full justify-between items-center min-w-0 flex-1"):
            if item.type in TYPE_STYLES:
                type_bg, type_text = TYPE_STYLES[item.type]
            else:
                type_bg, type_text = DEFAULT_TYPE_STYLE

            ui.input(value=item.type.upper()).on("blur", lambda e: edit_field(e, "type")).props(f'borderless dense input-style="text-align: center;" input-class="tracking-wider px-2 py-1 rounded font-bold text-xs text-[{type_text}] bg-[{type_bg}]"')

        with ui.grid(columns=2).classes("w-full gap-x-16 gap-y-3 mt-4"):
            with ui.column().classes("gap-0 min-w-0 flex-1"):
                ui.label("Role").classes(f"text-sm font-bold text-[{TITLE_TEXT}]")
                ui.input(value=item.role).on("blur", lambda e: edit_field(e, "role")).props(f'borderless input-class="text-sm text-[{TITLE_TEXT}] w-full"')

            if item.start_date:
                dates_str = f"{item.start_date} - {item.end_date}"
            else:
                dates_str = item.end_date

            with ui.column().classes("gap-0 min-w-0 flex-1"):
                ui.label("Date(s)").classes(f"text-sm font-bold text-[{TITLE_TEXT}]")
                ui.input(value=dates_str).on("blur", lambda e: edit_field(e, "dates")).props(f'borderless input-class="text-sm text-[{TITLE_TEXT}]"')

            awards_or_hours = ("Hours", item.hours) if item.type in {"Volunteer", "Volunteering"} else ("Awards", ", ".join(item.awards))
            label, value = awards_or_hours

            with ui.column().classes("gap-0 min-w-0 flex-1"):
                ui.label(label).classes(f"text-sm font-bold text-[{TITLE_TEXT}]")
                ui.input(value=value).on("blur", lambda e: edit_field(e, label.lower())).props(f'borderless input-class="text-sm text-[{TITLE_TEXT}]"')

            with ui.column().classes("gap-0 min-w-0 flex-1"):
                ui.label("Certificate").classes(f"text-sm font-bold text-[{TITLE_TEXT}]")
                if item.certificate_path is None:
                    ui.upload(label="Upload", on_upload=upload_certificate, auto_upload=True).classes("max-w-full")
                else:
                    filename = os.path.basename(item.certificate_path)
                    cert_url = f"/certificates/{filename}"

                    with ui.dialog() as cert_dialog, ui.card().classes("p-4 items-center"):
                        ui.image(cert_url).classes("w-96 max-h-[80vh] object-contain rounded-lg")
                        ui.button("Close", on_click=cert_dialog.close).props("flat color=brown").classes("mt-2")

                    ui.button("View", on_click=cert_dialog.open).props("flat dense color=brown").classes("text-sm p-0 justify-start text-left")


def add_empty_item():
    item = models.PortfolioItem(id=str(uuid.uuid4()), title="", organiser="", type="")
    storage.add_portfolio_item(item)
    render_portfolio.refresh()


@ui.page("/portfolio")
def portfolio(app_state_) -> None:
    global app_state
    app_state = app_state_
    #  Search
    with ui.row().classes(f"w-full items-center justify-between gap-4 bg-[{CARD}] p-4 rounded-xl border border-[{CARD_BORDER}]"):
        ui.input(
            label="Search portfolio", 
            placeholder="Type to filter...",
            on_change=render_portfolio.refresh
        ).bind_value_to(search_state, "query").classes("w-full md:w-128").props(f"outlined dense clearable color=brown text-sm debounce={SEARCH_DEBOUNCE}")
        
        #  Sorting parameter criteria dropdown selector
        ui.select(
            options=list(SORT_OPTIONS), 
            value=search_state.sort_by,
            label="Sort By",
            on_change=render_portfolio.refresh
        ).bind_value_to(search_state, "sort_by").classes("w-full md:w-48").props("outlined dense color=brown text-sm")

        ui.button(icon="add", text="Add", on_click=add_empty_item).props("flat color=brown rounded-full").classes("w-48 bg-amber-100")

    render_portfolio()
