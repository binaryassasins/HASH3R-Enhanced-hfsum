class InvalidChunkSize(Exception):
    "Raised when the chunk size is non integer value and less than 0"
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)