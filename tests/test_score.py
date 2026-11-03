import pytest

from otp.entities import CATEGORIES, build_items
from otp.score import score, spell_to_digits


@pytest.mark.parametrize("text, expected", [
    ("four one five", "4 1 5"),
    ("forty two", "42"),
    ("oh seven seven double oh", "0 7 7 00"),
    ("triple nine", "999"),
    ("four hundred fifteen", "4 15"),
    ("four hundred five", "40 5"),
    ("twenty third", "23"),
    ("hello there", "hello there"),
])
def test_spell_to_digits(text, expected):
    assert spell_to_digits(text) == expected


CASES = [
    # (category, gold, transcript, should_pass)
    ("uk_mobile", {"digits": "7700900123"}, "and we will call you on 07700 900 123.", True),
    ("uk_mobile", {"digits": "7700900123"}, "Our number is +44 7700 900123.", True),
    ("uk_mobile", {"digits": "7700900123"}, "oh seven seven double oh, nine double oh, one two three", True),
    ("uk_mobile", {"digits": "7700900123"}, "07700 900 132", False),
    ("us_phone", {"digits": "4155550142"}, "Just call us at (415) 555-0142.", True),
    ("us_phone", {"digits": "4155550142"}, "four one five, five five five, oh one four two", True),
    ("us_phone", {"digits": "4155550142"}, "Just call us at 415-555-1042.", False),
    ("card_last4", {"digits": "0421"}, "the card ending in 0421", True),
    ("card_last4", {"digits": "0421"}, "the card ending in 421", False),
    ("us_zip", {"digits": "02115"}, "And the ZIP code is 02115?", True),
    ("us_zip", {"digits": "02115"}, "And the ZIP code is 2115?", False),
    ("booking_ref", {"alnum": "K7M4QX"}, "Your booking reference is K7M4QX.", True),
    ("booking_ref", {"alnum": "K7M4QX"}, "Your booking reference is K7M-4QX.", True),
    ("booking_ref", {"alnum": "K7M4QX"}, "Your booking reference is K 7 M 4 Q X.", True),
    ("booking_ref", {"alnum": "K7M4QX"}, "Your booking reference is K7N4QX.", False),
    ("uk_postcode", {"alnum": "SW1A1AA"}, "The postcode is SW1A 1AA, is that right?", True),
    ("uk_postcode", {"alnum": "SW1A1AA"}, "the postcode is S W one A one A A", True),
    ("uk_postcode", {"alnum": "SW1A1AA"}, "The postcode is SW1A 1AE.", False),
    ("uk_postcode", {"alnum": "G99SX"}, "Your nearest branch is at G9, 9SX.", True),
    ("price_usd", {"currency": "USD", "cents": 124850}, "your balance is $1,248.50, due on the 15th", True),
    ("price_usd", {"currency": "USD", "cents": 124850}, "1,248 dollars and 50 cents", True),
    ("price_usd", {"currency": "USD", "cents": 124850}, "one thousand two hundred forty eight dollars and fifty cents", True),
    ("price_usd", {"currency": "USD", "cents": 124850}, "your balance is $1,248.15", False),
    ("price_gbp", {"currency": "GBP", "cents": 3499}, "That comes to £34.99 including tax.", True),
    ("price_gbp", {"currency": "GBP", "cents": 3499}, "thirty four pounds ninety nine", True),
    ("price_gbp", {"currency": "GBP", "cents": 3499}, "That comes to $34.99 including tax.", False),
    ("price_gbp", {"currency": "GBP", "cents": 1200}, "I can refund £12 to your card.", True),
    ("date", {"month": 11, "day": 3}, "You're all set for Tuesday, November 3rd.", True),
    ("date", {"month": 11, "day": 3}, "on the third of November", True),
    ("date", {"month": 11, "day": 3}, "November 3, 2026", True),
    ("date", {"month": 11, "day": 3}, "on 11/3/2026", True),
    ("date", {"month": 11, "day": 3}, "You're all set for November 13th.", False),
    ("date", {"month": 11, "day": 3}, "You're all set for March 11th.", False),
    ("time", {"hour": 16, "minute": 30}, "The technician will arrive at 4:30 PM.", True),
    ("time", {"hour": 16, "minute": 30}, "four thirty p.m.", True),
    ("time", {"hour": 16, "minute": 30}, "at 16:30", True),
    ("time", {"hour": 16, "minute": 30}, "at 4:30 AM", False),
    ("time", {"hour": 9, "minute": 0}, "Pickup is at 9 AM sharp.", True),
    ("time", {"hour": 9, "minute": 0}, "Pickup is at nine o'clock sharp.", True),
    ("email", {"email": "j.smith42@acme.co.uk"}, "I've sent it to j.smith42@acme.co.uk.", True),
    ("email", {"email": "j.smith42@acme.co.uk"}, "j dot smith forty two at acme dot co dot uk", True),
    ("email", {"email": "j.smith42@acme.co.uk"}, "j.smith24@acme.co.uk", False),
]


@pytest.mark.parametrize("category, gold, transcript, should_pass", CASES)
def test_scorers(category, gold, transcript, should_pass):
    passed, heard = score(category, transcript, gold)
    assert passed is should_pass, heard


def test_every_item_scores_against_its_own_text():
    """Each sentence, read back verbatim, must pass: the scorer understands the set."""
    for item in build_items(per_category=40, seed=3):
        passed, heard = score(item.category, item.text, item.gold)
        assert passed, (item.id, item.text, heard)


def test_build_is_deterministic_and_covers_every_category():
    a, b = build_items(5, seed=11), build_items(5, seed=11)
    assert [i.text for i in a] == [i.text for i in b]
    assert {i.category for i in a} == set(CATEGORIES)
    assert len({i.id for i in a}) == len(a)
