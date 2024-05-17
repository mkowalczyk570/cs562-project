from generator import main as generator
from _generated import query as _generated

from sql import query as sql


def test_generator():
    # Generate the file
    generator()

    # Compare the output of your generated code to the output of the actual SQL query
    # Note: This only works for standard queries, not ESQL queries.
    assert _generated() == sql()

test_generator()