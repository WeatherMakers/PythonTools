@echo off
setlocal enabledelayedexpansion

:: 获取当前目录名称
for %%A in ("%cd%") do set "folder_name=%%~nxA"
set "output_dir=!folder_name!_ASTC12x12_Linear"

echo Batch converting PNG to ASTC (12x12, Linear, Exhaustive)...
echo Output folder: !output_dir!

:: 创建目标文件夹（如果不存在）
if not exist "!output_dir!" (
    mkdir "!output_dir!"
    echo Folder created: !output_dir!
)

:: 批量转换PNG到ASTC
for %%f in (*.png) do (
    set "filename=%%~nf"
    echo Processing: %%f
    astcenc-sse4.1 -cl "%%f" "!output_dir!\!filename!.astc" 12x12 -exhaustive
)

echo Conversion complete! All files saved to [!output_dir!] folder.
pause
