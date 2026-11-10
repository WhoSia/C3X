# C3X 0.30 — Product P1→P2: 첫 번째 실행 가능한 교육용 대조 체스 해설기

**연구 기록:** 2026-11-10 KST. **상태:** 실제 Stockfish16 기반 한국어 해설 프로그램 P1 + 체스 규칙 기반 CCC 개념 차분 P2 모두 **GitHub Actions 실제 성공**. 사용자 대면 제품의 첫 실행 가능한 *세로 단위(vertical slice)*; 기존 경쟁 해설기를 능가한다는 실증은 아님.

## 0. 원래 질문과 사용자 문제 재정의

가장 초기 원본 [**C3X 1.md, 2026-08-14 11:52, Google Drive**](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view): *"stockfish를 보고 일반인들이 공부를 잘 못함... 그 수가 왜 좋은 수인지, 다른 수들보다 왜 근소하게 좋은지 등을 explainable-ai하게 할 수 있는 연구 있나?"*.

지향점은 "기물 전개를 한다"처럼 **두 후보에 공통인 설명을 버리고**, "왜 A이지 B가 아닌가?"에 대해 실측 근거·반박 가능한 대응·불확실성을 제공하는 교육 도구이다. **두 수의 6cp 차이가 인간 전략 개념으로 additive하게 분해된다고 가정하지 않는다.**

## 1. 선행연구를 직접 붙인 부분 / 재현하지 않은 부분

| 기능 | 선행연구 원본을 우선 인용 | 이번 구현한 정확한 단위 | 아직 미구현 |
|---|---|---|---|
| 대응에 따라 달라지는 미래 계획 | [Cui, Ling & Ng (2026), *Communicating Chess Strategies in Natural Language*, Drive 원문](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) | 각 후보 수 아래 **상대 상위 MultiPV 최대 k=3 응수** + 각 응수별 실제 엔진 최선의 내 수와 재검색 평가 | Cui의 **전체 깊이/재귀 전략나무**, 전략 언어모델, 사용자 효용 평가 |
| 개념 기반 교수 설명 | [Kim et al. (2024), *Concept-Guided Chess Commentary*, Drive 원문](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view) | 기물 가치·패스폰·폰 섬·공격 대상·무방어 기물·킹 주변 공격·상대 응수 수 등 **7개 엄밀하게 정의한 규칙 지표**, 두 수 사이 공통 지표는 숨김 | 논문의 **학습된 개념 추출기, 인간/LLM 교수학습 실험, 자동 개념 평가 정확도** |
| 전술 사실 검증 | [Hebbar et al. (2026) ACT-Eval, Drive 원문](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) | 합법수·체크·포획 등을 현재 국면의 체스 규칙으로 직접 검증; 불가능한 수 입력은 거부 | 완전한 ACT-Eval 325문항 및 자유 설명 추출/교정 |
| 대조적 설명, 최소 차이 | [C3X 1.md 초기 질문, Drive](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view) | 같은 측정값을 차이 근거로 **사용 금지**, A−B의 두 엔진 깊이 평가와 실제 차이만 보고 | 인과적 전략 가치 분해·인간 학습 성과 검증 |

기존 0.29의 Cui k3 및 미래 계획 실험과 0.30 R1~R7의 SARFA/SHAP/ACT-Eval/Parfenova 연구 구현은 버리지 않는다. 그러나 **현재 제품에는 확실한 기물 사실과 실제 엔진 검색만 먼저 노출**한다. 인과적 증명이 없는 수치에서 유창한 원인을 만들어 내는 LLM 단계는 의도적으로 붙이지 않았다.

## 2. 구체적인 소프트웨어 계약

- [사용자 비교 엔진 `product/c3x_explain_two_moves.py`](../product/c3x_explain_two_moves.py) · [10개 테스트](../product/test_c3x_explain_two_moves.py) · [P1 실행 CI #42783144894 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42783144894).
- [개념 차분 엔진 `product/c3x_concept_contrast.py`](../product/c3x_concept_contrast.py) · [10개 추가 테스트](../product/test_c3x_concept_contrast.py) · [**P2 통합 CI #42783791922 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42783791922), 제품 관련 총 20개 회귀 테스트 GREEN.
- 입출력: `FEN + 서로 다른 합법 UCI 두 수 + Stockfish 바이너리` → 기계 판독 가능한 provenance JSON + **한국어 사용자 해설 Markdown**. P2에서는 기존 P1 JSON을 정확히 SHA 검증해 **7개 규칙 개념을 연결한 통합 한국어 Markdown**까지 생성.
- 실측 엔진: 공식 upstream unmodified Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, 1 thread, 16MB hash, **Use NNUE=False**. 각 후보 root depth8/10에서 강제 수 분석, depth8에서 각 후보마다 상대 MultiPV 최대3개, 이후 반응별 depth8 최선 응수 재검색. **같은 Stockfish를 사용하므로 독립 referee가 아니며 상대 모든 합법 수를 전수 검정하지 않았다**.
- 한계 문구를 보고서에 의무 포함: 차이가 미세하거나 깊이 간 선호 반전 시 **동등할 가능성/추가 탐색 필요**; 킹 주변 공격 칸 수는 원본 Stockfish의 KingSafety eval term이 아님; 공격 그래프에는 핀 된 기물의 유사 합법 외 공격이 포함될 수 있음; 특정 특징이 다르다는 것과 원본 엔진이 그 특징 때문에 A를 골랐다는 인과적 연결은 별개.

### 직접 실행 (체스 파서와 Stockfish가 설치된 사용자 컴퓨터)

```bash
python -m pip install 'chess==1.11.2'
python product/c3x_explain_two_moves.py \
  --fen 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' \
  --move-a e2e4 \
  --move-b d2d4 \
  --engine /path/to/pinned/stockfish \
  --out-json demo.json \
  --out-md demo.md

python product/c3x_concept_contrast.py \
  --base-report-json demo.json \
  --out-json demo-concepts.json \
  --out-md demo-concepts.md
cat demo.md demo-concepts.md > demo-combined.md
```

설치 경로와 엔진 바이너리는 사용자 환경에 맞춰야 한다. 두 시작 수 비교는 동작 예시일 뿐 "근소 차이 전략" 연구 국면의 사례라는 뜻이 아니다. 이 커맨드를 별도로 사용자 로컬에서 실행했다고 주장하지 않는다.

## 3. 실제 역사 대국 2개에서 얻은 결과

**P1 [실제 성공 #42783144894](https://github.com/WhoSia/C3X/actions/runs/42783144894).** P37 사전 SHA-봉인 과거 합법 PGN 2개 → 동일 원본 국면 두 후보 비교.

| 실측 과거 국면 | 후보 A/B | A−B depth8 | A−B depth10 | 동작한 응수 분기 |
|---|---|---:|---:|---:|
| Sahel | e5f4 / e5c3 | **+6 cp** | **+19 cp** | 두 후보 × 상대 상위 3개 = 6 |
| Cerrado | e5f6 / d1c2 | **−21 cp** | **+4 cp** | 두 후보 × 상대 상위 3개 = 6 |

- **Sahel P1 source JSON SHA** `970e3ca2229edfc2a890e3a4f056dc47de175536eb61bfbaff54720706bdee04`; **한국어 Markdown SHA** `5e247c026d0f151eb991a7664de38e83ba18eadff8df8f86de0d6b965ca36b80`.
- **Cerrado P1 JSON SHA** `979a5384395822f750d0cdae85ada7147098441c0c9866c579655621ec7c1085`; **한국어 Markdown SHA** `2c43ce5c81c2433a0b97b848970056df60ab19e069039441b647dfc854fa9ff2`.
- **P1 실제 아티팩트 ID** `13747106522`, ZIP digest `eaa2e9729771e977cc46786eaf2af5c5c887209af6ef44037330ebfa4cac23ef`.

**P2 [실제 통합 성공 #42783791922](https://github.com/WhoSia/C3X/actions/runs/42783791922)**: 7개 지표 × 두 국면의 두 수. Sahel에서는 **측정된 차별 지표 1개, 동일 지표 6개**이고 Cerrado에서는 **차별 지표 4개, 동일 3개**. 의미 없는 공유 개념을 "왜 A가 좋다"의 원인으로 사용하지 않는다. 이 결과 자체가 C3X 최초 문제의 "최소 차이"를 실측 교육 형식으로 바꾼 것이다.

- **P2 Sahel 개념 JSON SHA** `1e5a6320fdd216057e67eee0af40c644050002b60f35d4923c1bcc6c1fd11e75`.
- **P2 Cerrado 개념 JSON SHA** `680ef508a1b0af7c127ad342421db58062bccfc396950680a9eb7f063c3c62df`.
- **실제 통합 사용자 Markdown SHA:** Sahel `f91ec3daaff927b6493a12e0344fd61b14809efbdae1d5efb8532de53b2c631d`; Cerrado `523251930c042c2682fa6bceb84fc4849d74ae686f0aef3d6f87f4cb5f88c60f`.
- **P2 아티팩트 ID** `13747730492`; ZIP SHA `3f4eadf4067067eaa92b31afedd090770bcbe5d347cded124d892c8a05c34643`.

## 4. 실제 제품 경쟁 기준: chess.com / Lichess와 비교해 무엇을 추가할 것인가?

검토한 현재 공식 [Chess.com **Game Review** 안내(2026-09-25)](https://support.chess.com/en/articles/8584089-how-does-game-review-work)는 **평가 그래프·정확도·수 분류·코치 설명·Show Idea/Line·Retry·맞춤 설정** 등을 이미 제공한다. [Lichess 공식 기능 안내](https://lichess.org/features) 역시 무료 엔진 분석·학습 복기·스터디·퍼즐을 제공한다. 따라서 **'자연어로 한 줄 말한다'거나 '엔진 예상 수순을 표시한다'는 기능만으로 경쟁 우위를 주장할 수 없다**.

C3X가 객관적으로 경쟁을 시도할 수 있는 차별 목표:

1. **왜 A이지 B가 아닌가:** 같은 국면에서 학생이 실제 생각한 대안 B를 직접 지정한 두 수 비교. 공통된 특징이 해설 원인으로 둔갑하지 않도록 제약.
2. **가치 차이의 안정성:** 깊이 변화·독립 referee·응수 분포 변화를 재측정해 0.04폰의 미세 차이를 "당연히 좋은 수"라고 단정하지 않는 것.
3. **상대가 주된 예측과 다르게 응수하면:** Cui식 실제 실행 가능한 분기 구조. 현재는 첫 상대 ply 상위3으로 제한; recursive k3 전반은 아직 미구현.
4. **모든 주장에 증거:** 임의로 생성한 전략적 문장은 사실이라고 채택하지 않음. Board rule exact / Source Stockfish measured / Independent referee measured / Hypothesis / Unverified 표시.
5. **학습자 적응:** [Tang et al. (2024) **Maia-2 원본 Drive PDF**](https://drive.google.com/file/d/1cagwzcRDAHfvzbuCaNsEha2SRKg_Xpmk/view)의 원래 인간 수 선택 분포 실측 모델을 나중에 통합. **현재 C3X에서는 Maia2 추론을 했다고 주장하지 않음**.

### 정량 평가 게이트: 아직 실증되지 않은 계획

대조군을 "평가값+메인라인", "단순 개념 설명", "현재 chess.com Game Review의 실제 사용자용 설명", "C3X 개념·응수·불확실성 포함"으로 만들고, **같은 포지션을 평가하되 답변 출처를 가린 사람 평가**를 해야 한다.

- *대조 설명 특이성*: 평가자가 A와 B의 공통 속성을 제외한 실제 차이를 알아낼 수 있는가?
- *사실 오류*: 규칙 위반·불법 수·포획/체크 오류·잘못된 근거를 얼마나 생성하는가?
- *반례 강건성*: 공개 전 숨겨둔 상대 응수나 독립 평가자에서도 설명이 유효한가?
- *학습 효용*: 내용을 보고 새 포지션에서 선택과 반박을 실제로 더 잘 수행하는가?
- *일반화 및 비용*: 생각 시간, 검색 노드와 설명 길이 통제. 결과는 같은 원본 게임군 단위로 집계하고 노출된 후보 두 개를 독립 표본 두 개처럼 부풀리지 않는다.

**현재 chess.com보다 설명 품질이 낫다는 시험은 0회**이며 사용성 A/B 시험 또한 0회. 따라서 평가 우위라는 표현은 HOLD다.

## 5. 다음 실질 구현 순서

**P3** 먼저 UI와 반복 가능 데이터 계약: FEN 붙여넣기 → 체스판 → 두 후보 선택 → 평가·차이·근거·실제 대응나무 → 출처와 신뢰 단계를 하나의 화면/JSON schema로 제시.

**P4** 서로 다른 독립 엔진 심판과 깊이별 안정성, 상대 응수 전수 vs k3 및 재귀 전략나무, 변화가 뚜렷하지 않은 경우에는 인간에게 **"아직 구별할 근거 부족"**을 말하는 제품 정책.

**P5** Maia-2 실제 학습자 수 선호가 모델로 측정된 경우에만 학생 실력별 설명 난이도를 조절. 이후 다른 생성 모델의 해설이 들어오면 ACT-Eval의 규칙 기반 도구를 거쳐 검증 가능한 문장만 제시.

이렇게 해야 **0.29에서 연구 중인 original Stockfish source의 물리적 검색 개입 → 최종 후보 수 변화 → 동일 세계 상대 응수 강건 계획**이라는 원래 연구 질문과 제품 결과가 만난다. **원본 same-world causal join HOLD, 신규 공식 원본 코호트 7/8 HOLD**는 바꾸지 않는다.

## 미보유 문헌 (Drive 소장 우선 확인)

| 원문 | Drive 확인 | 본 단위 |
|---|---|---|
| Cui, Ling & Ng (2026) strategy verbalization | 보유 | 한 ply 상위 k=3을 제품에 재현 |
| Kim et al. (2024) CCC | 보유 | 정확한 7 규칙 개념 차분 |
| Hebbar et al. (2026) ACT-Eval | 보유 | 합법/체크/포획 검증 |
| Tang et al. (2024) Maia-2 | 보유 | 앞으로의 실제 사용자 모형 통합 대상 |

**직접 확인한 선행 논문의 추가 미보유 없음.** 코드·원문 문단 복사와 과학적 방법의 적법한 재현은 구별한다. 각 구현의 출처를 명시하고, 데이터·모델·코드의 라이선스를 준수한다.
