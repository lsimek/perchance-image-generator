from random import sample


class MyWordlist:
    def __init__(self):
        self.wordlist = ["Dragon", "Castle", "Moon", "Forest", "Apple", "Fish", "Green", "Banana", "Queen Elizabeth I", "Inspiration"]

    def get_prompt(self, number=10):  # returns 'first, second, third...' type string
        return ', '.join(sample(self.wordlist, number))
