from pydantic_settings import BaseSettings


class QuizConfig(BaseSettings):
    CLOZE_EXPRESSION: str = r'\{\{[^}]+\}\}'
    CLOZE_SYNTAX: str = '{{...}}'


quiz_config = QuizConfig()
