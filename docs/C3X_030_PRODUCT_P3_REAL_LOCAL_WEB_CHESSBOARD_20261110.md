# C3X 0.30/P3 — 로컬 체스판 UI → 실제 Stockfish 검색 → 대조적 학습 해설

**연구/제품 기록:** 2026-11-10 KST. **상태:** 실제 GitHub Actions의 로컬 HTTP 엔드포인트에 원본 Stockfish16을 연결해 **전체 API 경로 검증 성공**, 누적 **35개 회귀 테스트 성공**, 원본 보고서 JSON 및 한국어 Markdown 아티팩트 생성.

## I. 최초 궁금증 및 선행연구 귀속

[2026-08-14 **C3X 1.md 원본**, Google Drive](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view): Stockfish를 공부하는 일반인이 *왜 A가 B보다 근소하게 좋은지* 이해하도록 만들 수 있는가?

- [**Cui, Ling & Ng (2026) 원문, Drive**](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view): 반응별 계획 및 엔진 평가. 현재 제품의 1개 상대 ply의 최대 k=3 engine-ranked 응수·실제 다음 자기 수 실험만 가져왔고 원문 재귀 전략나무·전략 언어화·효용 평가는 재현하지 못했다.
- [**Kim et al. (2024) Concept-guided Chess Commentary 원문, Drive**](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view): 인간에게 의미 있는 개념. 현재 제품은 7개 **규칙 기반** 개념의 후보 간 차분만 구현했고 원문의 학습된 concept classifier나 원래 연구의 사용자 평가를 재현한 것은 아니다.
- [**Hebbar et al. (2026) ACT-Eval 원문, Drive**](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view): 불법 수 및 체크·포획 등 원자 명제에 대한 정확한 체스 규칙 검사.
- 제품 P1/P2는 [**이전 실제 Stockfish/CCC 해설 제품 과학 보고서**](C3X_030_PRODUCT_P1_P2_REAL_LEARNER_EXPLAINER_AND_COMPETITIVE_EVIDENCE_20261110.md)에 실제 원본 SHA와 결과 기록. 이번 P3은 알고리즘을 새로 만든 것이 아니라 **사용 가능한 제품 인터페이스로 통합**했다.

## II. 구현된 4개 층

**클라이언트:** [`product/c3x_board.html`](../product/c3x_board.html) + [`product/c3x_board.js`](../product/c3x_board.js), 외부 패키지/외부 폰트/분석 API 없음. FEN 입력, 현재 국면 렌더링, 출발·도착 칸 클릭 및 A/B 후보 선택, 실제 합법 수 SAN dropdown, depth8/10 후보 gap, source response tree 최대 3회씩, 7개 실제 개념 중 차이만 표시, 원본 JSON 확인, 한국어 Markdown 저장.

**로컬 Python API:** [`product/c3x_local_web.py`](../product/c3x_local_web.py). `127.0.0.1` 고정 바인딩, `GET /` HTML, `GET /c3x_board.js` JS, `GET /api/health` health, `POST /api/legal` FEN validation and exact legal UCI/SAN, `POST /api/analyze` FEN+두 실제 UCI 후보를 사용한 원본 Stockfish 분석. 사용자 임의 엔진 경로/셸 명령/파일 읽기 입력은 API에서 거부. 입력 크기 최대 4096 bytes, 허용 필드 정확히 3개, 법적으로 불가능한 두 후보는 네이티브 엔진을 열기 전에 **422**로 거부. Origin 검사, CSP, no-store, clickjacking 관련 응답 헤더 포함.

**실제 원본 검색:** `product/c3x_explain_two_moves.py`를 그대로 재사용. Stockfish16 원본 `68e1e9b3811e16cad014b590d7443b9063b3eb52`를 CI에서 직접 체크아웃하고 빌드했다. CPU 1 thread, 16MB Hash, NNUE off. 두 후보 root depth8/10 forced selection, 각 후보 이하 max k3 opponent replies MultiPV depth8 + 실제 다음 자기 수에 대한 depth8 native continuation. **독립 referee 아님, 전체 응수 검사 아님**, 내부 source search 개입 실험 아님.

**실제 개념 차분:** `product/c3x_concept_contrast.py`를 그대로 재사용해 원래 FEN과 두 UCI로 확정한 7개 개념을 계산. P1 두 후보와 P2 두 후보 사이의 보드·UCI identity를 서버 안에서 강제 검증한 다음 JSON+한국어 Markdown 연결. 이 기능은 둘 다 알고리즘에서 직접 측정한 사실을 출력하되 **엔진이 그렇게 판단한 물리적 계산 원인까지 입증한 것은 아님**.

## III. 어떻게 실행하는가? (로컬 사용자용)

리포지토리를 내려받고 Python 3.12 및 Stockfish UCI 바이너리가 준비된 상태에서:

```bash
python -m pip install 'chess==1.11.2'
python product/c3x_local_web.py --stockfish /absolute/path/to/stockfish --port 8765
```

로컬 브라우저에서 **`http://127.0.0.1:8765`** 접속. Windows에서는 `--stockfish "C:\\path\\to\\stockfish.exe"` 같은 실제 바이너리 경로를 사용한다. 이 프로토타입은 공인 인터넷 서버에 게시하지 않으며, 포트 8765에서 localhost만 허용한다.

**주의:** CI에서 원본 commit과 실제 실행 바이너리를 연결해 검증했으나, 사용자가 임의의 다른 Stockfish 바이너리를 넘긴 로컬 실행에 대해 업스트림 버전이 동일하다고 자동 보증하지는 않는다. 정확한 비교 재현을 위해서는 CI에서 사용한 commit의 바이너리를 직접 빌드하고 적어야 한다. 로컬 노트북/PC 실제 사용자 실행은 아직 관측하지 않았다.

## IV. 실제 CI를 통과한 결과

[**P3 실제 HTTP end-to-end GitHub Actions #42787312373 — SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42787312373).

- P1/P2/P3 총 **35개 테스트 GREEN**, `node --check`로 JavaScript 구문 검사, API mock-only가 아닌 실제 loopback HTTP 시험.
- 실제 공식 Stockfish 소스를 정확한 SHA로 체크아웃하고 원본 바이너리를 빌드.
- 별도의 로컬 HTTP 서버 프로세스를 기동해 `GET /`의 실제 HTML, `GET /c3x_board.js`의 JS, `POST /api/legal`의 20개 시작 국면 합법 수, 실제 **`POST /api/analyze` (시작 FEN; e2e4 vs d2d4)**까지 확인.
- 본 Native HTTP end-to-end 시험에서 root 후보 2개 × depth8/10, opponent 상위 replies [3, 3], 정확한 7개 개념 모두 실제 계산했고 두 시작 수 사이 다른 개념 **0개**, 동일 **7개**. 당장 차이가 없다고 억지 설명을 만들지 않는 제품 동작을 입증.
- 실제 불법 수 `e2e5` 입력은 엔진을 실행하지 않고 HTTP **422**를 돌려줌.
- **학생용 JSON SHA256** `da06c35fe9e2608fc5c2855f78602b8d057a23d1ce925a04f1c01109c089b2c8`; **학생용 한국어 MD SHA256** `c02ef85183be0c6c1d2556b4b7eacfa6fdbeb85a744651a2e9fa86a7d2ed803d`.
- Native 아티팩트: `c3x030-p3-REAL-local-HTTP-chessboard-full-stack-native-Stockfish`, ID **13749418850**, archive digest `sha256:f03ec99b69278c41a5c310761bcb14a6168c9e10f044dfb35cc997ee72ee0648`.

**이미 실험한 원래 근소 후보 사례는 P1/P2 실제 Sahel/Cerrado, P3 HTTP E2E에 쓴 초기 국면은 UI 시스템 동작만 확인하려는 표준 시작 FEN이다.** 시작 수 e4/d4의 깊이10 점수 차를 원래 연구의 원본 근소 전략 사례로 바꾸어 주장하지 않는다. 또한 실제 브라우저 렌더링을 스크린샷으로 수락·검수하지 않았으므로 **UX 시각 수락 검증 HOLD** (HTML/JS 정적·실제 HTTP는 통과).

## V. 사용자에게 보여줄 '좋은 해설'의 근거 정책

1. **RULE_EXACT** (합법/포획/체크/기물과 폰·공격 그래프): 정확한 체스 규칙에 근거.
2. **SOURCE_ENGINE_MEASURED** (한 국면에서 depth8/10 평가, 일부 상대 응수): 실행한 Stockfish 검증 범위에 한정.
3. **INDEPENDENT_REFEREE_MEASURED**: 현재 제품 **HOLD**. 0.29의 독립 Berserk 연구와 미래 같은 세계 대조를 연결할 수 있으나 UI의 현재 결과인 것처럼 보여서는 안 됨.
4. **ORIGINAL_SEARCH_DECISION_CAUSAL**: 초기 C3X 질문의 강한 연구 목표이며 **HOLD**. 기물 개념이 변한 사실은 엔진 내부 최종 선택의 원인이라는 증거와 다름.
5. **HUMAN_LEARNING_BENCHMARK**: Chess.com/Lichess와 비교한 블라인드 사용자 학습 실험 **0회**, 우수성 주장 **HOLD**.

## VI. 다음 개발: P4

먼저 GitHub CI에서 **실제 브라우저 렌더링을 Playwright screenshot과 자동 화면 수락으로 검증**, 그다음 체스판과 수순 화살표를 연결하고 여러 깊이의 PV를 직관적으로 표시하자. P1/P2 JSON을 통한 원본 결과는 변조하지 않는다. 이후 독립 referee 평가, Cui의 recursion k3, Maia-2의 인간의 수 선택 분포를 각기 독립된 source/rights/provenance 계약으로 붙인다.

## Drive 미보유 문헌

| 직접 인용한 선행연구 | 원문 Drive | 상태 |
|---|---|---|
| Cui, Ling & Ng (2026) | [원본 PDF](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) | 보유 |
| Kim et al. (2024) CCC | [원본 PDF](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view) | 보유 |
| Hebbar et al. (2026) ACT-Eval | [원본 PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) | 보유 |
| C3X 최초 질문 | [C3X 1.md](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view) | 보유 |

**이번 단위 직접 인용 문헌 중 추가 미보유 없음.** 원본 0.29 prereg 신규 소스 적격 7/8 HOLD와 original source-engine calculation→choice→future-plan SAME-WORLD 인과적 검증 HOLD 유지.
