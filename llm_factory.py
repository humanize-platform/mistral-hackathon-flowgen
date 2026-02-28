import os
import re
import sys
from mistralai import Mistral

from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class LLMFactory:

    @staticmethod
    def invoke_mistral_agent(agent_id: str, prompt: str, api_key: str) -> str:
        """
        Invoke a Mistral agent with the given agent_id and prompt, returning the response content.
        """
        client = Mistral(api_key)
        print(prompt)
        agent_response = client.agents.complete(
            messages=[
                {
                    "content": prompt,
                    "role": "user",
                },
            ],
            agent_id=agent_id,
            stream=False,
        )

        if not agent_response.choices[0]:
            raise ValueError("No outputs found in Mistral agent response")
        return agent_response

    @staticmethod
    def invoke_mistral(
        system_prompt: str = None,
        human_message: str = None,
    ):
        """
        Invoke the Mistral LLM with given prompts using ChatPromptTemplate and return
        the final agent response.
        """
        load_dotenv(override=True)
        api_key = os.getenv("MISTRAL_API_KEY")
        flowgen_agent_id = os.getenv("MISTRAL_FLOWGEN_AGENT_ID")
        flowanalyst_agent_id = os.getenv("MISTRAL_FLOWANALYST_AGENT_ID")

        if system_prompt and human_message:
            system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")
            human_message = human_message.replace("{", "{{").replace("}", "}}")
            prompt_obj = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(human_message),
                ]
            )
            formatted_messages = prompt_obj.format_messages()
            prompt = "\n".join([msg.content for msg in formatted_messages])
            first_resp = LLMFactory.invoke_mistral_agent(
                agent_id=flowanalyst_agent_id, prompt=prompt, api_key=api_key
            )
            raw_content = first_resp.choices[0].message.content
            if raw_content.startswith("xml"):
                cleaned = re.sub(r"^xml\s*", "", raw_content)
                cleaned = re.sub(r"\s*$", "", cleaned)
                updated_prompt = cleaned.strip()
            else:
                updated_prompt = raw_content.strip()
            second_resp = LLMFactory.invoke_mistral_agent(
                agent_id=flowgen_agent_id, prompt=updated_prompt, api_key=api_key
            )
            return second_resp

        elif human_message:
            human_message = human_message.replace("{", "{{").replace("}", "}}")
            first_resp = LLMFactory.invoke_mistral_agent(
                agent_id=flowanalyst_agent_id, prompt=human_message, api_key=api_key
            )
            raw_content = first_resp.choices[0].message.content
            if raw_content.startswith("xml"):
                cleaned = re.sub(r"^xml\s*", "", raw_content)
                cleaned = re.sub(r"\s*```$", "", cleaned)
                updated_prompt = cleaned.strip()
            else:
                updated_prompt = raw_content.strip()
            second_resp = LLMFactory.invoke_mistral_agent(
                agent_id=flowgen_agent_id, prompt=updated_prompt, api_key=api_key
            )
            return second_resp

        else:
            raise ValueError("At least a human_message must be provided.")
