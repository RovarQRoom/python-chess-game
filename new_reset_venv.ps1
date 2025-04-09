# Simple PowerShell script to reset virtual environment

# Stop the script if any command fails
$ErrorActionPreference = "Stop"

# Step 1: Remove existing venv if it exists
Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
if (Test-Path -Path ".\venv") {
    Remove-Item -Path ".\venv" -Recurse -Force
}

# Step 2: Create new virtual environment
Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv venv

# Step 3: Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Step 4: Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Step 5: Set up chess assets
Write-Host "Setting up chess assets..." -ForegroundColor Green

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

# Display summary
Write-Host "`nAsset setup summary:" -ForegroundColor Green
Write-Host "Successfully copied: $success files" -ForegroundColor Cyan
Write-Host "Failed to copy: $failed files" -ForegroundColor $(if ($failed -gt 0) { "Yellow" } else { "Cyan" })

if ($failed -gt 0) {
    Write-Host "`nWarning: Some chess piece images could not be found." -ForegroundColor Yellow
    Write-Host "The game will use text fallback for missing pieces." -ForegroundColor Yellow
    Write-Host "Please check that the source directory exists: $sourceDir" -ForegroundColor Yellow
} else {
    Write-Host "`nAll chess piece images were successfully copied!" -ForegroundColor Green
}

Write-Host "`nSetup complete!" -ForegroundColor Cyan
Write-Host "You can now run the game with: python main.py" -ForegroundColor Cyan 