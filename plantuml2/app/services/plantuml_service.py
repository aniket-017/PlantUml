# app/services/plantuml_service.py
import subprocess
from pathlib import Path

PLANTUML_JAR = Path(__file__).resolve().parents[1] / "plantuml.jar"  # backend/plantuml.jar

def render_plantuml_from_text(puml_text: str, output_dir: str, filename_base: str = "plantuml"):
    """
    Write a .puml and call local plantuml.jar to render a PNG.
    Returns the path to the produced PNG.
    """
    try:
        print("=== RENDER_PLANTUML_START ===")
        print(f"Timestamp: {__import__('datetime').datetime.now()}")
        print(f"Output directory: {output_dir}")
        print(f"Filename base: {filename_base}")
        print(f"PlantUML text length: {len(puml_text)}")
        
        outdir = Path(output_dir)
        print(f"Creating output directory: {outdir}")
        outdir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory created/verified")
        
        puml_file = outdir / f"{filename_base}.puml"
        png_file = outdir / f"{filename_base}.png"
        print(f"PlantUML file path: {puml_file}")
        print(f"Expected PNG path: {png_file}")

        print("Writing PlantUML file...")
        puml_file.write_text(puml_text, encoding="utf-8")
        print(f"✓ PlantUML file written successfully")

        print(f"Checking for PlantUML jar at: {PLANTUML_JAR}")
        if not PLANTUML_JAR.exists():
            print(f"✗ ERROR: plantuml.jar not found at {PLANTUML_JAR}")
            raise FileNotFoundError(f"plantuml.jar not found at {PLANTUML_JAR}")
        print(f"✓ PlantUML jar found")

        # Check if Java is available
        print("Checking Java availability...")
        try:
            result = subprocess.run(["java", "-version"], check=True, capture_output=True, text=True)
            print(f"✓ Java is available")
            print(f"Java version output: {result.stderr[:100]}...")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"✗ ERROR: Java is not installed or not in PATH: {str(e)}")
            raise Exception("Java is not installed or not in PATH")

        # call PlantUML to generate PNG
        cmd = ["java", "-jar", str(PLANTUML_JAR), "-tpng", str(puml_file), "-charset", "UTF-8"]
        print(f"Running PlantUML command: {' '.join(cmd)}")
        print(f"Working directory: {outdir}")
        
        result = subprocess.run(cmd, check=True, cwd=str(outdir), capture_output=True, text=True)
        print(f"✓ PlantUML command executed successfully")
        print(f"PlantUML stdout: {result.stdout}")
        if result.stderr:
            print(f"PlantUML stderr: {result.stderr}")

        # PlantUML usually writes png alongside the puml file
        print(f"Checking if PNG file exists at: {png_file}")
        if not png_file.exists():
            print("PNG file not found at expected location, searching for alternatives...")
            # PlantUML may name output differently; search for *.png in outdir matching filename_base
            matches = list(outdir.glob(f"{filename_base}*.png"))
            if matches:
                print(f"✓ Found PNG file: {matches[0]}")
                print("=== RENDER_PLANTUML_SUCCESS ===")
                return str(matches[0])
            else:
                print(f"✗ ERROR: No PNG files found matching pattern {filename_base}*.png")
                print(f"Files in directory: {list(outdir.glob('*'))}")
                raise FileNotFoundError("PlantUML did not produce a PNG.")
        else:
            print(f"✓ PNG file found at expected location: {png_file}")
        
        print("=== RENDER_PLANTUML_SUCCESS ===")
        return str(png_file)
    except Exception as e:
        print(f"=== RENDER_PLANTUML_ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("=== RENDER_PLANTUML_ERROR_END ===")
        raise