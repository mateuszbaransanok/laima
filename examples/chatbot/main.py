from chatbot.apps.endpoint import chat_endpoint
from chatbot.setup.factories import setup

import laima

if __name__ == "__main__":
    setup(repository="postgres")  # Options: in_memory, postgres

    print(chat_endpoint("1234", "Hello world!"))
    print()
    print(chat_endpoint("1234", "How are you doing?"))

    laima.reset_container()
