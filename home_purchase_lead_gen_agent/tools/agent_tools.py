import asyncio
import re
import webbrowser

from home_purchase_lead_gen_agent.phone_call_agent_as_tool.main import call


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


async def initiate_phone_call(phone_number: str) -> str:
    """
    Use this tool whenever the user asks you to call someone, make a phone call, or connect them to a number via audio.

    Args:
        phone_number (str): The phone number to dial. MUST be in strict E.164 format.
        It must begin with a plus sign (+), followed by the country code (e.g., 1 for US/Canada),
        and the subscriber number. You must remove all spaces, dashes, and parentheses.
        Example, If the user says '(248) 890-6977', you MUST pass '+12488906977'.
        If the user does not provide a country code, assume it is US/Canada (+1).
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
    asyncio.create_task(call(phone_number=phone_number))

    return f"Successfully initiated the call to {phone_number}."


async def send_text_message(phone_number: str) -> str:
    """
    Use this tool whenever the user asks you to text someone or send a text.

    Args:
        phone_number (str): The phone number to dial. MUST be in strict E.164 format.
        It must begin with a plus sign (+), followed by the country code (e.g., 1 for US/Canada),
        and the subscriber number. You must remove all spaces, dashes, and parentheses.
        Example, If the user says '(248) 890-6977', you MUST pass '+12488906977'.
        If the user does not provide a country code, assume it is US/Canada (+1).
    """
    # Validate strict E.164 format (Starts with '+', followed by 1 to 15 digits)
    if not re.match(r"^\+[1-9]\d{1,14}$", phone_number):
        return (
            f"ERROR: You passed '{phone_number}', which is invalid. "
            "You MUST use strict E.164 format. Do not ask the user for clarification yet. "
            "Instead, immediately fix the format yourself by stripping all spaces, dashes, and parentheses, "
            "ensure it starts with '+' and the country code (e.g., +1), and call this tool again."
        )
    print(f"Sent a text message to {phone_number}")

    return f"Successfully sent a text message to {phone_number}."