#!/usr/bin/env python3
"""
Install script for nl_calc.

Creates a single self-contained executable and adds it to the user's PATH.
Supports Linux, macOS, and Windows.
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys


def get_install_path() -> str:
    """Get the appropriate installation path for the platform."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return os.path.join(base, "Programs", "calc")
    else:
        return os.path.join(os.path.expanduser("~"), ".local", "bin")


def build_single_file():
    """Build the single-file version of nl_calc."""
    build_script = os.path.join(os.path.dirname(__file__), "build_single.py")
    if os.path.exists(build_script):
        subprocess.run([sys.executable, build_script], check=True)
        return os.path.join(os.path.dirname(__file__), "nl_calc.py")
    else:
        print("Error: build_single.py not found")
        sys.exit(1)


def create_executable(source_path: str, install_dir: str) -> str:
    """Copy the single-file executable to install directory."""
    os.makedirs(install_dir, exist_ok=True)
    dest_path = os.path.join(install_dir, "calc")
    
    with open(source_path, "r") as f:
        content = f.read()
    
    with open(dest_path, "w") as f:
        f.write(content)
    
    os.chmod(dest_path, os.stat(dest_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    return dest_path


def add_to_path(install_dir: str) -> bool:
    """Add install directory to PATH. Returns True if successful."""
    if sys.platform == "win32":
        current_path = os.environ.get("PATH", "")
        if install_dir not in current_path:
            print(f"\nTo add to PATH on Windows, run:")
            print(f'  setx PATH "%PATH%;{install_dir}"')
            print(f"\nOr manually add this to your PATH:")
            print(f"  {install_dir}")
        return False
    else:
        shell_profile = os.path.expanduser("~/.bashrc")
        zshrc = os.path.expanduser("~/.zshrc")
        
        target_file = zshrc if os.path.exists(zshrc) else shell_profile
        
        if os.path.exists(target_file):
            with open(target_file, "r") as f:
                content = f.read()
            
            export_line = f'export PATH="{install_dir}:$PATH"'
            
            if export_line in content:
                print(f"\n{install_dir} is already in your PATH configuration.")
                return True
            
            with open(target_file, "a") as f:
                f.write(f"\n# Added by nl_calc install\n{export_line}\n")
            
            current_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{install_dir}{os.pathsep}{current_path}"
            print(f"\nAdded {install_dir} to PATH in {target_file}")
            print("Note: You may need to restart your shell or run: source " + target_file)
            return True
        else:
            print(f"\nNo shell config found. Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
            print(f'  export PATH="{install_dir}:$PATH"')
            return False


def main():
    parser = argparse.ArgumentParser(description="Install calc command-line tool")
    parser.add_argument("--path", "-p", help="Custom installation directory")
    parser.add_argument("--uninstall", "-u", action="store_true", help="Uninstall calc")
    parser.add_argument("--no-path", action="store_true", help="Don't modify PATH")
    parser.add_argument("expression", nargs="*", help="Expression to evaluate after install")
    args = parser.parse_args()
    
    install_dir = args.path or get_install_path()
    
    if args.uninstall:
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
            print(f"Removed {install_dir}")
        else:
            print(f"calc is not installed at {install_dir}")
        return
    
    print("Building single-file nl_calc...")
    single_file = build_single_file()
    
    calc_path = create_executable(single_file, install_dir)
    print(f"Installed calc to: {calc_path}")
    
    already_in_path = install_dir in os.environ.get("PATH", "").split(os.pathsep)
    
    if already_in_path:
        print("\ncalc is already in your PATH!")
    elif args.no_path:
        add_to_path(install_dir)
    else:
        added = add_to_path(install_dir)
        
        if args.expression:
            expr = " ".join(args.expression)
            shell = os.path.expanduser("~/.zshrc") if os.path.exists(os.path.expanduser("~/.zshrc")) else os.path.expanduser("~/.bashrc")
            new_path = f"{install_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            print(f"\nRunning: calc {expr}")
            result = subprocess.run(
                ["bash", "-c", f"source {shell} && calc {expr}"],
                env={**os.environ, "PATH": new_path}
            )
            sys.exit(result.returncode)
        
        if added:
            print(f"\nSpawning interactive shell with calc available...")
            print(f"Run 'calc <expression>' to use it. Type 'exit' to quit.\n")
            new_path = f"{install_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            subprocess.run(
                ["bash", "-i"],
                env={**os.environ, "PATH": new_path}
            )
            return
        
        print(f"\nTo use calc, either:")
        print(f'  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)')
        print(f"  2. Run with full path: {install_dir}/calc")
        print(f"\nExample:")
        print(f'  {install_dir}/calc "five plus two"')
        
        if added:
            print(f"\ncalc is ready to use!")

    if args.expression:
        expr = " ".join(args.expression)
        print(f"\nRunning: calc {expr}")
        result = subprocess.run([calc_path, expr])
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
