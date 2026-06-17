param($binFile)

if (-not (Test-Path $binFile)) {
    Write-Host "File not found: $binFile"
    exit 1
}

$bytes = [System.IO.File]::ReadAllBytes($binFile)

if ($bytes.Length -lt 32) {
    Write-Host "File too small"
    exit 1
}

$sum = 0L
for ($i = 0; $i -lt 7; $i++) {
    $word = [BitConverter]::ToUInt32($bytes, $i * 4)
    $sum = ($sum + $word) -band 0xFFFFFFFFL
}

$checksum = (0xFFFFFFFFL - $sum + 1L) -band 0xFFFFFFFFL
$checksumBytes = [BitConverter]::GetBytes([uint32]$checksum)

for ($i = 0; $i -lt 4; $i++) {
    $bytes[28 + $i] = $checksumBytes[$i]
}

[System.IO.File]::WriteAllBytes($binFile, $bytes)
Write-Host ("LPC Checksum patched successfully: 0x{0:X8}" -f $checksum)
