import gradio as gr
import pycountry

from services.analyzer_services import generate_competitor_analysis_service, update_competitor_dropdown


def get_country_names():
    countries = [("Global", "Global")]
    for country in pycountry.countries:
        countries.append((country.name, country.name))
    return countries


country_list = get_country_names()


def is_url(input_str):
    """Check if input is a URL"""
    return input_str.startswith(("http://", "https://", "www."))


def update_dropdown_options(company_input, location_input):
    """Reset UI state when inputs change"""
    return {
        competitor_dropdown: gr.Dropdown(
            visible=False, value=None, choices=[]), status_message: gr.Markdown(
            visible=False), analysis_output: gr.Markdown(
                value="", visible=False), loading: gr.Markdown(
                    visible=False)}


def handle_competitor_search(company_input, location_input):
    """Fetch and display competitors"""
    if is_url(company_input) or not company_input or location_input == "Global":
        return gr.Dropdown(visible=False)

    try:
        competitors = update_competitor_dropdown(company_input, location_input)
        return gr.Dropdown(
            choices=competitors,
            visible=bool(competitors),
            interactive=True
        )
    except Exception as e:
        print(f"Error fetching competitors: {e}")
        return gr.Dropdown(visible=False)


def handle_analysis(company_input, location_input, selected_competitor):
    """Handle analysis generation with proper loading states"""
    yield gr.Markdown(value="## 🔍 Analyzing...", visible=True), gr.Markdown(visible=False)

    try:
        if is_url(company_input):
            # Direct URL analysis
            analysis = generate_competitor_analysis_service(company_input, "")
        else:
            # Competitor-based analysis
            if not selected_competitor:
                return
            analysis = generate_competitor_analysis_service(
                company_input, selected_competitor)

        yield gr.Markdown(visible=False), gr.Markdown(value=analysis, visible=True)

    except Exception as e:
        print(f"Analysis error: {e}")
        yield gr.Markdown(visible=False), gr.Markdown(value=f"Error generating analysis: {str(e)}", visible=True)


with gr.Blocks(theme=gr.themes.Default()) as iface:
    with gr.Row():
        company_input = gr.Textbox(
            label="Product/Company Website",
            placeholder="Enter product name or company URL",
            interactive=True
        )
        location_input = gr.Dropdown(
            label="Select Country/Region",
            choices=country_list,
            value="Global",
            interactive=True
        )

    competitor_dropdown = gr.Dropdown(
        label="Select Competitors",
        choices=[],
        visible=False,
        interactive=True
    )

    status_message = gr.Markdown(visible=False)
    loading = gr.Markdown(visible=False)
    analysis_output = gr.Markdown(visible=False)

    # Input change handlers
    company_input.change(
        update_dropdown_options,
        inputs=[company_input, location_input],
        outputs=[competitor_dropdown, status_message, analysis_output, loading]
    ).then(
        handle_competitor_search,
        inputs=[company_input, location_input],
        outputs=competitor_dropdown
    )

    location_input.change(
        update_dropdown_options,
        inputs=[company_input, location_input],
        outputs=[competitor_dropdown, status_message, analysis_output, loading]
    ).then(
        handle_competitor_search,
        inputs=[company_input, location_input],
        outputs=competitor_dropdown
    )

    inputs = [company_input, location_input, competitor_dropdown]
    company_input.submit(
        handle_analysis,
        inputs=inputs,
        outputs=[loading, analysis_output]
    )
    competitor_dropdown.change(
        handle_analysis,
        inputs=inputs,
        outputs=[loading, analysis_output]
    )

iface.launch(server_port=8090, server_name="0.0.0.0")
