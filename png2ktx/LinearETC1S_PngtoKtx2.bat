@echo off
setlocal enabledelayedexpansion

:: Get current directory name (e.g. SmallRain_fore)
for %%A in ("%cd%") do set "folder_name=%%~nxA"
set "output_dir=!folder_name!ETC1S"

echo Batch converting PNG to KTX2 (ETC1S)...
echo Output folder: !output_dir!

:: Create target folder if it doesn't exist
if not exist "!output_dir!" (
    mkdir "!output_dir!"
    echo Folder created: !output_dir!
)

:: Batch convert PNG to KTX2
for %%f in (*.png) do (
    set "filename=%%~nf"
    echo Processing: %%f
toktx --encode etc1s --t2 --target_type RGBA --clevel 5 --qlevel 255 --assign_oetf linear "!output_dir!\!filename!.ktx2" "%%f"

)

echo Conversion complete! All files saved to [!output_dir!] folder.
pause