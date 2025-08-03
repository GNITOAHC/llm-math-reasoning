from openai import OpenAI


class OpenAIReasoning:
    def __init__(self, api_key: str, model: str = "o3-mini", reasoning_effort: str = "high"):
        self.client = OpenAI(api_key=api_key)
        self.messages = []
        self.model = model
        self.reasoning_effort = reasoning_effort

        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.total_tokens = 0
        self.reasoning_tokens = 0
    def complete(self, mes: str, system_prompt: str) -> str:
        request_msg = []
        request_msg.append({"role": "system", "content": system_prompt})
        request_msg.append({"role": "user", "content": mes})

        c = self.client.chat.completions.create(
            reasoning_effort=self.reasoning_effort,
            model=self.model,
            messages=request_msg,
        )

        if c.usage and c.usage.completion_tokens:
            self.completion_tokens += c.usage.completion_tokens

        if c.usage and c.usage.prompt_tokens:
            self.prompt_tokens += c.usage.prompt_tokens

        if c.usage and c.usage.total_tokens:
            self.total_tokens += c.usage.total_tokens

        if (
            c.usage
            and c.usage.completion_tokens_details
            and c.usage.completion_tokens_details.reasoning_tokens
        ):
            self.reasoning_tokens += c.usage.completion_tokens_details.reasoning_tokens

        if c.choices and c.choices[0].message and c.choices[0].message.content:
            self.messages.append({"role": "user", "content": mes})
            self.messages.append(
                {"role": "assistant", "content": c.choices[0].message.content}
            )

        return str(c.choices[0].message.content)

    def history(self) -> list:
        return self.messages

    def token_used(self) -> dict:
        return {
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }
