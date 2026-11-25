from pathlib import Path

import pandas as pd

from analysis import 분석표, 반별평균, 손계산용_정제기록, 정제


DATA_DIR = Path(__file__).parent
원본 = pd.read_csv(DATA_DIR / "scores_2026.csv")
미니원본 = pd.read_csv(DATA_DIR / "mini.csv")


def test_정제하면_100행이_남는다():
    assert len(정제(원본, verbose=False)) == 100


def test_반은_두종류만_남는다():
    cleaned = 정제(원본, verbose=False)
    assert sorted(cleaned["반"].unique()) == ["1반", "2반"]


def test_그룹합계와_전체합계가_같다():
    cleaned = 정제(원본, verbose=False)
    by_class, _ = 분석표(cleaned)
    assert by_class["합계"].sum() == cleaned["점수"].sum()


def test_미니파일_1반_평균은_손계산과_같다():
    cleaned = 정제(미니원본, verbose=False)
    assert len(cleaned) == 7
    assert 반별평균(cleaned)["1반"] == 80.0
    assert 반별평균(cleaned)["2반"] == 70.0


def test_정제단계별_행수가_진단과_일치한다():
    records = 손계산용_정제기록(원본)
    assert [(row["남은 행"], row["제외 행"]) for row in records] == [
        (114, 0),
        (108, 6),
        (104, 4),
        (104, 0),
        (100, 4),
    ]


def test_정제는_원본을_바꾸지_않는다():
    before = 원본.copy(deep=True)
    정제(원본, verbose=False)
    pd.testing.assert_frame_equal(원본, before)