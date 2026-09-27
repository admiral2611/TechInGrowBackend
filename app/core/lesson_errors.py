class LessonContentError(Exception):

    def __init__(
        self,
        file_name: str,
        message: str
    ):
        self.file_name = file_name
        self.message = message

        super().__init__(
            f"{file_name}: {message}"
        )