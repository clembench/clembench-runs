from check_scores_files import count_missing_scores


def test_count_missing_scores_v1_5_returns_zero():
    missing_count = count_missing_scores("v1.5")
    assert missing_count == 0, f"There should be no 'scores.json' missing, but there are: {missing_count}"
