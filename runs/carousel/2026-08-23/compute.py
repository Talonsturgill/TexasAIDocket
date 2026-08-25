"""Every figure the 2026-08-23 deck computes, derived here and nowhere else."""
from decimal import Decimal as D

INITIAL   = D("825000")      # c2, quoted
AFTER_1ST = D("4250000")     # c3, quoted
THIRD_ADD = D("5600000")     # c5, quoted
TOTAL     = D("9850000")     # c5, quoted
HRIS      = 7                # c4, quoted "all seven"

assert AFTER_1ST + THIRD_ADD == TOTAL, "the quoted figures do not reconcile"

results = {
    "committed_without_a_board_vote": AFTER_1ST,
    "share_without_a_board_vote_pct": (AFTER_1ST / TOTAL * 100).quantize(D("0.1")),
    "share_without_a_board_vote_rounded_pct": int((AFTER_1ST / TOTAL * 100).quantize(D("1"))),
    "multiple_initial_to_total": (TOTAL / INITIAL).quantize(D("0.01")),
    "amendments_before_the_board_saw_it": 2,
    "hospitals_now_covered": HRIS,
}
if __name__ == "__main__":
    for k, v in results.items():
        print(f"{k:42} {v}")
