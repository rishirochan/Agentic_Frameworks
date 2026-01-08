import gradio as gr
from sidekick import Sidekick

# Mode configurations
MODES = {
    "🗓️ Calendar": {
        "show_criteria": False,
        "default_criteria": "Complete the calendar task accurately",
        "placeholder": "Schedule a meeting, check availability, or manage events..."
    },
    "🔍 Research": {
        "show_criteria": True,
        "default_criteria": "Provide comprehensive and accurate information",
        "placeholder": "Research a topic, find information..."
    },
    "💻 Code": {
        "show_criteria": True,
        "default_criteria": "Code should work correctly and be well-documented",
        "placeholder": "Write code, run scripts, solve programming problems..."
    }
}


async def setup():
    sidekick = Sidekick()
    await sidekick.setup()
    return sidekick


async def process_message(sidekick, message, success_criteria, mode, history):
    """Process a message and return results"""
    if not message or not message.strip():
        return history, sidekick, ""
    if not success_criteria:
        success_criteria = MODES[mode]["default_criteria"]
    results = await sidekick.run_superstep(message, success_criteria, history)
    return results, sidekick, ""


async def run_quick_action(sidekick, query, mode, history):
    """Run a quick action immediately"""
    success_criteria = MODES[mode]["default_criteria"]
    results = await sidekick.run_superstep(query, success_criteria, history)
    return results, sidekick


async def run_quick_add(sidekick, title, date, time, duration, mode, history):
    """Run quick add with form data"""
    if not title or not date or not time:
        error_msg = {"role": "assistant", "content": "⚠️ Please fill in Title, Date, and Time fields."}
        return history + [error_msg], sidekick
    
    query = f"Schedule a meeting called '{title}' on {date} at {time} for {duration} minutes"
    success_criteria = MODES[mode]["default_criteria"]
    results = await sidekick.run_superstep(query, success_criteria, history)
    return results, sidekick


async def reset(mode):
    new_sidekick = Sidekick()
    await new_sidekick.setup()
    return "", "", None, new_sidekick


def on_mode_change(mode):
    """Toggle success criteria visibility based on mode"""
    config = MODES[mode]
    return (
        gr.update(visible=config["show_criteria"]),
        gr.update(placeholder=config["placeholder"]),
        config["default_criteria"] if config["show_criteria"] else ""
    )


def free_resources(sidekick):
    print("Cleaning up")
    try:
        if sidekick:
            sidekick.cleanup()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


# Load CSS from external file
with open("styles.css", "r") as f:
    custom_css = f.read()

with gr.Blocks(
    title="PlannerPA", 
    theme=gr.themes.Soft(primary_hue="emerald", neutral_hue="slate"),
    css=custom_css
) as ui:
    
    # Header
    gr.Markdown("# 🚀 PlannerPA Sidekick")
    gr.Markdown("Your AI-powered personal assistant for scheduling, research, and coding.")
    
    # State
    sidekick = gr.State(delete_callback=free_resources)
    current_mode = gr.State(value="🗓️ Calendar")
    
    # Mode Tabs
    with gr.Row(elem_classes="mode-tabs"):
        mode_selector = gr.Radio(
            choices=list(MODES.keys()),
            value="🗓️ Calendar",
            label="Mode",
            interactive=True
        )
    
    # Quick Actions (Calendar mode only)
    with gr.Row(elem_classes="quick-actions", visible=True) as quick_actions_row:
        gr.Markdown("**Quick Actions:**")
        today_btn = gr.Button("📋 Today's Agenda", size="sm")
        add_btn = gr.Button("➕ Quick Add", size="sm")
        free_btn = gr.Button("🔍 Find Free Time", size="sm")
    
    # Quick Add Form (hidden by default)
    with gr.Group(visible=False) as quick_add_form:
        gr.Markdown("### ➕ Quick Add Event")
        with gr.Row():
            event_title = gr.Textbox(label="Event Title", placeholder="Team Meeting")
            event_date = gr.Textbox(label="Date", placeholder="2026-01-08 or tomorrow")
        with gr.Row():
            event_time = gr.Textbox(label="Time", placeholder="14:00")
            event_duration = gr.Dropdown(
                label="Duration",
                choices=["15", "30", "45", "60", "90", "120"],
                value="60"
            )
        with gr.Row():
            cancel_add_btn = gr.Button("Cancel", size="sm")
            confirm_add_btn = gr.Button("Create Event", size="sm", variant="primary")
    
    # Chat Area
    chatbot = gr.Chatbot(
        label="Conversation",
        height=350,
        type="messages",
        show_copy_button=True
    )
    
    # Input Area
    with gr.Group():
        message = gr.Textbox(
            show_label=False,
            placeholder=MODES["🗓️ Calendar"]["placeholder"],
            lines=2
        )
        success_criteria = gr.Textbox(
            show_label=False,
            placeholder="Success criteria (what makes this task complete?)",
            visible=False,
            lines=1
        )
    
    # Action Buttons
    with gr.Row():
        reset_button = gr.Button("🔄 Reset", variant="stop")
        go_button = gr.Button("📨 Send", variant="primary")
    
    # Event Handlers
    ui.load(setup, [], [sidekick])
    
    # Mode switching
    mode_selector.change(
        on_mode_change,
        [mode_selector],
        [success_criteria, message, success_criteria]
    ).then(
        lambda m: gr.update(visible=(m == "🗓️ Calendar")),
        [mode_selector],
        [quick_actions_row]
    ).then(
        lambda m: m,
        [mode_selector],
        [current_mode]
    )
    
    # Quick action: Today's Agenda - runs immediately
    today_btn.click(
        run_quick_action,
        [sidekick, gr.State("What's on my calendar today?"), current_mode, chatbot],
        [chatbot, sidekick]
    )
    
    # Quick action: Find Free Time - runs immediately
    free_btn.click(
        run_quick_action,
        [sidekick, gr.State("When am I free tomorrow?"), current_mode, chatbot],
        [chatbot, sidekick]
    )
    
    # Quick action: Quick Add - shows form
    add_btn.click(
        lambda: gr.update(visible=True),
        [],
        [quick_add_form]
    )
    
    # Quick Add form handlers
    cancel_add_btn.click(
        lambda: (gr.update(visible=False), "", "", "", "60"),
        [],
        [quick_add_form, event_title, event_date, event_time, event_duration]
    )
    
    confirm_add_btn.click(
        run_quick_add,
        [sidekick, event_title, event_date, event_time, event_duration, current_mode, chatbot],
        [chatbot, sidekick]
    ).then(
        lambda: (gr.update(visible=False), "", "", "", "60"),
        [],
        [quick_add_form, event_title, event_date, event_time, event_duration]
    )
    
    # Message submission
    message.submit(
        process_message,
        [sidekick, message, success_criteria, current_mode, chatbot],
        [chatbot, sidekick, message]
    )
    go_button.click(
        process_message,
        [sidekick, message, success_criteria, current_mode, chatbot],
        [chatbot, sidekick, message]
    )
    reset_button.click(
        reset,
        [current_mode],
        [message, success_criteria, chatbot, sidekick]
    )


ui.launch(inbrowser=True)
