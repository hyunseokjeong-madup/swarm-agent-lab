# research/ — 에이전트 선별 실험 (아카이브)

MADOBI의 **챔피언 전략이 어떻게 선별됐는지**를 기록한 실험 자료. 제품 사용에는 불필요하며,
방법론·재현용 아카이브다. (제품은 최상위 `marketing/`, `.claude/`, `tests/`, `docs/`.)

## 내용
- `optimization_log.md` — 스웜 최적화 운영 일지(Gen0~5, 과정·교훈)
- `KNOWHOW.md` — 최적화 누적 지식 · `TEAM.md` — 팀 조직도 · `REPORT.md` — 실험 리포트
- `benchmark/` — 코드검증 추론 벤치(20문항) 생성기/정답
- `designs/` — 시드 전략 + Planner 역할 정의
- `results/` — 세대별 결과 데이터(랭킹·집단·결선) ※ 원자료 덤프·eval 스크립트는 정리(재생성 가능)
- 스크립트: `make_eval_script.py`(워크플로 생성), `merge_and_rank.py`, `score.py`, `track.py`,
  `extract_pop.py`, `gen_designs.js`, `swarm_eval.js`, `eval_swarm_args.js`

## 핵심 결론
검증(adversarial self-verify) + 다수결 전략(`F03_adversarial_c`)이 4세대 토너먼트에서 최강 →
이 전략을 마케팅 정합성에 특화한 것이 제품 **MADOBI**.

---

## ⚠️ `.js` 파일은 무엇인가 — 기여자(contributor)는 실행할 필요 없음

> **이 디렉터리(`research/`)는 동결 아카이브(FROZEN ARCHIVE)다.** 검증 우선(verification-first)
> 챔피언 전략이 **어떻게 발견됐는지**를 남긴 종이흔적(paper-trail)일 뿐, **제품 코드가 아니다.**
> 여기 있는 3개의 `.js`는 일회성 Gen0~5 토너먼트를 돌릴 때만 쓴 평가 스크립트다.
> **OSS 기여자가 빌드·테스트·실행할 이유가 전혀 없다.** 제품(`marketing/`, `.claude/`,
> `tests/`)과 핵심 불변식(외부 의존성 0 · Python 표준 라이브러리만)은 이 JS와 무관하다.

이 레포는 Python 전용인데 JS가 섞여 있어 혼란을 줄 수 있어 명시한다:

| 파일 | 역할 |
|------|------|
| `gen_designs.js` | **디자이너 스웜(generator).** 14개 전략 패밀리(F01~F14) × 각 8개 = 약 100개의 closed-book 추론 "운영 매뉴얼(메타프롬프트)" 후보를 병렬 생성. Gen0 초기 집단을 키우는 데 한 번 사용. |
| `swarm_eval.js` | **Gen1 스웜 평가기(self-contained).** 4개 시드 설계(C0~C3) × 10개 벤치 문제 = 40개 평가 노드를 closed-book(도구·코드 실행 금지)으로 병렬 채점. 설계·문제를 스크립트에 직접 내장(`args` 전달이 불안정해서 — `optimization_log.md` Gen1 노트 참고). |
| `eval_swarm_args.js` | 위와 같은 평가기이나 **데이터를 `args`로 주입**하는 일반화 버전(`designs × problems × trials`). `args` 전송이 검증되면 쓰려던 변형. 실제 세대는 self-contained 쪽(`swarm_eval.js` / `make_eval_script.py` 산출물)을 사용. |

### 실행 환경 (참고 — 재현하려는 사람만)
- 이 `.js`들은 **`node foo.js`로 직접 실행하는 일반 Node 스크립트가 아니다.** `agent()`,
  `parallel()`, `phase()`, `log()` 같은 전역(global)과 LLM 노드를 제공하는 **Workflow 스웜 러너**가
  주입·실행한다(파일 상단 `export const meta` + 글로벌 호출 = Workflow 컨벤션). 단독으로 `node`에
  넣으면 위 전역이 없어 동작하지 않는다.
- 형식상 ESM 모듈이라 ES2020+(`async`/`await`, optional chaining)을 이해하는 Node 14+급 엔진을 가정하지만,
  **버전 핀(pin)은 없다** — 실행 주체는 Node CLI가 아니라 Workflow 러너이기 때문.
- 평가 스크립트 생성은 Python(`make_eval_script.py`)이 담당하며, **LF 전용·ASCII**로 emit해야 한다
  (CRLF는 Workflow 권한 훅에 차단됨 — `REPORT.md` §7 참고).

**요약: 이 JS는 일회성 토너먼트의 흔적이다. 보존된 IP일 뿐, 제품 동작과 무관하고 재실행 불필요하다.**
