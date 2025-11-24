from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

def verify_claims_with_gemini(text):
    api_key = os.environ.get("GEMINI_API_KEY")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API Key not found"}

    if not api_key:
        return {"claims": [], "error": "GEMINI_API_KEY not found in environment variables."}

    
    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash"
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Extract claims from this text and verify them. classify each claim in one of the following ways: True, False or Uncertain. Search internet for evidence supporting or opposing the claim. Return the response in JSON format. In json object return claim text, claim validity, sources used for verifying claim, confidence on verdict(range 1 to 100), category of claim (health, finance, sports, etc.). For each source provide source name, url, text from source used for verification, source credibility(range 0-100).  Also provide some reasoning to justify your verdict. Do not provide broken links for sources."""),
                types.Part.from_text(text=f"{text}"),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["claims"],
            properties={
                "claims": genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        required=["claim_text", "claim_validity", "sources_cited", "confidence", "reasoning", "category"],
                        properties={
                            "claim_text": genai.types.Schema(type=genai.types.Type.STRING),
                            "claim_validity": genai.types.Schema(type=genai.types.Type.STRING),
                            "category": genai.types.Schema(type=genai.types.Type.STRING),
                            "sources_cited": genai.types.Schema(
                                type=genai.types.Type.ARRAY,
                                items=genai.types.Schema(
                                    type=genai.types.Type.OBJECT,
                                    properties={
                                        "source_name": genai.types.Schema(type=genai.types.Type.STRING),
                                        "source_link": genai.types.Schema(type=genai.types.Type.STRING),
                                        "source_credibility": genai.types.Schema(type=genai.types.Type.INTEGER),
                                        "source_text": genai.types.Schema(type=genai.types.Type.STRING),
                                    },
                                ),
                            ),
                            "confidence": genai.types.Schema(type=genai.types.Type.INTEGER),
                            "reasoning": genai.types.Schema(type=genai.types.Type.STRING),
                        },
                    ),
                ),
            },
        ),
    )

    try:
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        full_response = ""
        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
        
        return json.loads(full_response)
    except Exception as e:
        print(f"LLM Error: {e}")
        return {"claims": [], "error": str(e)}