"""Clean and summarize the week 12 score CSV files."""

from __future__ import annotations

import pandas as pd


SCORE_COLUMN = "점수"
CLASS_COLUMN = "반"
SUBJECT_COLUMN = "과목"


def 정제(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Return a cleaned copy, reporting retained rows after each rule."""
    cleaned = df.copy()
    stages = [("시작", len(cleaned))]

    cleaned = cleaned.dropna(subset=[SCORE_COLUMN]).copy()
    stages.append(("빈 점수 제거", len(cleaned)))

    cleaned = cleaned.drop_duplicates().copy()
    stages.append(("완전 중복 제거", len(cleaned)))

    for column in (CLASS_COLUMN, SUBJECT_COLUMN):
        cleaned[column] = cleaned[column].astype("string").str.strip()
    stages.append(("반·과목 공백 정리", len(cleaned)))

    scores = pd.to_numeric(cleaned[SCORE_COLUMN], errors="coerce")
    cleaned = cleaned.loc[scores.between(0, 100)].copy()
    cleaned[SCORE_COLUMN] = pd.to_numeric(cleaned[SCORE_COLUMN]).astype(int)
    stages.append(("점수 범위 밖 제거", len(cleaned)))

    if verbose:
        previous_count = stages[0][1]
        for stage, remaining in stages:
            removed = previous_count - remaining
            reason = "기준 행 수" if stage == "시작" else f"{removed}행 제외"
            print(f"{stage}: {remaining}행 ({reason})")
            previous_count = remaining

    return cleaned.reset_index(drop=True)


def 진단표(df: pd.DataFrame) -> dict[str, object]:
    """Summarize the raw data before any cleaning."""
    return {
        "행·열 수": df.shape,
        "빈 점수 행": int(df[SCORE_COLUMN].isna().sum()),
        "완전 중복 행": int(df.duplicated().sum()),
        "반 이름 종류": sorted(df[CLASS_COLUMN].dropna().astype(str).unique().tolist()),
        "점수 최소": float(df[SCORE_COLUMN].min()),
        "점수 최대": float(df[SCORE_COLUMN].max()),
    }


def 분석표(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return class summaries and subject-by-class mean scores."""
    by_class = df.groupby(CLASS_COLUMN)[SCORE_COLUMN].agg(
        개수="count", 평균="mean", 중앙값="median", 최댓값="max", 합계="sum"
    )
    by_subject_class = df.pivot_table(
        index=SUBJECT_COLUMN,
        columns=CLASS_COLUMN,
        values=SCORE_COLUMN,
        aggfunc="mean",
    )
    return by_class, by_subject_class


def 반별평균(df: pd.DataFrame) -> dict[str, float]:
    """Return mean score by class as a dictionary."""
    return df.groupby(CLASS_COLUMN)[SCORE_COLUMN].mean().to_dict()


def 손계산용_정제기록(df: pd.DataFrame) -> list[dict[str, int | str]]:
    """Return stage counts for comparing a small file with hand calculations."""
    current = df.copy()
    records: list[dict[str, int | str]] = [{"단계": "시작", "남은 행": len(current), "제외 행": 0}]

    for label, operation in (
        ("빈 점수 제거", lambda data: data.dropna(subset=[SCORE_COLUMN])),
        ("완전 중복 제거", lambda data: data.drop_duplicates()),
    ):
        before = len(current)
        current = operation(current).copy()
        records.append({"단계": label, "남은 행": len(current), "제외 행": before - len(current)})

    before = len(current)
    for column in (CLASS_COLUMN, SUBJECT_COLUMN):
        current[column] = current[column].astype("string").str.strip()
    records.append({"단계": "반·과목 공백 정리", "남은 행": len(current), "제외 행": before - len(current)})

    before = len(current)
    scores = pd.to_numeric(current[SCORE_COLUMN], errors="coerce")
    current = current.loc[scores.between(0, 100)].copy()
    records.append({"단계": "점수 범위 밖 제거", "남은 행": len(current), "제외 행": before - len(current)})
    return records