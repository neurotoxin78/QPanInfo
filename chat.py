from tools import get_config

import openai


class ChatBot():
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config['openai']['api_key']
        self.model_engine = self.config['openai']['model_engine']
        self.prompt = ""
        openai.api_key = self.api_key

    def setPrompt(self, prompt: str):
        self.prompt = prompt
        # Set up the model and prompt

    def getResponce(self, max_tokens=1024, n=1, stop=None, temperature=0.5 ):
        # Generate a response
        completion = openai.Completion.create(
            engine=self.model_engine,
            prompt=self.prompt,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            temperature=temperature,
        )

        # response = completion.choices[0].text
        return completion.choices

chat = ChatBot()
chat.setPrompt("Привіт, як справи?")
print(chat.getResponce()[0].text)