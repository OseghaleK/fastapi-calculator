"""End to end tests that drive a real browser with Playwright."""

import pytest

# A marker no real result could ever be. Blanking the result div and
# waiting for it to stop being empty looked fine but was not reliable,
# because a leftover value could satisfy the wait before the new request
# had even been sent. Waiting for this to be replaced cannot be
# satisfied by anything except a fresh response.
PENDING = "__waiting_for_response__"


def mark_pending(page):
    """Stamp the result div so we can tell new output from old."""
    page.evaluate(
        "marker => { document.getElementById('result').innerText = marker; }",
        PENDING,
    )


def calculate(page, a, b, button):
    """Fill both inputs, click a button, return whatever the page shows.

    The buttons in index.html have no ids, they use inline onclick
    handlers, so they get found by their visible text.
    """
    mark_pending(page)
    page.fill("#a", str(a))
    page.fill("#b", str(b))
    page.get_by_role("button", name=button, exact=True).click()
    page.wait_for_function(
        "marker => {"
        " const text = document.getElementById('result').innerText.trim();"
        " return text !== '' && text !== marker;"
        "}",
        arg=PENDING,
    )
    return page.inner_text("#result")


def test_the_page_loads(page, live_server):
    page.goto(live_server)
    assert page.inner_text("h1") == "Hello World"


def test_the_calculator_section_is_present(page, live_server):
    page.goto(live_server)
    assert page.inner_text("h2") == "Calculator"
    assert page.is_visible("#a")
    assert page.is_visible("#b")


def test_the_result_starts_empty(page, live_server):
    page.goto(live_server)
    assert page.inner_text("#result").strip() == ""


@pytest.mark.parametrize(
    "button, a, b, expected",
    [
        ("Add", 23, 34, "Calculation Result: 57"),
        ("Add", -23, 23, "Calculation Result: 0"),
        ("Subtract", 34, 23, "Calculation Result: 11"),
        ("Subtract", 23, 34, "Calculation Result: -11"),
        ("Multiply", 23, 2, "Calculation Result: 46"),
        ("Multiply", 34, 0, "Calculation Result: 0"),
        ("Divide", 34, 2, "Calculation Result: 17"),
        ("Divide", 23, 2, "Calculation Result: 11.5"),
    ],
)
def test_each_button_calculates(page, live_server, button, a, b, expected):
    page.goto(live_server)
    assert calculate(page, a, b, button) == expected


def test_dividing_by_zero_shows_the_error(page, live_server):
    page.goto(live_server)
    assert calculate(page, 23, 0, "Divide") == "Error: Cannot divide by zero!"


def test_empty_inputs_show_an_error(page, live_server):
    # Empty fields become NaN in the browser, which serializes to null
    # and comes back as a validation error rather than a result.
    page.goto(live_server)
    page.get_by_role("button", name="Add", exact=True).click()
    page.wait_for_function(
        "document.getElementById('result').innerText.trim() !== ''"
    )
    assert page.inner_text("#result").startswith("Error:")


def test_you_can_do_one_calculation_after_another(page, live_server):
    page.goto(live_server)
    assert calculate(page, 23, 34, "Add") == "Calculation Result: 57"
    assert calculate(page, 23, 2, "Multiply") == "Calculation Result: 46"
    assert calculate(page, 34, 2, "Divide") == "Calculation Result: 17"


def test_an_error_can_be_recovered_from(page, live_server):
    page.goto(live_server)
    assert calculate(page, 23, 0, "Divide").startswith("Error:")
    assert calculate(page, 23, 34, "Add") == "Calculation Result: 57"
