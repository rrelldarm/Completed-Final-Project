from openai import OpenAI


class InventoryAssistant:
    """
    Responsible only for building the AI prompt and calling the OpenAI API.
    No Streamlit code, no file I/O, no session state lives here.
    """

    def __init__(self, api_key: str, products_context: str, sales_context: str = ""):
        self.client           = OpenAI(api_key=api_key)
        self.products_context = products_context
        self.sales_context    = sales_context

    def build_prompt(self) -> str:
        """
        Builds the hidden system prompt that grounds the AI in live store data.
        Sales context is only injected for the Store Manager role.
        """
        prompt = (
            "You are a helpful inventory assistant for District 9, a clothing store.\n"
            "Answer questions based ONLY on the data provided below.\n"
            "If the answer cannot be determined from the data, say so clearly.\n"
            "Be concise, friendly, and specific — cite product names and numbers "
            "when relevant.\n\n"
            f"PRODUCT INVENTORY:\n{self.products_context}\n"
        )
        if self.sales_context:
            prompt += f"\nSALES HISTORY:\n{self.sales_context}\n"
        return prompt

    def get_response(self, chat_history: list) -> str:
        """
        Prepends the hidden system prompt to the visible chat history,
        calls gpt-3.5-turbo, and returns the assistant reply as a string.
        """
        messages = [{"role": "system", "content": self.build_prompt()}] + chat_history
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
