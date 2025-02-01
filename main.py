import gradio as gr

from services.analyzer_services import generate_competitor_analysis_service

# Create Gradio interface
iface = gr.Interface(
    fn=generate_competitor_analysis_service,
    inputs=[
        gr.Textbox(label="Enter Product or Company Website", placeholder="Enter product or company website URL"),
        gr.Textbox(label="Enter Country or Location (Optional)", placeholder="e.g. Global or specific region"),
        gr.Slider(label="Max Competitors to Analyze", minimum=1, maximum=10, step=1)
    ],
    outputs=gr.Markdown(),
    title="Competitor Analysis Tool",
    description="Provide a product or company website to analyze its competitors. Set the number of competitors to analyze."
)

iface.launch(debug=True)
