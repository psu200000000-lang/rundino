# 🦕 Dino Running Game

Chrome의 공룡 게임을 Python(Pygame)과 HTML5 Canvas로 구현한 프로젝트입니다.

## 🎮 게임 소개

- **Python 버전**: Pygame 라이브러리를 사용한 독립 실행 버전
- **Web 버전**: HTML5 Canvas와 JavaScript를 사용한 웹 버전
- **3가지 난이도**: 쉬움, 보통, 어려움
- **점수 저장**: 최고점을 로컬에 저장

## 🚀 시작하기

### Python 버전 실행

1. Python 3.x 설치 확인
2. 프로젝트 폴더 이동:
   ```bash
   cd /path/to/rundino
   ```
3. 의존성 설치:
   ```bash
   pip install pygame
   ```
4. 게임 실행:
   ```bash
   python game.py
   ```

### Web 버전 실행

1. [psu200000000.github.io./rundino/](psu200000000.github.io./rundino/)을 웹 브라우저에서 열면 됩니다.
   - 또는 간단한 HTTP 서버 실행:
   ```bash
   python -m http.server 8000
   ```

## 🎮 조작법

| 동작 | 키/입력 |
|------|--------|
| 점프 | <kbd>Space</kbd> 또는 <kbd>↑</kbd> |
| 재시작 | <kbd>Enter</kbd> |
| 난이도 변경 | 화면 좌상단 버튼 클릭 |

## 📁 파일 구조

```
rundino/
├── [game.py](game.py)           # Python Pygame 버전
├── [game.html](game.html)       # HTML 마크업
├── [script.js](script.js)       # JavaScript 게임 로직
├── [style.css](style.css)       # 게임 스타일
├── [dino_high.json](dino_high.json)    # 최고점 저장 파일
└── README.md         # 이 파일
```

## ⚙️ 난이도 설정

- **쉬움**: 느린 속도, 많은 시간차
- **보통**: 기본 설정 (기본값)
- **어려움**: 빠른 속도, 짧은 시간차

## 💾 데이터 저장

최고점은 `dino_high.json` 파일에 자동으로 저장됩니다.
