import subprocess
import yaml
import glob
import os
import json
from datetime import datetime

# Load configuration from YAML
with open("config.yaml", "r", encoding="utf8") as file:
    config = yaml.safe_load(file)

def load_order_mapping():
    """Load the order mapping created by Auto_test_gen.py"""
    mapping_file = os.path.join("generated-scripts", "order_mapping.json")
    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r') as f:
                order_mapping = json.load(f)
            print(f"Loaded order mapping with {len(order_mapping)} entries")
            return order_mapping
        except Exception as e:
            print(f"Error loading order mapping: {e}")
            return None
    else:
        print("Order mapping file not found, falling back to alphabetical order")
        return None


def get_all_script_files():
    """Gets all Python files in the scripts directory using order mapping."""

    # **NEW: Try to use order mapping first**
    order_mapping = load_order_mapping()

    if order_mapping:
        # Use the explicit order from mapping
        ordered_files = []
        for item in sorted(order_mapping, key=lambda x: x['order_index']):
            script_path = f"generated-scripts/{item['script_name']}"
            if os.path.exists(script_path):
                ordered_files.append(script_path)
                print(f"  {item['order_index']}. {script_path} (from {item['source_file']})")
            else:
                print(f"WARNING: Mapped script not found: {script_path}")

        if ordered_files:
            print(f"Found {len(ordered_files)} script files (using order mapping):")
            return ordered_files

    # **FALLBACK: Use alphabetical if no mapping available**
    files = glob.glob("generated-scripts/*.py")
    if not files:
        print("No Python files found in generated-scripts directory.")
        return []

    # Exclude the mapping file itself
    files = [f for f in files if not f.endswith("order_mapping.json")]
    files.sort()  # Alphabetical fallback

    print(f"Found {len(files)} script files (alphabetical fallback):")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    return files


def run_command_to_file(command, output_file):
    """Executes a command and writes output to file."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")
    with open(output_file, "w", encoding="utf8") as file:
        file.write(result.stdout)
        if result.stderr:
            file.write(f"{result.stderr}\n")
    return result

'''
def run_tool_on_single_file(tool_name, file_path, options, file_index=None):
    """Run a specific tool on a single file and return result"""

    # Special handling for Bandit to avoid overwriting HTML files
    if tool_name == "bandit":
        # For individual files, use unique HTML output files
        if file_index is not None:
            individual_html_file = f"reports/bandit_output_{file_index}.html"
            # Modify options to output to individual file
            modified_options = options.replace("reports/bandit_output.html", individual_html_file)
        else:
            # Fallback for when no index provided
            individual_html_file = f"reports/bandit_temp_{os.path.basename(file_path)}.html"
            modified_options = options.replace("reports/bandit_output.html", individual_html_file)

        # Run bandit with modified output file
        command = f"{tool_name} {file_path} {modified_options}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")

        # Read the generated HTML file for stdout content
        html_content = ""
        if os.path.exists(individual_html_file):
            try:
                with open(individual_html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
            except Exception as e:
                html_content = f"Error reading HTML file: {e}"

        return {
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'stdout': html_content,  # HTML content for display
            'stderr': result.stderr,
            'html_file': individual_html_file  # Track the HTML file location
        }
    else:
        # Standard handling for other tools
        command = f"{tool_name} {file_path} {options}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")
        return {
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
'''

def run_tool_on_single_file(tool_name, file_path, options, file_index=None):
    """Run a specific tool on a single file and return result"""
    # Special handling for Bandit to avoid overwriting HTML files
    if tool_name == "bandit":
        # For individual files, use unique HTML output files
        if file_index is not None:
            individual_html_file = f"reports/bandit_output_{file_index}.html"
            # Modify options to output to individual file
            modified_options = options.replace("reports/bandit_output.html", individual_html_file)
        else:
            # Fallback for when no index provided
            individual_html_file = f"reports/bandit_temp_{os.path.basename(file_path)}.html"
            modified_options = options.replace("reports/bandit_output.html", individual_html_file)

        # Run bandit with modified output file
        command = f"{tool_name} {file_path} {modified_options}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")

        # Read the generated HTML file for stdout content
        html_content = ""
        if os.path.exists(individual_html_file):
            try:
                with open(individual_html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
            except Exception as e:
                html_content = f"Error reading HTML file: {e}"

        return {
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'stdout': html_content,  # HTML content for display
            'stderr': result.stderr,
            'html_file': individual_html_file  # Track the HTML file location
        }
    # Special handling for flake8 with --output-file
    elif tool_name == "flake8" and "--output-file=" in options:
        # For individual files, use unique output files
        if file_index is not None:
            individual_output_file = f"reports/flake8_output_{file_index}.txt"
            # Modify options to output to individual file
            modified_options = options.replace("reports/flake8_output.txt", individual_output_file)
        else:
            # Fallback for when no index provided
            individual_output_file = f"reports/flake8_temp_{os.path.basename(file_path)}.txt"
            modified_options = options.replace("reports/flake8_output.txt", individual_output_file)

        # Run flake8 with modified output file
        command = f"{tool_name} {file_path} {modified_options}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")

        # Read the generated output file for stdout content
        output_content = ""
        if os.path.exists(individual_output_file):
            try:
                with open(individual_output_file, "r", encoding="utf-8") as f:
                    output_content = f.read()
            except Exception as e:
                output_content = f"Error reading output file: {e}"

        # If file is empty, flake8 found no issues
        if not output_content.strip():
            output_content = "No issues found by flake8."

        return {
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'stdout': output_content,  # File content for display
            'stderr': result.stderr,
            'output_file': individual_output_file  # Track the output file location
        }
    else:
        # Standard handling for other tools
        command = f"{tool_name} {file_path} {options}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")
        return {
            'returncode': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

def create_reports_folder():
    """Creates the reports folder if it does not exist."""
    if not os.path.exists("reports"):
        os.makedirs("reports")
        print("Created reports folder.")
    else:
        print("Reports folder already exists.")


def delete_old_summaries():
    reports_folder = "reports/"
    if os.path.exists(reports_folder):
        files_removed = 0
        for filename in os.listdir(reports_folder):
            file_path = os.path.join(reports_folder, filename)
            try:
                if filename.startswith("summary") or filename.endswith("_output.txt") or filename.endswith(
                        "_output.html"):
                    os.remove(file_path)
                    files_removed += 1
                    print(f"Removed file: {file_path}")
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
        print(f"Cleanup completed: {files_removed} old files removed")
    else:
        print(f"Reports folder '{reports_folder}' does not exist.")


def write_combined_summary(all_results, analyzed_files):
    """Write the main summary.txt with combined results"""
    with open("reports/summary.txt", "w", encoding="utf8") as f:
        f.write("CODE REVIEW SUMMARY\n")
        f.write("=" * 20 + "\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Files analyzed: {len(analyzed_files)}\n")

        for file in analyzed_files:
            f.write(f"  - {file}\n")
        f.write("\n")

        # Calculate overall status for each tool
        tools = ['black - Code Formatting', 'flake8 - Style & Lint Checks',
                 'bandit - Security Analysis', 'pylint - Static Code Analysis']

        for tool in tools:
            # Check if ANY file has issues for this tool
            any_issues = any(not all_results[file][tool]['success'] for file in analyzed_files)
            overall_return_code = max(all_results[file][tool]['returncode'] for file in analyzed_files)

            # ADD ICONS HERE - DETERMINE ICON BASED ON ISSUES AND TOOL TYPE
            if not any_issues:
                icon = "✅"
            elif 'pylint' in tool.lower():
                icon = "❌"  # Red cross for pylint issues
            else:
                icon = "⚠️"  # Amber warning for other tools

            f.write(f"{tool.upper()}: {icon}\n")
            f.write(f"  Return Code: {overall_return_code}\n")
            f.write(f"  Status: {'Issues Found' if any_issues else 'Success'}\n")
            f.write("\n")


def write_individual_summaries(all_results, analyzed_files):
    """Write individual summary files for each analyzed file"""
    for i, file_path in enumerate(analyzed_files, 1):
        with open(f"reports/summary{i}.txt", "w", encoding="utf8") as f:
            f.write("CODE REVIEW SUMMARY\n")
            f.write("=" * 20 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"File analyzed: {file_path}\n\n")

            file_results = all_results[file_path]

            for tool_name, result in file_results.items():
                # Determine icon based on individual file result
                if result['success']:
                    icon = "✅"
                elif 'pylint' in tool_name.lower():
                    icon = "❌"  # Red cross for pylint issues
                else:
                    icon = "⚠️"  # Amber warning for other tools

                f.write(f"{tool_name.upper()}: {icon}\n")
                f.write(f"  Return Code: {result['returncode']}\n")
                f.write(f"  Status: {'Success' if result['success'] else 'Issues Found'}\n")
                f.write("\n")


def write_individual_tool_outputs(all_results, analyzed_files):
    """Write individual tool output files for each test case"""
    tools_config = {
        'black': 'black - Code Formatting',
        'flake8': 'flake8 - Style & Lint Checks',
        'bandit': 'bandit - Security Analysis',
        'pylint': 'pylint - Static Code Analysis'
    }

    for i, file_path in enumerate(analyzed_files, 1):
        file_results = all_results[file_path]

        for tool_command, tool_display_name in tools_config.items():
            result = file_results[tool_display_name]

            # For bandit, use .html extension, for others use .txt
            if tool_command == 'bandit':
                extension = '.html'
            else:
                extension = '.txt'

            # Write individual tool output
            output_file = f"reports/{tool_command}_output_{i}{extension}"
            with open(output_file, "w", encoding="utf8") as f:
                f.write(result['stdout'])
                if result['stderr']:
                    f.write(f"\nSTDERR:\n{result['stderr']}")

            print(f"Created individual output: {output_file}")


def write_combined_tool_outputs(all_results, analyzed_files):
    """Write combined tool output files for collective analysis"""
    tools_config = {
        'black': 'black - Code Formatting',
        'flake8': 'flake8 - Style & Lint Checks',
        'bandit': 'bandit - Security Analysis',
        'pylint': 'pylint - Static Code Analysis'
    }

    for tool_command, tool_display_name in tools_config.items():
        # For bandit use .html, for others use .txt
        if tool_command == 'bandit':
            extension = '.html'
        else:
            extension = '.txt'

        # Write combined tool output
        output_file = f"reports/{tool_command}_output{extension}"
        with open(output_file, "w", encoding="utf8") as f:
            for i, file_path in enumerate(analyzed_files, 1):
                if i > 1:  # Add separator between files
                    if tool_command == 'bandit':
                        f.write(f"\n\n<!-- === {file_path} === -->\n")
                    else:
                        f.write(f"\n\n=== {file_path} ===\n")

                result = all_results[file_path][tool_display_name]
                f.write(result['stdout'])
                if result['stderr']:
                    if tool_command == 'bandit':
                        f.write(f"\n<!-- STDERR: {result['stderr']} -->\n")
                    else:
                        f.write(f"\nSTDERR:\n{result['stderr']}")

        print(f"Created combined output: {output_file}")


# ADD THIS NEW FUNCTION TO SAVE RETURN CODES FOR COMPATIBILITY
def save_return_codes_for_compatibility(all_results, analyzed_files):
    """Save return codes in individual files for get_return_code() function compatibility"""
    tools_mapping = {
        'black - Code Formatting': 'black',
        'flake8 - Style & Lint Checks': 'flake8',
        'bandit - Security Analysis': 'bandit',
        'pylint - Static Code Analysis': 'pylint'
    }

    # Calculate overall return codes (max across all files)
    overall_return_codes = {}
    for tool_display_name, tool_command in tools_mapping.items():
        max_return_code = max(all_results[file][tool_display_name]['returncode'] for file in analyzed_files)
        overall_return_codes[tool_command] = max_return_code

    # Save overall return codes to files
    for tool_command, return_code in overall_return_codes.items():
        with open(f"reports/{tool_command}_return_code.txt", "w") as f:
            f.write(str(return_code))
        print(f"Saved return code for {tool_command}: {return_code}")


# Main execution
create_reports_folder()

# Get all script files to analyze
all_files = get_all_script_files()
if not all_files:
    print("No files to analyze. Exiting.")
    exit(1)

print(f"Analyzing {len(all_files)} files individually...")

# Store results for each file
all_results = {}

# Tool configurations
tools_config = {
    'black - Code Formatting': ('black', config["linting"]["black"]),
    'flake8 - Style & Lint Checks': ('flake8', config["linting"]["flake8"]),
    'bandit - Security Analysis': ('bandit', config["security"]["bandit"]),
    'pylint - Static Code Analysis': ('pylint', config["linting"]["pylint"])
}

# Clean up old files first
delete_old_summaries()

# Analyze each file individually
for i, file_path in enumerate(all_files, 1):
    print(f"\nAnalyzing: {file_path}")
    all_results[file_path] = {}

    for tool_display_name, (tool_command, tool_options) in tools_config.items():
        print(f"  Running {tool_command}...")
        # Pass file index for bandit individual file handling
        result = run_tool_on_single_file(tool_command, file_path, tool_options, file_index=i)
        all_results[file_path][tool_display_name] = result

# Write all output files
print(f"\nGenerating output files...")

# Write summary files
write_combined_summary(all_results, all_files)
write_individual_summaries(all_results, all_files)

# Write individual tool outputs
write_individual_tool_outputs(all_results, all_files)

# Write combined tool outputs
write_combined_tool_outputs(all_results, all_files)

# ADD THIS LINE: Save return codes for compatibility with get_return_code() function
save_return_codes_for_compatibility(all_results, all_files)

print("\nCode analysis completed successfully!")
print(f"Reports generated in 'reports/' directory")
print(f"Main summary available in 'reports/summary.txt'")
print(f"Individual summaries: summary1.txt, summary2.txt, etc.")
print(f"Individual tool outputs: flake8_output_1.txt, bandit_output_1.txt, etc.")
print(f"Combined tool outputs: flake8_output.txt, bandit_output.txt, etc.")

# Print quick results overview
print(f"\nQuick Results Overview:")
for i, file_path in enumerate(all_files, 1):
    file_results = all_results[file_path]
    issues = sum(1 for result in file_results.values() if not result['success'])
    print(f"  summary{i}.txt ({file_path}): {4 - issues}/4 tools passed, {issues} issues found")