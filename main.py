# -*- coding: utf-8 -*-
# filepath: /Users/braincraft/Desktop/demo-fp/multi-agent-competitor-analyzer/main.py
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


def search_competitors(company_input, location_input, progress=gr.Progress()):
    """Search for competitors and update dropdown"""
    if not company_input.strip():
        return (
            gr.Dropdown(choices=[], visible=False),
            gr.HTML(value="<p style='color: orange;'>Please enter a product or company name</p>", visible=True),
            gr.Button(interactive=True, value="Search Competitors"),
            gr.Button(interactive=False)
        )
    
    if is_url(company_input):
        return (
            gr.Dropdown(choices=[], visible=False),
            gr.HTML(value="<p style='color: blue;'>URL detected - Ready for direct website analysis</p>", visible=True),
            gr.Button(interactive=True, value="Search Competitors"),
            gr.Button(interactive=True, value="Analyze Website")
        )
    
    # Show progress for competitor search
    progress(0.1, desc="Starting competitor search...")
    progress(0.3, desc="Searching web for competitors...")
    
    try:
        competitors = update_competitor_dropdown(company_input, location_input)
        progress(0.8, desc="Processing competitor data...")
        
        if competitors:
            progress(1.0, desc="Competitor search complete!")
            success_msg = "<p style='color: green;'>Found " + str(len(competitors)) + " competitors for " + company_input + " in " + location_input + "</p>"
            return (
                gr.Dropdown(choices=competitors, visible=True, value=None),
                gr.HTML(value=success_msg, visible=True),
                gr.Button(interactive=True, value="Search Competitors"),
                gr.Button(interactive=False)
            )
        else:
            progress(1.0, desc="No competitors found")
            return (
                gr.Dropdown(choices=[], visible=False),
                gr.HTML(value="<p style='color: orange;'>No competitors found. Try a different company name or location.</p>", visible=True),
                gr.Button(interactive=True, value="Search Competitors"),
                gr.Button(interactive=False)
            )
    except Exception as e:
        progress(1.0, desc="Search failed")
        error_msg = "<p style='color: red;'>Error searching competitors: " + str(e) + "</p>"
        return (
            gr.Dropdown(choices=[], visible=False),
            gr.HTML(value=error_msg, visible=True),
            gr.Button(interactive=True, value="Search Competitors"),
            gr.Button(interactive=False)
        )


def analyze_competitor(company_input, location_input, selected_competitor, progress=gr.Progress()):
    """Generate competitor analysis"""
    if not company_input.strip():
        return gr.Textbox(value="Please enter a product or company name or website URL", visible=True)
    
    if is_url(company_input):
        # Direct URL analysis
        progress(0.1, desc="Analyzing website structure...")
        progress(0.3, desc="Extracting website data...")
        progress(0.6, desc="Generating AI insights...")
        try:
            analysis = generate_competitor_analysis_service(company_input, "")
            progress(1.0, desc="Website analysis complete!")
            return gr.Textbox(value=analysis, visible=True)
        except Exception as e:
            progress(1.0, desc="Analysis failed")
            error_msg = "Error analyzing website: " + str(e)
            return gr.Textbox(value=error_msg, visible=True)
    else:
        # Competitor analysis
        if not selected_competitor:
            return gr.Textbox(value="Please select a competitor from the dropdown", visible=True)
        
        progress(0.1, desc="Initializing competitor research...")
        progress(0.3, desc="Gathering competitor data...")
        progress(0.5, desc="Collecting market insights...")
        progress(0.7, desc="Generating AI analysis...")
        progress(0.9, desc="Finalizing report...")
        
        try:
            analysis = generate_competitor_analysis_service(company_input, selected_competitor)
            progress(1.0, desc="Competitor analysis complete!")
            return gr.Textbox(value=analysis, visible=True)
        except Exception as e:
            progress(1.0, desc="Analysis failed")
            error_msg = "Error generating analysis: " + str(e)
            return gr.Textbox(value=error_msg, visible=True)


def on_competitor_select(selected_competitor):
    """Handle competitor selection and enable analyze button"""
    if selected_competitor:
        return gr.Button(interactive=True, value="Generate Analysis")
    else:
        return gr.Button(interactive=False, value="Generate Analysis")


def clear_interface():
    """Clear all fields and reset interface"""
    return (
        "",  # company_input
        "Global",  # location_input
        gr.Dropdown(choices=[], visible=False, value=None),  # competitor_dropdown
        gr.HTML(value="", visible=False),  # status_message
        gr.Textbox(value="", visible=False),  # analysis_output
        gr.Button(interactive=True, value="Search Competitors"),  # search_btn
        gr.Button(interactive=False)  # analyze_btn
    )


# Custom CSS for better styling
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.instruction-box {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.step-box {
    background: #fff;
    border: 2px solid #e3f2fd;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: border-color 0.3s ease;
}

.step-box:hover {
    border-color: #2196f3;
}

/* Button styling */
.gr-button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* Status messages */
.gr-html p {
    font-size: 1.1rem;
    font-weight: 500;
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

/* Examples styling */
.gr-examples {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    background: #fafafa;
}

/* Analysis output styling */
.gr-html div[style*="background: #f0f8ff"] {
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    margin: 1rem 0 !important;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="🏢 AI Competitor Analyzer") as iface:
    
    # 1. INPUT FIELDS FIRST
    with gr.Row():
        with gr.Column(scale=2):
            company_input = gr.Textbox(
                label="Product or Company Name or Website URL",
                placeholder="Enter product/company name (e.g., Tesla, Apple) or website URL (https://...)",
                info="Enter either a product/company name to find competitors, or a direct website URL for immediate analysis"
            )
        
        with gr.Column(scale=1):
            location_input = gr.Dropdown(
                label="Target Market",
                choices=country_list,
                value="Global",
                info="Select the geographic market for competitor research"
            )
    
    # Status and competitor selection
    status_message = gr.HTML(visible=False)
    
    competitor_dropdown = gr.Dropdown(
        label="🎯 Select Competitor to Analyze",
        choices=[],
        visible=False,
        info="Choose a competitor from the list to generate detailed analysis"
    )
    
    # 2. BUTTONS SECOND
    with gr.Row():
        search_btn = gr.Button(
            "Search Competitors", 
            variant="primary", 
            size="lg",
            interactive=True
        )
        analyze_btn = gr.Button(
            "Generate Analysis", 
            variant="secondary", 
            size="lg",
            interactive=False
        )
        clear_btn = gr.Button(
            "Clear All", 
            variant="stop", 
            size="lg"
        )
    
    # 3. ANALYSIS REPORT VIEWER THIRD
    analysis_output = gr.Textbox(
        label="📊 Generated Analysis Report",
        value="",
        lines=20,
        max_lines=30,
        visible=False,
        interactive=False,
        show_copy_button=True,
        container=True
    )
    
    # Event handlers
    search_btn.click(
        search_competitors,
        inputs=[company_input, location_input],
        outputs=[competitor_dropdown, status_message, search_btn, analyze_btn]
    )
    
    # Enable analyze button when competitor is selected
    competitor_dropdown.change(
        on_competitor_select,
        inputs=[competitor_dropdown],
        outputs=[analyze_btn]
    )
    
    analyze_btn.click(
        analyze_competitor,
        inputs=[company_input, location_input, competitor_dropdown],
        outputs=[analysis_output]
    )
    
    clear_btn.click(
        clear_interface,
        outputs=[company_input, location_input, competitor_dropdown, status_message, analysis_output, search_btn, analyze_btn]
    )


if __name__ == "__main__":
    print("🚀 Launching AI Competitor Analyzer...")
    print("📍 Interface will be available at: http://localhost:7861")
    print("💡 Use Ctrl+C to stop the server")
    
    iface.launch(
        server_port=7861,
        server_name="0.0.0.0",
        show_api=False,
        share=False
    )
