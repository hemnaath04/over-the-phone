import pytest

from otp.detect import detect, scorer_category
from otp.entities import build_items
from otp.run import locale_for
from otp.score import score


def found(text, locale="en-US"):
    return [(text[s.start:s.end], s.category, s.gold) for s in detect(text, locale)]


def test_a_realistic_reply():
    text = ("Perfect! You're booked for 05/08/2026 at 4:30 PM with Dr. Patel. Your confirmation "
            "code is MU6-MRF, and the receipt goes to noah.okafor@brightdental.com. The total is "
            "£7,900.99, charged to the card ending in 8091. Questions? Call 07700 900123.")
    got = found(text, "en-GB")
    assert ("05/08/2026", "date", {"month": 8, "day": 5, "style": "numeric"}) in got
    assert ("4:30 PM", "time", {"hour": 16, "minute": 30}) in got
    assert ("MU6-MRF", "booking_ref", {"alnum": "MU6MRF"}) in got
    assert ("noah.okafor@brightdental.com", "email", {"email": "noah.okafor@brightdental.com"}) in got
    assert ("£7,900.99", "price", {"currency": "GBP", "cents": 790099}) in got
    assert ("8091", "card_last4", {"digits": "8091"}) in got
    assert ("07700 900123", "uk_mobile", {"digits": "7700900123"}) in got
    assert len(got) == 7


@pytest.mark.parametrize("text, locale, gold", [
    ("on 05/08/2026", "en-US", {"month": 5, "day": 8, "style": "numeric"}),
    ("on 05/08/2026", "en-GB", {"month": 8, "day": 5, "style": "numeric"}),
    ("on 25/10/2026", "en-US", {"month": 10, "day": 25, "style": "numeric"}),
    ("by 2026-11-03", "en-US", {"month": 11, "day": 3, "style": "iso"}),
    ("on November 3rd", "en-US", {"month": 11, "day": 3, "style": "words"}),
])
def test_dates_follow_the_locale(text, locale, gold):
    assert found(text, locale)[0][2] == gold


def test_no_false_entities_in_plain_speech():
    assert found("Hi, thanks for calling. The reference is below, and we open at nine.") == []


def test_email_digits_are_not_a_phone_number():
    got = found("Write to sam4155550142@acme.com today.")
    assert [c for _, c, _ in got] == ["email"]


def test_every_benchmark_sentence_is_detected_and_self_scores():
    """Each generated sentence yields exactly its own entity, which scores against the sentence."""
    for item in build_items(per_category=20, seed=9):
        spans = detect(item.text, locale_for(item))
        assert len(spans) == 1, (item.id, item.text, spans)
        s = spans[0]
        assert score(scorer_category(s), item.text, s.gold)[0], (item.id, item.text, s.gold)


@pytest.mark.parametrize("transcript, expected", [
    ("You're booked for August 5th, 2026 at 16:30. Receipt goes to N-O-A-H dot O-K-A-F-O-R at brightdental.com.",
     "noah.okafor@brightdental.com"),
    ("You will get an email at T-P-A-T-E-L at acme.com, and", "tpatel@acme.com"),
    ("booked for May 8th, 2026 at 16:30 with Dr Patel", "(no address)"),
])
def test_heard_as_shows_the_real_address(transcript, expected):
    from otp.heardas import readable
    assert readable("email", transcript, "", "") == expected
