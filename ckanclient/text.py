import re


CAMEL_TO_SNAKE_CASE_PATTERN_1 = re.compile('(.)([A-Z][a-z]+)')
CAMEL_TO_SNAKE_CASE_PATTERN_2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name):
    name = re.sub(CAMEL_TO_SNAKE_CASE_PATTERN_1, r'\1_\2', name)
    return re.sub(CAMEL_TO_SNAKE_CASE_PATTERN_2, r'\1_\2', name).lower()
