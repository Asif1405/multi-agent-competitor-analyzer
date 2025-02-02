import gradio as gr
from services.analyzer_services import generate_competitor_analysis_service, update_competitor_dropdown

def update_dropdown_options(company_input, location_input):
    """Handle UI state updates based on user input"""
    if company_input.startswith(("http://", "https://", "www.")):
        return {
            competitor_dropdown: gr.Dropdown(visible=False),
            status_message: gr.Markdown(visible=False),
            analysis_output: gr.Markdown(visible=True)
        }
    
    if not location_input:
        return {
            competitor_dropdown: gr.Dropdown(visible=False),
            status_message: gr.Markdown(value="📍 Please enter a location first", visible=True),
            analysis_output: gr.Markdown(visible=False)
        }
    
    competitors = update_competitor_dropdown(company_input, location_input)
    return {
        competitor_dropdown: gr.Dropdown(choices=competitors, visible=bool(competitors)),
        status_message: gr.Markdown(visible=False),
        analysis_output: gr.Markdown(visible=True)
    }

with gr.Blocks() as iface:
    with gr.Row():
        company_input = gr.Textbox(
            label="Product/Company Website",
            placeholder="Enter product name or company URL"
        )
        location_input = gr.Textbox(
            label="Location (Required for Products)",
            placeholder="Global or specific region"
        )
    
    competitor_dropdown = gr.Dropdown(
        label="Select Competitors",
        choices=[],
        visible=False,
        interactive=True
    )
    
    status_message = gr.Markdown(visible=False)
    
    analysis_output = gr.Markdown(
        value="## Enter product/website and location to begin analysis",
        visible=True
    )

    # Event handlers
    company_input.change(
        update_dropdown_options,
        inputs=[company_input, location_input],
        outputs=[competitor_dropdown, status_message, analysis_output]
    )
    
    location_input.change(
        update_dropdown_options,
        inputs=[company_input, location_input],
        outputs=[competitor_dropdown, status_message, analysis_output]
    )
    
    competitor_dropdown.change(
        generate_competitor_analysis_service,
        inputs=[company_input, competitor_dropdown],
        outputs=analysis_output
    )

iface.launch()
