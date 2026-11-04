import pytest

from otp.entities import build_items
from otp.run import locale_for
from otp.score import score
from otp.speakable import speakable


@pytest.mark.parametrize("text, locale, expected", [
    ("Your next appointment is on 05/08/2026.", "en-GB", "Your next appointment is on the 5th of August."),
    ("Your next appointment is on 11/3/2026.", "en-US", "Your next appointment is on November 3rd."),
    ("Your next appointment is on 25/10/2026.", "en-US", "Your next appointment is on October 25th."),
    ("The parcel should arrive by 2026-11-03.", "en-US", "The parcel should arrive by November 3rd."),
    ("We've moved your call to 16:15.", "en-US", "We've moved your call to 4:15 PM."),
    ("Pickup is at 09:00 sharp.", "en-US", "Pickup is at 9 AM sharp."),
    ("We've moved your call to 16:15.", "en-GB", "We've moved your call to 16:15."),
    ("The technician will arrive at 4:30 PM.", "en-US", "The technician will arrive at 4:30 PM."),
    ("The receipt will go to noah.okafor@brightdental.com.", "en-US",
     "The receipt will go to N-O-A-H dot O-K-A-F-O-R at brightdental.com."),
    ("Your booking reference is MU6-MRF.", "en-US",
     "Your booking reference is M-U-6-M-R-F, that's M for Mike, F for Foxtrot."),
    ("Your nearest branch is at SE14 9PS.", "en-GB",
     "Your nearest branch is at S-E-1-4, 9-P-S, that's S for Sierra, E for Echo, P for Papa."),
    ("We'll text the confirmation to 07700 900123.", "en-GB",
     "We'll text the confirmation to 0-7-7-0-0, 9-0-0-1-2-3."),
    ("The number we have on file is +44 7700 900123.", "en-GB",
     "The number we have on file is +4-4, 7-7-0-0, 9-0-0-1-2-3."),
    ("You can reach the front desk at (452) 555-0118.", "en-US",
     "You can reach the front desk at 4-5-2, 5-5-5, 0-1-1-8."),
    ("I'll charge the card ending in 8091.", "en-US", "I'll charge the card ending in 8-0-9-1."),
    ("That comes to £34.99 including tax.", "en-GB", "That comes to £34.99 including tax."),
])
def test_rewrites(text, locale, expected):
    assert speakable(text, locale) == expected


def test_rewritten_sentences_still_carry_their_entity():
    """Read back verbatim, every rewritten sentence must still score as a pass."""
    for item in build_items(per_category=40, seed=5):
        rewritten = speakable(item.text, locale_for(item))
        passed, heard = score(item.category, rewritten, item.gold)
        assert passed, (item.id, rewritten, heard)


@pytest.mark.parametrize("transcript", [
    "The receipt will go to N-O-A-H dot O-K-A-F-O-R at brightdental.com.",
    "The receipt will go to NOAH.OKAFOR@brightdental.com.",
    "The receipt will go to N O A H dot O K A F O R at brightdental.com.",
])
def test_spelled_emails_score(transcript):
    assert score("email", transcript, {"email": "noah.okafor@brightdental.com"})[0]


def test_call_transcript_splits_at_item_markers():
    from otp.score_call import split_items
    text = ("Starting the test script. Item 1. Your next appointment is on May 8th. "
            "Item two. Your next appointment is on the 5th of August. Item twenty-four, bye.")
    parts = split_items(text)
    assert parts[1] == "Your next appointment is on May 8th."
    assert parts[2] == "Your next appointment is on the 5th of August."
    assert 24 in parts
