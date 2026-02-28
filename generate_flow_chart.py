import os
import re
import sys
import tempfile
from datetime import datetime
import time
from uuid import uuid4
import json

from llm_factory import LLMFactory


def get_flow_code(file_content: str) -> str:
    try:

        messages = file_content.strip()

        print("Generating flow diagram code using Mistral Agent")
        response = LLMFactory.invoke_mistral(
            human_message=messages,
        )
        raw_response = response.choices[0].message.content.strip()
        if raw_response.startswith("xml"):
            flow_code = re.sub(r"^xml\s*", "", raw_response)
            flow_code = re.sub(r"\s*$", "", flow_code)
        else:
            flow_code = raw_response
        print("Flow diagram code generated successfully.")
        match = re.search(r"<mxfile.*?</mxfile>", flow_code, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("No valid <mxfile> XML found in the LLM output.")

    except Exception as e:
        # Reraise the exception to trigger retry logic
        raise e


def generate_flow_chart(file_content: str) -> str:
    """
    Generates a flow diagram XML from the provided text content.

    Parameters:
      - file_content: The text/markdown content to generate a flow chart from.

    Returns:
      - The generated Draw.io XML string.
    """
    # Generate Draw.io XML
    try:
        final_xml = get_flow_code(file_content)
    except Exception as e:
        raise Exception(f"Error generating flow diagram code: {e}") from e

    return final_xml