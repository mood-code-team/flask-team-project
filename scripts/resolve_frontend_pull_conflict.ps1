# =============================================================================
#  frontend pull 충돌 자동 해결 — gallery.py / gallery_service.py
# =============================================================================
#
#  VS Code에 이렇게 보이면 이 스크립트 또는 docs/GALLERY_충돌_해결.txt 참고:
#
#    <<<<<<< HEAD
#    (내 코드)
#    =======
#    (팀원/원격 코드)   ← 이쪽(origin/frontend)만 남기면 됨
#    >>>>>>> origin/frontend
#
#  [실행]  프로젝트 폴더에서:
#    git fetch team frontend
#    powershell -File scripts/resolve_frontend_pull_conflict.ps1
#
# =============================================================================

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$conflictFiles = @(
    "routes/gallery.py",
    "services/gallery_service.py"
)

Write-Host ""
Write-Host "========================================"
Write-Host " gallery 충돌 해결 (2파일)"
Write-Host "========================================"
Write-Host ""
Write-Host "[수동으로 할 때 — VS Code]"
Write-Host "  <<<<<<< HEAD 와 ======= 사이 = 내 코드 → 삭제"
Write-Host "  ======= 와 >>>>>>> origin/frontend 사이 = 팀 frontend → 유지"
Write-Host "  <<<<<<< / ======= / >>>>>>> 줄도 전부 삭제"
Write-Host ""
Write-Host "[자동] GitHub team/frontend 최신본으로 2파일 덮어쓰기"
Write-Host ""

Write-Host "[1/5] git fetch"
$remotes = @("team", "origin")
$fetched = $false
foreach ($remote in $remotes) {
    git remote get-url $remote 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        git fetch $remote frontend 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      → fetch $remote frontend OK"
            $fetchRef = "$remote/frontend"
            $fetched = $true
            break
        }
    }
}
if (-not $fetched) {
    Write-Host "      ⚠ team/origin remote 없음. fetch 생략."
    $fetchRef = "frontend"
}

Write-Host ""
Write-Host "[2/5] git status"
git status --short

$inMerge = Test-Path ".git/MERGE_HEAD"

Write-Host ""
Write-Host "[3/5] gallery 2파일 → $fetchRef 버전으로 교체"
foreach ($file in $conflictFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "      skip (없음): $file"
        continue
    }
    git checkout $fetchRef -- $file 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      checkout $fetchRef 실패 → --theirs 시도: $file"
        git checkout --theirs $file 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout --ours $file 2>$null
        }
    }
    # 혹시 <<<<<<< 가 남아 있으면 경고
    $markers = Select-String -Path $file -Pattern "^<<<<<<< " -ErrorAction SilentlyContinue
    if ($markers) {
        Write-Host "      ⚠ 아직 충돌 표시 남음! docs/GALLERY_충돌_해결.txt 보고 수동 정리: $file"
        exit 1
    }
    git add $file
    Write-Host "      OK: $file"
}

Write-Host ""
if ($inMerge) {
    Write-Host "[4/5] merge commit"
    git commit -m "merge: gallery 충돌 해결 (frontend 원격 기준)"
    Write-Host "      → commit 완료"
} else {
    $staged = git diff --cached --name-only
    if ($staged) {
        Write-Host "[4/5] commit (merge 상태 아님 — staged 변경만)"
        git commit -m "fix: gallery 파일 frontend 기준으로 정리"
    } else {
        Write-Host "[4/5] commit 생략 (변경 없음)"
    }
}

Write-Host ""
$stash = git stash list 2>$null
if ($stash) {
    Write-Host "[5/5] git stash pop"
    git stash pop
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  ⚠ stash pop 추가 충돌 → VS Code에서 <<<<<<< 수동 정리 후 git add / commit"
        exit 1
    }
} else {
    Write-Host "[5/5] stash 없음"
}

Write-Host ""
Write-Host "완료. 서버 재시작 후 /gallery 확인하세요."
Write-Host ""
