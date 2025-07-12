from langgraph.graph import StateGraph, END
from .state import CompetitorAnalysisState
from .nodes import CompetitorAnalysisNodes


class CompetitorAnalysisWorkflow:
    """LangGraph workflow for competitor analysis."""
    
    def __init__(self):
        self.nodes = CompetitorAnalysisNodes()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Creates and configures the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(CompetitorAnalysisState)
        
        # Add nodes
        workflow.add_node("input_classifier", self.nodes.input_classifier_node)
        workflow.add_node("competitor_search", self.nodes.competitor_search_node)
        workflow.add_node("competitor_selection", self.nodes.competitor_selection_node)
        workflow.add_node("website_analysis", self.nodes.website_analysis_node)
        workflow.add_node("data_collection", self.nodes.data_collection_node)
        workflow.add_node("analysis_generation", self.nodes.analysis_generation_node)
        workflow.add_node("error", self.nodes.error_node)
        
        # Set entry point
        workflow.set_entry_point("input_classifier")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "input_classifier",
            self.nodes.should_continue,
            {
                "competitor_search": "competitor_search",
                "website_analysis": "website_analysis",
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "competitor_search",
            self.nodes.should_continue,
            {
                "competitor_selection": "competitor_selection",
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "competitor_selection",
            self.nodes.should_continue,
            {
                "data_collection": "data_collection",
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "website_analysis",
            self.nodes.should_continue,
            {
                "data_collection": "data_collection",
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "data_collection",
            self.nodes.should_continue,
            {
                "analysis_generation": "analysis_generation",
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "analysis_generation",
            self.nodes.should_continue,
            {
                "error": "error",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "error",
            self.nodes.should_continue,
            {
                "end": END
            }
        )
        
        return workflow.compile()
    
    def run_analysis(
        self,
        company_name_or_website: str,
        location: str = "global",
        selected_competitor: str = None
    ) -> CompetitorAnalysisState:
        """
        Runs the competitor analysis workflow.
        
        Args:
            company_name_or_website: Company name or website URL
            location: Geographic location for competitor search
            selected_competitor: Specific competitor to analyze
            
        Returns:
            Final state with analysis results
        """
        initial_state = CompetitorAnalysisState(
            company_name_or_website=company_name_or_website,
            location=location,
            selected_competitor=selected_competitor,
            is_website_input=False,
            search_urls=[],
            competitor_names=[],
            target_company="",
            company_website=None,
            company_data={},
            external_data={},
            analysis_report="",
            error_message=None,
            next_step="",
            workflow_completed=False
        )
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        return final_state
    
    def get_competitors(
        self,
        company_name: str,
        location: str = "global"
    ) -> list[str]:
        """
        Gets list of competitors for dropdown population.
        
        Args:
            company_name: Company name to search competitors for
            location: Geographic location for search
            
        Returns:
            List of competitor names
        """
        if company_name.startswith(("http://", "https://", "www.")):
            return []
        
        if not location:
            return []
        
        # Run partial workflow to get competitors
        initial_state = CompetitorAnalysisState(
            company_name_or_website=company_name,
            location=location,
            selected_competitor=None,
            is_website_input=False,
            search_urls=[],
            competitor_names=[],
            target_company="",
            company_website=None,
            company_data={},
            external_data={},
            analysis_report="",
            error_message=None,
            next_step="",
            workflow_completed=False
        )
        
        # Run only the competitor search portion
        nodes = CompetitorAnalysisNodes()
        classified_state = nodes.input_classifier_node(initial_state)
        
        if classified_state.get("next_step") == "competitor_search":
            # Update state with classification results
            updated_state = {**initial_state, **classified_state}
            search_result = nodes.competitor_search_node(updated_state)
            return search_result.get("competitor_names", [])
        
        return []
