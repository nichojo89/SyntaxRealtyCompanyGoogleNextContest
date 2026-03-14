import asyncio
import re
import webbrowser

from home_purchase_lead_gen_agent.phone_call_agent_as_tool.main import call
from home_purchase_lead_gen_agent.phone_call_agent_as_tool.models.fsbo_prompt_parameters import FSBOPromptParameters


def open_url(url: str) -> str:
    """
    Use this tool whenever the user asks to open a website, visit a webpage, go to a specific link, or view a property listing in their browser.

    Args:
        url (str): The exact web address to open. MUST be a raw, fully qualified URL starting with 'https://'.
            Do NOT wrap the URL in markdown format (e.g., never send [Google](https://google.com), just send 'https://www.google.com').
            If the user asks to open a known website by its name (e.g., 'Open Zillow' or 'Go to Syntax Realty'),
            you must infer the proper URL and pass the raw web address.
    """
    # Sanitize common LLM URL mistakes
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    url = url.replace("https.", "https://").replace("http.", "http://")

    webbrowser.open(url)
    return f"Successfully opened {url} in the default browser."


async def initiate_phone_call(
        phone_number: str,
        sale_property_address: str,
        available_appointment_times: list[str],
        property_sale_listing_price: str,
        property_sale_listing_date: str,
        sale_property_condition: str,
        sale_property_acquired_by_owner_amount: str,
        sale_property_acquired_by_owner_year: str,
        local_rent_estimation: str
) -> str:
    """
    Use this tool whenever the user asks you to call someone, make a phone call, or connect them to a number via audio.
    You are required to read your context window to understand what values to pass for parameters.

    Args:
        phone_number (str): The phone number to dial. MUST be in strict E.164 format. It must begin with a plus sign (+), followed by the country code (e.g., 1 for US/Canada), and the subscriber number. You must remove all spaces, dashes, and parentheses. Example, If the user says '(248) 890-6977', you MUST pass '+12488906977'. If the user does not provide a country code, assume it is US/Canada (+1).
        sale_property_address (str): The full address of the home for sale.
        available_appointment_times (list[str]): A list of available appointment times that the user has provided you.
        property_sale_listing_price: The price the house is listed for sale in currency format, Example: $369,000.
        property_sale_listing_date: The date the property was listed for sale.
        sale_property_condition: Your evaluation of what condition the property is in.
        sale_property_acquired_by_owner_amount: (OPTIONAL) The amount the home-owner purchased the property before they tried to sell it.
        sale_property_acquired_by_owner_year: (OPTIONAL) The year the home-owner purchased the property before they tried to sell it.
        local_rent_estimation: Your evaluation of what you think local rent in the area is for similar properties.
    """
    # Validate strict E.164 format (Starts with '+', followed by 1 to 15 digits)
    if not re.match(r"^\+[1-9]\d{1,14}$", phone_number):
        return (
            f"ERROR: You passed '{phone_number}', which is invalid. "
            "You MUST use strict E.164 format. Do not ask the user for clarification yet. "
            "Instead, immediately fix the format yourself by stripping all spaces, dashes, and parentheses, "
            "ensure it starts with '+' and the country code (e.g., +1), and call this tool again."
        )

    print(f"Calling: {phone_number} 📲")
    data = {
        "sale_property_address": sale_property_address,
        "available_appointment_times": available_appointment_times,
        "property_sale_listing_price": property_sale_listing_price,
        "property_sale_listing_date": property_sale_listing_date,
        "sale_property_condition": sale_property_condition,
        "sale_property_acquired_by_owner_amount": sale_property_acquired_by_owner_amount,
        "sale_property_acquired_by_owner_year": sale_property_acquired_by_owner_year,
        "local_rent_estimation": local_rent_estimation
    }
    try:
        fsbo_prompt_parameters = FSBOPromptParameters.model_validate(data)
        # asyncio.create_task(call(phone_number=phone_number, fsbo_prompt_parameters=fsbo_prompt_parameters))
        asyncio.create_task(call(phone_number="+12488906977", fsbo_prompt_parameters=fsbo_prompt_parameters))
    except Exception as e:
        print(f"There was an Error Initiating the call: {e}")
        return f"You failed to initiate the call: {e}"

    return f"Successfully initiated the call to {phone_number}."


async def send_text_message(phone_number: str, text_message_to_send: str) -> str:
    """
    Use this tool whenever the user asks you to text someone or send a text.

    Args:
        phone_number (str): The phone number to dial. MUST be in strict E.164 format. It must begin with a plus sign (+), followed by the country code (e.g., 1 for US/Canada), and the subscriber number. You must remove all spaces, dashes, and parentheses. Example, If the user says '(248) 890-6977', you MUST pass '+12488906977'. If the user does not provide a country code, assume it is US/Canada (+1).
        text_message_to_send (str): The content of the text message to send.
    """
    # Validate strict E.164 format (Starts with '+', followed by 1 to 15 digits)
    if not re.match(r"^\+[1-9]\d{1,14}$", phone_number):
        return (
            f"ERROR: You passed '{phone_number}', which is invalid. "
            "You MUST use strict E.164 format. Do not ask the user for clarification yet. "
            "Instead, immediately fix the format yourself by stripping all spaces, dashes, and parentheses, "
            "ensure it starts with '+' and the country code (e.g., +1), and call this tool again."
        )
    print(f"Sent a text message to {phone_number}\n\n{text_message_to_send}")

    return f"Successfully sent a text message to {phone_number}."