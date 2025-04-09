# Simple PowerShell script to copy chess assets

# Source directory
$sourceDir = ".\assets\PNGs\With Shadow\128px"

# Target directory
$targetDir = ".\assets"

# Image mappings
$mappings = @(
    @{ "Source" = "w_pawn_png_shadow_128px.png"; "Target" = "wP.png" },
    @{ "Source" = "w_rook_png_shadow_128px.png"; "Target" = "wR.png" },
    @{ "Source" = "w_knight_png_shadow_128px.png"; "Target" = "wN.png" },
    @{ "Source" = "w_bishop_png_shadow_128px.png"; "Target" = "wB.png" },
    @{ "Source" = "w_queen_png_shadow_128px.png"; "Target" = "wQ.png" },
    @{ "Source" = "w_king_png_shadow_128px.png"; "Target" = "wK.png" },
    @{ "Source" = "b_pawn_png_shadow_128px.png"; "Target" = "bP.png" },
    @{ "Source" = "b_rook_png_shadow_128px.png"; "Target" = "bR.png" },
    @{ "Source" = "b_knight_png_shadow_128px.png"; "Target" = "bN.png" },
    @{ "Source" = "b_bishop_png_shadow_128px.png"; "Target" = "bB.png" },
    @{ "Source" = "b_queen_png_shadow_128px.png"; "Target" = "bQ.png" },
    @{ "Source" = "b_king_png_shadow_128px.png"; "Target" = "bK.png" }
)

Write-Host "Copying chess pieces..." -ForegroundColor Green

$success = 0
$failed = 0

foreach ($mapping in $mappings) {
    $sourcePath = Join-Path -Path $sourceDir -ChildPath $mapping.Source
    $targetPath = Join-Path -Path $targetDir -ChildPath $mapping.Target
    
    if (Test-Path -Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $targetPath -Force
        Write-Host "Copied $($mapping.Source) to $($mapping.Target)" -ForegroundColor Cyan
        $success++
    } else {
        Write-Host "Could not find $($mapping.Source)" -ForegroundColor Yellow
        $failed++
    }
}

Write-Host "`nCopied $success files, failed to copy $failed files." -ForegroundColor Green
Write-Host "Run the game with: python main.py" -ForegroundColor Green 