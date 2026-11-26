# FAA HOLDOVER TIME (2026-27)

FAA Holdover Time Guidelines Winter 2026-2027 (Original Issue Aug 11, 2026)를 기준으로 HOT를 찾아 주는 웹 계산기입니다. 화면은 A380 MCDU 모양으로 만들었습니다.

> **THE RESPONSIBILITY FOR THE APPLICATION OF THESE DATA REMAINS WITH THE USER.**
> 교육·검증용 도구입니다. 실제 운항 판단은 회사 승인 문서와 FAA 원문을 따르십시오.

## 다루는 범위

| 유체 | 근거 표 |
|---|---|
| Type IV Kilfrost ABC-S Plus 100/0, 75/25, 50/50 | Table 43, Adj-43 (Flap/Slat DN, 76%) |
| Type I Aluminum / Composite | Table 2/3, Adj-2/3 |
| Active Frost | Table 1, Adj-1 |
| Ice Pellets / Small Hail Allowance Time (100/0) | Table 56, Adj-55 |
| 눈 강도(시정 기준, 주간/야간) | Table 57 |
| LOUT | Table 61 |

아직 없는 것: statute mile 시정 입력, 다른 유체 브랜드.

## 파일 구성

```
index.html          완성된 계산기 (브라우저로 바로 열면 됩니다)
src/template.html   화면과 계산 로직 (데이터 자리표시자 __DATA__ 등 포함)
src/build.py        data/ 의 JSON을 template에 넣어 index.html을 만듭니다
data/               FAA 문서에서 뽑아 교차검증한 표 데이터 (JSON)
tests/hot_cases.js  33개 조건별 HOT 확인 테스트 (Playwright)
tools/              FAA 문서 텍스트에서 데이터를 뽑고 검증한 스크립트
```

## 만들고 확인하는 법

```bash
python3 src/build.py          # index.html 다시 만들기
node tests/hot_cases.js       # 마지막 줄이 "fail 0 errors []" 이면 통과
```

테스트에는 Node.js와 Playwright(Chromium)가 필요합니다.

## 데이터 검증

- Table 43, Table 2/3 값을 FAA 원문 텍스트와 줄 단위로 대조했습니다.
- Appendix A 값은 표준 HOT × 0.76 반올림과 비교했습니다. Adj-43은 136개 중 129개가 일치하고, 나머지 7개는 모두 3:00 상한입니다. Type I은 112/112, Adj-55는 29/29 일치합니다.
- FAA docx 파일에서 따로 뽑은 표와도 대조했습니다(Table 43 90/90칸, Type I 72/72칸).

`tools/` 스크립트는 FAA 문서의 텍스트 파일 경로를 첫 번째 인자로 받습니다. 원문은 FAA 사이트에서 받을 수 있습니다:
https://www.faa.gov/other_visit/aviation_industry/airline_operators/airline_safety/deicing/FAA-2026-27_Holdover_Tables.pdf
