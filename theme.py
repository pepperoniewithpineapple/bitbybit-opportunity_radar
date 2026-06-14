"""Shared warm design system for the Opportunity Radar NiceGUI app."""

from __future__ import annotations

from contextlib import contextmanager

from nicegui import ui


CANVAS = "#f7f1e7"
SURFACE = "#fffdf8"
SURFACE_SOFT = "#fbf4e9"
INK = "#2f2620"
INK_SOFT = "#5a4d41"
MUTED = "#8c7b69"
LINE = "#e9dcc7"
ACCENT = "#bd5d3a"
ACCENT_DEEP = "#a14d2e"
ACCENT_SOFT = "#f5e2d6"
GOOD = "#5f7d43"
WARN = "#a9742a"
BAD = "#a8432f"
INFO = "#9a6534"
GOOD_SOFT = "#eaf2e0"
WARN_SOFT = "#f5ead8"
BAD_SOFT = "#f5e0de"
INFO_SOFT = "#f0e8d8"


def apply_theme() -> None:
    """Apply the shared warm Opportunity Radar theme."""
    ui.add_head_html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..700&family=DM+Sans:wght@400;500;600;700&display=swap');

        :root {
            --canvas: #f7f1e7;
            --surface: #fffdf8;
            --surface-soft: #fbf4e9;
            --ink: #2f2620;
            --ink-soft: #5a4d41;
            --muted: #8c7b69;
            --line: #e9dcc7;
            --accent: #bd5d3a;
            --accent-deep: #a14d2e;
            --accent-soft: #f5e2d6;
            --good: #5f7d43;
            --warn: #a9742a;
            --bad: #a8432f;
            --info: #9a6534;
            --good-soft: #eaf2e0;
            --warn-soft: #f5ead8;
            --bad-soft: #f5e0de;
            --info-soft: #f0e8d8;
            --shadow-soft: 0 18px 44px -34px rgba(83, 57, 36, 0.44);
            --shadow-hover: 0 24px 54px -34px rgba(83, 57, 36, 0.54);
            --shadow-button: 0 14px 28px -20px rgba(161, 77, 46, 0.82);
            --radius-card: 18px;
            --radius-inner: 14px;
            --font-display: 'Fraunces', Georgia, 'Times New Roman', serif;
            --font-body: 'DM Sans', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        * {
            scrollbar-width: thin;
            scrollbar-color: var(--line) transparent;
        }

        ::-webkit-scrollbar {
            height: 10px;
            width: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--line);
            background-clip: content-box;
            border: 2px solid transparent;
            border-radius: 999px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #d9c7ab;
            background-clip: content-box;
        }

        body {
            background:
                radial-gradient(960px 520px at 14% -8%, rgba(255, 253, 248, 0.96) 0%, rgba(255, 253, 248, 0) 62%),
                radial-gradient(780px 440px at 92% 2%, rgba(245, 226, 214, 0.48) 0%, rgba(245, 226, 214, 0) 60%),
                linear-gradient(180deg, #faf4eb 0%, var(--canvas) 46%, #efe3d1 100%);
            background-attachment: fixed;
            color: var(--ink);
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
        }

        body,
        .q-page,
        .q-field__native,
        .q-field__label,
        .q-field__prefix,
        .q-field__suffix,
        .q-btn__content,
        .q-tab__label,
        .q-item__label,
        .q-checkbox__label,
        .q-toggle__label,
        .q-radio__label,
        .q-table,
        .q-menu,
        .q-tooltip,
        .nicegui-content,
        input,
        textarea,
        button {
            font-family: var(--font-body);
        }

        .q-page,
        .nicegui-content {
            background: transparent;
        }

        .text-slate-950,
        .text-slate-900 {
            color: var(--ink) !important;
        }

        .text-slate-700,
        .text-slate-600 {
            color: var(--ink-soft) !important;
        }

        .text-slate-500 {
            color: var(--muted) !important;
        }

        .text-emerald-700 {
            color: var(--good) !important;
        }

        .hero {
            background:
                radial-gradient(420px 260px at 92% 8%, rgba(189, 93, 58, 0.13), rgba(189, 93, 58, 0) 70%),
                linear-gradient(135deg, rgba(255, 253, 248, 0.98), rgba(251, 244, 233, 0.98));
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: var(--shadow-soft);
            overflow: hidden;
            position: relative;
        }

        .hero::before {
            background: linear-gradient(90deg, rgba(189, 93, 58, 0.34), rgba(95, 125, 67, 0.16), rgba(154, 101, 52, 0));
            content: "";
            height: 1px;
            inset: 0 24px auto;
            pointer-events: none;
            position: absolute;
        }

        .hero-mark {
            align-items: center;
            background: linear-gradient(135deg, var(--accent), var(--accent-deep));
            border: 1px solid rgba(255, 253, 248, 0.48);
            border-radius: 18px;
            box-shadow: 0 14px 28px -20px rgba(161, 77, 46, 0.95);
            color: #fff;
            display: inline-flex;
            font-size: 30px !important;
            height: 56px;
            justify-content: center;
            width: 56px;
        }

        .wordmark {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 2.38rem;
            font-weight: 650;
            letter-spacing: 0;
            line-height: 1.04;
        }

        .hero-subtitle {
            color: var(--ink-soft);
            font-size: 1.02rem;
            font-weight: 500;
            line-height: 1.55;
            max-width: 48ch;
        }

        .hero-badge {
            background: rgba(255, 253, 248, 0.72);
            border: 1px solid var(--line);
            border-radius: 999px;
            color: var(--accent-deep);
            font-size: 0.8rem;
            font-weight: 700;
            line-height: 1;
            padding: 10px 15px;
            white-space: nowrap;
        }

        .metric-card,
        .section-card,
        .inner-card,
        .opp-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-card);
            box-shadow: var(--shadow-soft);
            color: var(--ink);
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease, background-color .2s ease;
        }

        .metric-card {
            display: flex;
            flex-direction: column;
            gap: 3px;
            min-height: 122px;
            padding: 21px;
        }

        .section-card {
            padding: 24px;
            width: 100%;
        }

        .inner-card {
            background: var(--surface-soft);
            border-radius: var(--radius-inner);
            padding: 16px;
            width: 100%;
        }

        .opp-card {
            padding: 20px;
            width: 100%;
        }

        .metric-card:hover,
        .section-card:hover,
        .inner-card:hover,
        .opp-card:hover {
            border-color: #dfcdae;
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }

        .metric-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 2.16rem;
            font-weight: 650;
            line-height: 1;
        }

        .metric-label {
            color: var(--ink-soft);
            font-size: 0.9rem;
            font-weight: 700;
            line-height: 1.35;
            margin-top: 7px;
        }

        .metric-hint {
            color: var(--muted);
            font-size: 0.77rem;
            font-weight: 500;
            line-height: 1.4;
        }

        .section-title {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.22rem;
            font-weight: 650;
            letter-spacing: 0;
            line-height: 1.16;
            margin-bottom: 1rem;
            padding-left: 13px;
            position: relative;
        }

        .section-title::before {
            background: linear-gradient(180deg, var(--accent), var(--accent-deep));
            border-radius: 999px;
            content: "";
            inset: 0.17em auto 0.17em 0;
            position: absolute;
            width: 4px;
        }

        .side-panel {
            max-width: 360px;
            width: 100%;
        }

        .content-panel {
            flex: 1 1 0;
            gap: 1rem;
            min-width: 0;
        }

        .primary-button,
        .soft-button,
        .danger-button {
            border-radius: 999px;
            font-weight: 700;
            min-height: 38px;
            text-decoration: none;
            text-transform: none;
            transition: transform .2s ease, box-shadow .2s ease, background-color .2s ease, border-color .2s ease, filter .2s ease;
        }

        .primary-button {
            background: linear-gradient(135deg, var(--accent), var(--accent-deep)) !important;
            border: 1px solid rgba(161, 77, 46, 0.18) !important;
            box-shadow: var(--shadow-button) !important;
            color: #fff !important;
        }

        .primary-button:hover {
            box-shadow: 0 18px 34px -20px rgba(161, 77, 46, 0.95) !important;
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        .soft-button {
            background: var(--surface-soft) !important;
            border: 1px solid var(--line) !important;
            box-shadow: none !important;
            color: var(--accent-deep) !important;
            padding: 8px 15px;
        }

        .soft-button:hover {
            background: var(--accent-soft) !important;
            border-color: #dec2a8 !important;
            transform: translateY(-1px);
        }

        .danger-button {
            background: var(--bad-soft) !important;
            border: 1px solid #e7beb8 !important;
            box-shadow: none !important;
            color: var(--bad) !important;
        }

        .danger-button:hover {
            background: #efcfca !important;
            border-color: #dda9a0 !important;
            transform: translateY(-1px);
        }

        .radar-badge {
            border: 1px solid transparent;
            border-radius: 999px;
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 700;
            line-height: 1.35;
            padding: 4px 11px;
            white-space: nowrap;
        }

        .radar-badge--neutral {
            background: var(--surface-soft);
            border-color: var(--line);
            color: var(--ink-soft);
        }

        .radar-badge--good {
            background: var(--good-soft);
            border-color: #d8e5cb;
            color: var(--good);
        }

        .radar-badge--warn {
            background: var(--warn-soft);
            border-color: #ecd6b6;
            color: var(--warn);
        }

        .radar-badge--bad {
            background: var(--bad-soft);
            border-color: #e9c4bf;
            color: var(--bad);
        }

        .radar-badge--info {
            background: var(--info-soft);
            border-color: #e3d2b9;
            color: var(--info);
        }

        .clean-tabs {
            background: rgba(255, 253, 248, 0.78);
            border: 1px solid var(--line);
            border-radius: 999px;
            box-shadow: var(--shadow-soft);
            max-width: 100%;
            overflow-x: auto;
            padding: 6px;
        }

        .clean-tabs .q-tabs__content {
            min-width: max-content;
        }

        .clean-tabs .q-tab {
            border-radius: 999px;
            color: var(--ink-soft);
            min-height: 40px;
            padding: 0 18px;
            text-transform: none;
            transition: background-color .2s ease, color .2s ease, box-shadow .2s ease;
        }

        .clean-tabs .q-tab:hover {
            color: var(--accent-deep);
        }

        .clean-tabs .q-tab--active {
            background: linear-gradient(135deg, var(--accent), var(--accent-deep));
            box-shadow: 0 14px 26px -20px rgba(161, 77, 46, 0.92);
            color: #fff !important;
        }

        .clean-tabs .q-tab--active .q-icon,
        .clean-tabs .q-tab--active .q-tab__label {
            color: #fff !important;
        }

        .clean-tabs .q-tab__indicator {
            display: none;
        }

        .clean-tabs .q-tab__content {
            gap: 7px;
        }

        .clean-tabs .q-tab__icon,
        .clean-tabs .q-icon {
            font-size: 19px;
        }

        .clean-tabs .q-tab__label {
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: none;
        }

        .q-tab-panels,
        .q-tab-panel {
            background: transparent !important;
        }

        @keyframes radar-rise {
            from {
                opacity: 0;
                transform: translateY(8px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .q-tab-panel > * {
            animation: radar-rise .32s ease both;
        }

        .q-field__label {
            color: var(--muted);
            font-weight: 500;
        }

        .q-field--focused .q-field__label {
            color: var(--accent-deep);
        }

        .q-field--outlined .q-field__control::before {
            border-color: var(--line);
        }

        .q-field--outlined.q-field--focused .q-field__control::after {
            border-color: var(--accent);
        }

        .q-expansion-item {
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-radius: var(--radius-inner);
            margin-bottom: 8px;
            overflow: hidden;
        }

        .q-linear-progress {
            border-radius: 999px;
            color: var(--accent);
            height: 8px !important;
            overflow: hidden;
        }

        .q-linear-progress__track {
            color: var(--accent-soft);
        }

        .q-separator {
            background: var(--line) !important;
        }

        .empty-state {
            background: rgba(255, 253, 248, 0.6);
            border: 1.5px dashed var(--line);
            border-radius: var(--radius-inner);
            color: var(--muted);
            padding: 1.5rem;
            text-align: center;
            width: 100%;
        }

        @media (max-width: 900px) {
            .side-panel {
                max-width: none;
            }

            .content-panel {
                flex-basis: 100%;
            }

            .hero {
                padding: 22px !important;
            }

            .hero .q-row {
                align-items: flex-start;
            }

            .hero-mark {
                border-radius: 16px;
                font-size: 26px !important;
                height: 50px;
                width: 50px;
            }

            .wordmark {
                font-size: 1.86rem;
            }

            .hero-subtitle {
                font-size: 0.96rem;
            }

            .hero-badge {
                margin-top: 10px;
                white-space: normal;
            }

            .metric-card {
                min-height: 0;
                padding: 18px;
            }

            .section-card,
            .opp-card {
                padding: 18px;
            }

            .clean-tabs .q-tab {
                padding: 0 14px;
            }
        }

        .border-slate-100 {
            border-color: var(--line) !important;
        }

        .border-slate-200 {
            border-color: var(--line) !important;
        }

        .primary-button:focus-visible,
        .soft-button:focus-visible,
        .danger-button:focus-visible,
        .clean-tabs .q-tab:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }

        .primary-button:active,
        .soft-button:active,
        .danger-button:active {
            transform: translateY(0);
        }

        img,
        svg,
        canvas {
            max-width: 100%;
        }

        @media (max-width: 820px) {
            [class*='radar-grid-2'] {
                grid-template-columns: 1fr !important;
            }
        }

        @media (max-width: 600px) {
            .clean-tabs .q-tab {
                padding-left: 8px;
                padding-right: 8px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: .001ms !important;
                transition-duration: .001ms !important;
            }

            .q-tab-panel > * {
                animation: none !important;
            }
        }
        </style>
        """
    )
    ui.colors(
        primary="#bd5d3a",
        secondary="#5f7d43",
        accent="#9a6534",
        positive="#5f7d43",
        negative="#a8432f",
        warning="#a9742a",
        info="#9a6534",
    )


def badge(text: str, tone: str = "neutral") -> ui.label:
    return ui.label(text).classes(f"radar-badge radar-badge--{tone}")


def stat_card(label: str, value: str, hint: str) -> None:
    with ui.card().classes("metric-card"):
        ui.label(value).classes("metric-value")
        ui.label(label).classes("metric-label")
        ui.label(hint).classes("metric-hint")


@contextmanager
def section_card(title: str | None = None):
    with ui.card().classes("section-card") as card:
        if title:
            ui.label(title).classes("section-title")
        yield card


@contextmanager
def inner_card():
    with ui.card().classes("inner-card") as card:
        yield card


@contextmanager
def page_container():
    with ui.column().classes("max-w-7xl mx-auto px-4 py-6 gap-6 w-full") as col:
        yield col


def primary_button(text: str, icon: str | None = None, on_click=None) -> ui.button:
    kwargs = {}
    if icon is not None:
        kwargs["icon"] = icon
    if on_click is not None:
        kwargs["on_click"] = on_click
    return ui.button(text, **kwargs).classes("primary-button")


def soft_button(text: str, icon: str | None = None, on_click=None) -> ui.button:
    kwargs = {}
    if icon is not None:
        kwargs["icon"] = icon
    if on_click is not None:
        kwargs["on_click"] = on_click
    return ui.button(text, **kwargs).classes("soft-button")


def danger_button(text: str, icon: str | None = None, on_click=None) -> ui.button:
    kwargs = {}
    if icon is not None:
        kwargs["icon"] = icon
    if on_click is not None:
        kwargs["on_click"] = on_click
    return ui.button(text, **kwargs).classes("danger-button")


def hero(title: str, subtitle: str, badge_text: str) -> None:
    with ui.card().classes("hero w-full p-8"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("radar").classes("hero-mark")
                with ui.column().classes("gap-1"):
                    ui.label(title).classes("wordmark")
                    ui.label(subtitle).classes("hero-subtitle")
            ui.label(badge_text).classes("hero-badge")
