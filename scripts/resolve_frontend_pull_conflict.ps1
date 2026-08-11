# =============================================================================
#  frontend pull 충돌 자동 해결 스크립트
# =============================================================================
#
#  [언제 쓰나요?]
#  git pull team frontend (또는 origin frontend) 후 아래처럼 멈췄을 때:
#    - CONFLICT in routes/gallery.py
#    - CONFLICT in services/gallery_service.py
#    - git stash pop 이 "충돌 때문에 불가" 라고 할 때
#
#  [왜 이런 일이 생기나요?]
#  1) 내 PC에 예전 gallery 코드가 있고
#  2) GitHub frontend 브랜치에도 gallery 수정이 올라와서
#  3) 같은 파일을 Git이 자동으로 합치지 못해 <<<<<<< 표시가 생깁니다.
#
#  Git은 "충돌이 남아 있으면 stash pop(임시 저장 꺼내기)"을 막습니다.
#  그래서 순서가 반드시: ① 충돌 해결 → ② commit → ③ stash pop 입니다.
#
#  [이 스크립트가 하는 일]
#  - gallery.py, gallery_service.py → frontend(원격) 최신 버전으로 맞춤
#    (피그마 UI + 백엔드 핫스팟 + C타입 카피가 이미 remote에 반영됨)
#  - merge commit 생성
#  - stash 가 있으면 pop
#
#  [실행 방법]  프로젝트 폴더에서:
#    powershell -File scripts/resolve_frontend_pull_conflict.ps1
#
# =============================================================================

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host ""
Write-Host "========================================"
Write-Host " frontend pull 충돌 해결"
Write-Host "========================================"
Write-Host ""
Write-Host "※ gallery 2개 파일은 '팀 frontend(원격)' 버전을 씁니다."
Write-Host "  내 로컬 gallery 수정은 이 파일들에서 덮어씌워질 수 있습니다."
Write-Host "  (다른 파일 작업은 stash pop 후 그대로 남습니다)"
Write-Host ""

Write-Host "[1/4] 현재 Git 상태 확인"
Write-Host "      (UU = 아직 충돌 중, M = 수정됨)"
git status --short

$conflictFiles = @("routes/gallery.py", "services/gallery_service.py")
$inMerge = Test-Path ".git/MERGE_HEAD"

if (-not $inMerge) {
    $hasMarkers = Select-String -Path $conflictFiles -Pattern "^<<<<<<< " -ErrorAction SilentlyContinue
    if (-not $hasMarkers) {
        Write-Host ""
        Write-Host "  → 지금은 merge 충돌 상태가 아닙니다."
        Write-Host "    먼저: git pull team frontend"
        Write-Host "    충돌 나면 이 스크립트를 다시 실행하세요."
        Write-Host ""
    }
}

Write-Host ""
Write-Host "[2/4] gallery 충돌 파일 → frontend(원격) 버전으로 선택"
Write-Host "      routes/gallery.py"
Write-Host "      services/gallery_service.py"
foreach ($file in $conflictFiles) {
    if (-not (Test-Path $file)) { continue }
    # pull 받을 때: --theirs = 방금 받은 remote(frontend) 쪽
    git checkout --theirs $file 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout --ours $file 2>$null
    }
    git add $file
}
Write-Host "      → 충돌 표시(<<<<<<<) 제거 후 staging 완료"

Write-Host ""
if ($inMerge) {
    Write-Host "[3/4] merge commit (충돌 해결 기록)"
    git commit -m "merge: frontend pull 충돌 해결 (gallery 원격 기준)"
    Write-Host "      → commit 완료. 이제 stash pop 가능합니다."
} else {
    Write-Host "[3/4] merge commit 생략"
    Write-Host "      → MERGE_HEAD 없음 (이미 commit 됐거나 pull 전 상태)"
}

Write-Host ""
$stash = git stash list 2>$null
if ($stash) {
    Write-Host "[4/4] git stash pop — 임시 저장해 둔 내 작업 꺼내기"
    git stash pop
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  ⚠ stash pop에서 또 충돌 났습니다."
        Write-Host "    VS Code에서 <<<<<<< 표시 찾아서 수동 정리 후:"
        Write-Host "      git add ."
        Write-Host "      git commit -m \"stash 적용\""
        exit 1
    }
    Write-Host "      → stash 적용 완료"
} else {
    Write-Host "[4/4] stash 없음 — 건너뜀"
}

Write-Host ""
Write-Host "========================================"
Write-Host " 완료"
Write-Host "========================================"
Write-Host "  다음 확인:"
Write-Host "    1) 서버 재시작 (실행_서버.bat)"
Write-Host "    2) 브라우저: /  /gallery  /category/light"
Write-Host ""
