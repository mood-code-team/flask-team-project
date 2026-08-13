# =============================================================================
#  gallery 충돌 반복 해결 (pull / stash pop 루프 끊기)
# =============================================================================
#
#  [왜 자꾸 충돌?]
#  stash(임시 저장) 안에 예전 gallery.py 수정이 들어 있습니다.
#  pull로 맞춘 뒤 stash pop 하면 같은 2파일이 또 충돌 → 무한 반복.
#
#  [해결]
#  gallery 2파일은 항상 GitHub frontend 최신본 사용.
#  stash에 gallery 수정이 있어도 이 스크립트가 원격으로 덮어씁니다.
#
#  powershell -File scripts/resolve_frontend_pull_conflict.ps1
#
# =============================================================================

$ErrorActionPreference = "Continue"
Set-Location (Split-Path $PSScriptRoot -Parent)

$conflictFiles = @(
    "routes/gallery.py",
    "services/gallery_service.py"
)

function Get-FrontendRef {
    foreach ($remote in @("team", "origin")) {
        git remote get-url $remote 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { continue }
        git fetch $remote frontend 2>$null
        if ($LASTEXITCODE -eq 0) {
            return "$remote/frontend"
        }
    }
    return "frontend"
}

function Restore-GalleryFromRemote {
    param([string]$Ref)
    $ok = $true
    foreach ($file in $conflictFiles) {
        if (-not (Test-Path $file)) { continue }
        git checkout $Ref -- $file 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout --theirs $file 2>$null
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "      ✗ 실패: $file"
            $ok = $false
            continue
        }
        git add $file 2>$null
        Write-Host "      ✓ $file ← $Ref"
    }
    return $ok
}

function Test-GalleryConflictMarkers {
    foreach ($file in $conflictFiles) {
        if (-not (Test-Path $file)) { continue }
        if (Select-String -Path $file -Pattern "^<<<<<<< " -Quiet) {
            return $true
        }
    }
    return $false
}

Write-Host ""
Write-Host "========================================"
Write-Host " gallery 충돌 반복 끊기"
Write-Host "========================================"
Write-Host ""
Write-Host "원인: stash 안의 예전 gallery 코드가 pop 할 때마다 다시 충돌"
Write-Host "대응: gallery 2파일은 무조건 frontend(원격) 최신본 사용"
Write-Host ""

$fetchRef = Get-FrontendRef
Write-Host "[1] fetch → $fetchRef"
Write-Host ""
Write-Host "[2] 현재 상태"
git status --short
Write-Host ""

# merge 중이면 gallery만 먼저 정리
if (Test-Path ".git/MERGE_HEAD") {
    Write-Host "[3] merge 중 → gallery 2파일 원격으로"
    Restore-GalleryFromRemote $fetchRef | Out-Null
    git commit -m "merge: gallery 충돌 해결 (frontend 원격 기준)" 2>$null
    Write-Host "      merge commit 완료"
} elseif (Test-GalleryConflictMarkers) {
    Write-Host "[3] 파일에 <<<<<<< 남음 → gallery 원격으로"
    Restore-GalleryFromRemote $fetchRef | Out-Null
    git commit -m "fix: gallery 충돌 표시 제거 (frontend 원격 기준)" 2>$null
} else {
    Write-Host "[3] gallery 원격본으로 맞춤 (예방)"
    Restore-GalleryFromRemote $fetchRef | Out-Null
}

Write-Host ""
$stash = git stash list 2>$null
if ($stash) {
    Write-Host "[4] stash pop (gallery는 pop 후에도 원격으로 다시 맞춤)"
    git stash pop 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0 -or (Test-GalleryConflictMarkers)) {
        Write-Host ""
        Write-Host "      → stash pop 후 gallery 재충돌 (예상됨) → 원격으로 다시 덮어씀"
        Restore-GalleryFromRemote $fetchRef | Out-Null
    }
    # stash pop 실패해도 gallery만 정리됐으면 나머지 충돌 확인
    if (Test-GalleryConflictMarkers) {
        Write-Host "      ✗ gallery에 <<<<<<< 아직 남음. VS Code 수동 확인 필요"
        exit 1
    }
    # 다른 파일 충돌
    $status = git status --porcelain 2>$null
    if ($status -match "^UU|^AA|^DD") {
        Write-Host ""
        Write-Host "      ⚠ gallery 외 다른 파일 충돌 있음. 해당 파일만 VS Code에서 정리:"
        git status --short | Select-String "^UU|^AA"
        Write-Host "      정리 후: git add .  &&  git commit -m \"stash 적용\""
        Write-Host "      gallery 2파일은 건드리지 마세요 (이미 원격본)"
    } elseif ($status -match "^[MADRCU].*") {
        git add -A 2>$null
        git diff --cached --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            git commit -m "chore: stash 적용 (gallery는 frontend 유지)" 2>$null
            Write-Host "      → 나머지 stash 변경 commit 완료"
        }
    }
    # pop 실패 시 stash 남아있을 수 있음 — gallery 제외하고 적용됐으면 drop 안내
    if (git stash list 2>$null) {
        Write-Host ""
        Write-Host "      참고: stash가 아직 남아 있으면 gallery 충돌 때문일 수 있음."
        Write-Host "      gallery 말고 다른 작업은 위에서 commit 됐다면:"
        Write-Host "        git stash drop"
    }
} else {
    Write-Host "[4] stash 없음"
}

Write-Host ""
Write-Host "========================================"
Write-Host " 완료"
Write-Host "========================================"
Write-Host "  앞으로 gallery.py / gallery_service.py 는"
Write-Host "  로컬에서 수정하지 말고 frontend pull 만 하세요."
Write-Host "  (수정 필요하면 frontend 브랜치에 push 후 pull)"
Write-Host ""
