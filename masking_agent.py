from typing import Dict, TypedDict, Annotated, Sequence
import operator
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from entities import TransformedData, ReflectionOuput
from prompts import pii_prompt_template, pii_reflect_template
from langchain.pydantic_v1 import BaseModel, Field
from textwrap import dedent


class ReflectionOuput(BaseModel):
    review: str = Field(default="n/a", description="Review of the TransformedData as to how well it aligns with the expected format")
    recommendations: str = Field(default="n/a", description="Actionable recommendations formatted as a multiline string containing bulleted list of necessary changes to align with original formatting instructions and improvement if needed for any attribute. Use examples as needed. If the TransformedData matches all requirements say so.")
    feedback: str = Field(default="n/a", description="'perfect' if no changes are required, or 'needs work' otherwise")
    
    
class GraphState(TypedDict):
    model_choice: str
    original_text: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    reflection_status: str
    transformed_data: TransformedData
    generation_quality: str


class PIITagger:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=TransformedData)
        self.wf = self._create_workflow()

    def _model_from_selection(self, model_selection: str) -> ChatOpenAI:
        """
        Initializes and returns the chat model for the selected LLM.

        Args:
            model_selection (str): The name of the selected model.

        Returns:
            ChatOpenAI: The initialized chat model.
        """
        temperature = 0.0
        model_dict: Dict[str, ChatOpenAI] = {
            "GPT 3.5": ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=temperature),
            "GPT 4": ChatOpenAI(model_name="gpt-4-0125-preview", temperature=temperature),
        }
        return model_dict[model_selection]
    

    def _prompt(self, state: GraphState) -> Dict:
        """
        Generates a prompt for tagging PII using the pii_prompt_template

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            Dict: The updated state with the generated prompt.
        """
        prompt = ChatPromptTemplate.from_messages(messages=pii_prompt_template)
        input_data = {
            "text": state["original_text"],
            "format_instructions": self.parser.get_format_instructions()
        }
        response = prompt.invoke(input_data)
        return {
            "messages": response.messages,
            "model_choice": state["model_choice"],
            "reflection_status": "n/a",
            "generation_quality": 'n/a'
        }


    def _generate(self, state: GraphState) -> Dict:
        """
        Invoke LLM to identify PII and apply tags as specified in the prompt and TransformedData

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            Dict: The updated state with the generated transformed data.
        """
        messages = state['messages']
        model_choice = state['model_choice']
        llm = self._model_from_selection(model_choice)
        chain = llm | self.parser
        response = chain.invoke(messages)
        # print(f"** generate ** response:\n{response}")
        return {
            "messages": [AIMessage(content=json.dumps(response.dict(), indent=4))],
            "transformed_data": response
        }


    def _reflect(self, state: GraphState) -> Dict:
        """
        Reflects on the generated transformed data and updates the generation quality.

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            Dict: The updated state with the reflection status and generation quality.
        """
        messages = state["messages"]
        model_choice = state['model_choice']
        generation_quality = state["generation_quality"]
        llm = self._model_from_selection(model_choice)
        prompt = ChatPromptTemplate.from_messages(
            messages=[
                *messages,
                ("human", pii_reflect_template)
            ]
        )
        parser = PydanticOutputParser(pydantic_object=ReflectionOuput)
        chain = prompt | llm | parser
        input = {
            "format_instructions": parser.get_format_instructions()
        }
        response = chain.invoke(input)
        print(f"response: '{response}'")
        
        review = response.review
        feedback = response.feedback
        recommendations = response.recommendations
        
        if feedback == 'perfect':
            generation_quality = 'perfect'
        else:
            generation_quality = 'needs rework'
        
        message = HumanMessage(content=dedent(f"""
                Here is the review of TransfrmedData.
                {review}
                
                Recommendations:
                {recommendations}
                
                Feedback: {feedback}
            """)
        )
        
        return {
            "messages": [message],
            "reflection_status": "completed",
            "generation_quality": generation_quality
        }
        

    def _should_reflect(self, state: GraphState) -> str:
        """
        Determines whether to reflect or end the graph based on the reflection status.

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            str: The next action to take ('reflect' or 'end').
        """
        reflection_status = state["reflection_status"]
        if reflection_status != "completed":
            return "reflect"
        return "end"
    

    def _should_generate(self, state: GraphState) -> str:
        """
        Determines whether to generate or end the graph based on the generation quality.

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            str: The next action to take ('generate' or 'end').
        """
        generation_quality = state["generation_quality"]
        if generation_quality != "perfect":
            return "generate"
        return "end"

    def _create_workflow(self) -> StateGraph:
        """
        Creates the graph.

        Returns:
            StateGraph: The created workflow graph.
        """
        g = StateGraph(GraphState)
        g.add_node("prompt", self._prompt)
        g.set_entry_point("prompt")
        g.add_node("generate", self._generate)
        g.add_edge("prompt", "generate")
        g.add_node("reflect", self._reflect)
        g.add_conditional_edges(
            "generate",
            self._should_reflect,
            {
                "reflect": "reflect",
                "end": END
            }
        )
        g.add_conditional_edges(
            "reflect",
            self._should_generate,
            {
                "generate": "generate",
                "end": END
            }
        )
        return g.compile()

    def tag_pii_elements(self, model_choice, input_text) -> Dict:
        """
        Transforms PII in the given input text.

        Args:
            input_data (Dict): The input data containing the original text and model choice.

        Returns:
            Dict: The transformed data.
        """
        input = {
            "original_text": input_text,
            "model_choice": model_choice
        }
        response = self.wf.invoke(input)
        return response


if __name__ == "__main__":
    transformer = PIITagger()
    response = transformer.tag_pii_elements("GPT 3.5", "john lives in montanna, and works at CVS pharmacy.")
    print(f"response:messages\n{response['messages']}")
    