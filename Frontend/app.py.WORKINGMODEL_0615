import paramiko
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import json
import sys
import subprocess
import re
import time
import glob
import threading
from datetime import datetime
import signal
import atexit

# Initialize Flask with explicit static folder configuration
app = Flask(__name__,
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
else:
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'dev-secret-key'

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), '..', 'test_case')
app.config['GENERATED_SCRIPTS_FOLDER'] = os.path.join(os.getcwd(), '..', 'generated-scripts')
app.config['REPORT_FOLDER'] = os.path.join(os.getcwd(), '..', 'reports')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

generation_lock = threading.Lock()

# Updated allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'rtf', 'md', 'log', 'pdf', 'doc', 'docx', 'odt', 'pages',
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================================================================================================
# PROGRESS FILES CLEANUP FUNCTIONS
# ================================================================================================
def progress_cleanup():
    """Simple cleanup - just remove progress files"""
    try:
        progress_files = ['progress_generate.json', 'progress_review.json', 'progress_execute.json']
        for file in progress_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"[CLEANUP] Removed {file}")
    except Exception as e:
        print(f"[CLEANUP] Error: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n[SHUTDOWN] Ctrl+C pressed - cleaning up...")
    progress_cleanup()
    print("[SHUTDOWN] Cleanup complete")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# ================================================================================================
# PROGRESS TRACKING FUNCTIONS
# ================================================================================================

def update_progress(task_type, progress, status, step, completed=False):
    """Update progress file for real-time tracking"""
    try:
        progress_data = {
            'progress': progress,
            'status': status,
            'step': step,
            'completed': completed,
            'timestamp': time.time()
        }
        progress_file = f"progress_{task_type}.json"
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
        print(f"[PROGRESS] {task_type}: {progress}% - {step}")
    except Exception as e:
        print(f"Error updating progress: {e}")


def clear_progress(task_type):
    """Clear progress file when starting new task"""
    try:
        progress_file = f"progress_{task_type}.json"
        if os.path.exists(progress_file):
            os.remove(progress_file)
    except Exception as e:
        print(f"Error clearing progress: {e}")


@app.route('/progress/<task_type>', methods=['GET'])
def get_progress(task_type):
    """Get real-time progress for generate/review/execute tasks"""
    try:
        progress_file = f"progress_{task_type}.json"
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            return jsonify(progress_data)
        else:
            return jsonify({
                'progress': 0,
                'status': 'Not started',
                'step': 'Initializing...',
                'completed': False
            })
    except Exception as e:
        return jsonify({
            'progress': 0,
            'status': f'Error: {str(e)}',
            'step': 'Error occurred',
            'completed': False
        })


# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


# Global variables to store uploaded files and generated scripts info
uploaded_files_global = []
generated_scripts_info = []


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    global uploaded_files_global

    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files selected'})

        files = request.files.getlist('files')
        uploaded_files = []
        total_size = 0

        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                #timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3] + '_'  # Include milliseconds
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                file_size = os.path.getsize(file_path)
                total_size += file_size

                uploaded_files.append({
                    'name': file.filename,
                    'size': file_size,
                    'path': filename
                })
            else:
                print(f"File not allowed: {file.filename}")

        # Store uploaded files globally
        uploaded_files_global = uploaded_files

        if uploaded_files:
            return jsonify({
                'success': True,
                'files': uploaded_files,
                'total_size': total_size,
                'message': f'Successfully uploaded {len(uploaded_files)} file(s)'
            })
        else:
            return jsonify({'success': False, 'message': 'No valid files uploaded. Please check file types.'})

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'message': f'Upload error: {str(e)}'})


@app.route('/ingest', methods=['POST'])
def ingest_test():
    """Process ingested test files and identify individual test cases"""
    try:
        data = request.get_json()
        files = data.get('files', [])

        # Process each uploaded file and identify test cases
        processed_files = []
        for i, file_info in enumerate(files):
            # Simulate analyzing file content to determine number of test cases
            # In reality, you might parse the file content here
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['path'])

            # For demonstration, assume each file contains 1 test case
            # You can enhance this to actually parse the file content
            test_case_name = file_info['name'].replace('.txt', '').replace('.docx', '').replace('.pdf', '')

            processed_files.append({
                'id': i + 1,
                'name': test_case_name,
                'original_filename': file_info['name'],
                'status': 'processed',
                'test_cases': f"1 test case identified",
                'file_path': file_path
            })

        return jsonify({
            'success': True,
            'processed_files': processed_files,
            'total_test_cases': len(processed_files),
            'message': f'Test ingestion completed successfully. Found {len(processed_files)} test case(s)'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Ingestion error: {str(e)}'})


def simulate_progress_during_subprocess(task_type, start_progress, end_progress, duration=8):
    """Simulate progress increment during subprocess execution"""
    steps = 4  # 65%, 70%, 75%, 80%
    step_size = (end_progress - start_progress) / steps
    sleep_time = duration / steps

    current_progress = start_progress
    status_messages = [
        "Analyzing test requirements...",
        "Generating Python test code...",
        "Optimizing code structure...",
        "Finalizing test scripts..."
    ]

    for i in range(steps):
        time.sleep(sleep_time)
        current_progress += step_size
        update_progress(task_type, int(current_progress), 'Processing', status_messages[i])


'''@app.route('/generate', methods=['POST'])
def generate_code():
    """Generate Python test code for all test cases with real progress tracking"""
    global uploaded_files_global
    global generated_scripts_info

    try:
        data = request.get_json()
        print(f"Generate request data: {data}")

        # Clear previous progress and initialize
        clear_progress('generate')
        update_progress('generate', 0, 'Starting', 'Analyzing test requirements')

        # Clear old scripts
        folder_path = app.config['GENERATED_SCRIPTS_FOLDER']
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"[INFO] Deleted old script: {file_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to delete {file_path}: {e}")
            try:
                os.rmdir(folder_path)
                print(f"[INFO] Deleted folder: {folder_path}")
            except:
                pass
        else:
            print(f"[INFO] Folder '{folder_path}' does not exist. Skipping cleanup.")

        # Step 1: Preparation (20%)
        update_progress('generate', 20, 'Processing', 'Creating Python test structure')
        time.sleep(1)  # Allow progress to be visible

        # Step 2: Script generation (40%)
        update_progress('generate', 40, 'Processing', 'Generating Python test code')

        # Run Auto_test_gen.py to generate scripts
        print(f"Executing Auto_test_gen.py")
        script_path = os.path.join(os.getcwd(), "..", "Backend", "Auto_test_gen.py")
        print(f"DEBUG: App.py current directory: {os.getcwd()}")
        print(f"DEBUG: Looking for Auto_test_gen.py at: {script_path}")
        print(f"DEBUG: Auto_test_gen.py exists: {os.path.exists(script_path)}")

        # Step 3: Executing script generation (60%)
        update_progress('generate', 60, 'Processing', 'Optimizing Python code')

        # START OF ENHANCED SUBPROCESS HANDLING
        print(f"Starting subprocess with progress simulation...")

        # Start progress simulation in a separate thread
        progress_thread = threading.Thread(
            target=simulate_progress_during_subprocess,
            args=('generate', 65, 80, 8)  # Go from 65% to 80% over 8 seconds
        )
        progress_thread.start()

        # Run the actual subprocess
        output = subprocess.run(["python3", os.path.join(os.getcwd(), "..", "Backend", "Auto_test_gen.py")],
                                capture_output=True, text=True)

        # Wait for progress thread to complete
        progress_thread.join()

        # END OF ENHANCED SUBPROCESS HANDLING

        print(f"Auto_test_gen.py completed")
        print(f"DEBUG: Subprocess return code: {output.returncode}")
        print(f"DEBUG: Subprocess stderr: '{output.stderr}'")
        print("STDOUT:", output.stdout)

        # Step 4: Processing results (80% → 90%)
        update_progress('generate', 80, 'Processing', 'Processing generated scripts')
        time.sleep(0.8)  # Small delay

        # Continue smooth progress during script processing
        update_progress('generate', 85, 'Processing', 'Reading script files')
        time.sleep(0.6)

        # Extract all generated script names
        matches = re.findall(r"Script generated\s*:\s*(\S+\.py)", output.stdout)

        if not matches:
            update_progress('generate', 0, 'Error', 'No scripts were generated', True)
            return jsonify({'success': False, 'message': 'No scripts were generated.'})

        # Continue progress during file reading
        update_progress('generate', 90, 'Processing', 'Organizing test cases')
        time.sleep(0.7)

        # Read all generated scripts
        generated_scripts_info = []
        script_folder = app.config['GENERATED_SCRIPTS_FOLDER']
        print(f"DEBUG: App looking for scripts in: {script_folder}")
        print(f"DEBUG: Generated scripts folder exists: {os.path.exists(script_folder)}")

        # Update progress while processing each script
        total_scripts = len(matches)
        for i, script_name in enumerate(matches):
            # Show incremental progress from 90% to 95%
            if total_scripts > 1:
                script_progress = 90 + (i * 5 // total_scripts)
                update_progress('generate', script_progress, 'Processing', f'Processing script {i + 1}/{total_scripts}')
                time.sleep(0.3)

            file_path = os.path.join(script_folder, script_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()

                    # Extract test case name from script name
                    test_case_name = script_name.replace('.py', '').replace('_', ' ').title()

                    generated_scripts_info.append({
                        'id': i + 1,
                        'script_name': script_name,
                        'test_case_name': test_case_name,
                        'file_path': file_path,
                        'code': f'# Generated Python Test Code - {script_name}\n# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n{script_content}'
                    })
                except Exception as e:
                    generated_scripts_info.append({
                        'id': i + 1,
                        'script_name': script_name,
                        'test_case_name': script_name.replace('.py', ''),
                        'file_path': file_path,
                        'code': f"Error reading file {script_name}: {str(e)}"
                    })
            else:
                generated_scripts_info.append({
                    'id': i + 1,
                    'script_name': script_name,
                    'test_case_name': script_name.replace('.py', ''),
                    'file_path': '',
                    'code': f"Script {script_name} was listed but not found on disk."
                })

        # Final progress steps (95% → 100%)
        update_progress('generate', 95, 'Processing', 'Finalizing test suite')
        time.sleep(0.8)

        update_progress('generate', 98, 'Processing', 'Preparing response')
        time.sleep(0.5)

        # Step 5: Complete (100%)
        update_progress('generate', 100, 'Completed', 'Code generation completed successfully!', True)

        return jsonify({
            'success': True,
            'generated_scripts': generated_scripts_info,
            'total_scripts': len(generated_scripts_info),
            'message': f'Successfully generated {len(generated_scripts_info)} Python test script(s)'
        })

    except Exception as e:
        update_progress('generate', 0, 'Error', f'Generation failed: {str(e)}', True)
        return jsonify({'success': False, 'message': f'Generation error: {str(e)}'})
'''

@app.route('/generate', methods=['POST'])
def generate_code():
    """Generate Python test code for all test cases with real progress tracking"""
    global uploaded_files_global
    global generated_scripts_info
    global generation_lock

    # CLEANUP: Remove progress file if exists from previous run
    try:
        if os.path.exists('progress_generate.json'):
            os.remove('progress_generate.json')
            print("[CLEANUP] Removed progress_generate.json after successful generation")
    except Exception as e:
        print(f"[CLEANUP] Error removing progress_generate.json: {e}")

    # Use lock to prevent multiple simultaneous generations
    with generation_lock:
        try:
            data = request.get_json()
            print(f"Generate request data: {data}")

            # Check if generation is already in progress by checking existing progress
            progress_file = "progress_generate.json"
            is_already_running = False

            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r') as f:
                        existing_progress = json.load(f)
                    # If progress exists and not completed, don't start new generation
                    if not existing_progress.get('completed', False) and existing_progress.get('progress', 0) > 0:
                        is_already_running = True
                        print(f"[INFO] Generation already in progress at {existing_progress.get('progress', 0)}%")
                except:
                    pass

            # Only clear progress if not already running
            if not is_already_running:
                clear_progress('generate')
                update_progress('generate', 0, 'Starting', 'Analyzing test requirements')

                # Clear old scripts (only if starting fresh)
                folder_path = app.config['GENERATED_SCRIPTS_FOLDER']
                if os.path.isdir(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                print(f"[INFO] Deleted old script: {file_path}")
                        except Exception as e:
                            print(f"[ERROR] Failed to delete {file_path}: {e}")
                    try:
                        os.rmdir(folder_path)
                        print(f"[INFO] Deleted folder: {folder_path}")
                    except:
                        pass
                else:
                    print(f"[INFO] Folder '{folder_path}' does not exist. Skipping cleanup.")

                # Step 1: Preparation (20%)
                update_progress('generate', 20, 'Processing', 'Creating Python test structure')
                time.sleep(1)  # Allow progress to be visible

                # Step 2: Script generation (40%)
                update_progress('generate', 40, 'Processing', 'Generating Python test code')

                # Run Auto_test_gen.py to generate scripts
                print(f"Executing Auto_test_gen.py")
                script_path = os.path.join(os.getcwd(), "..", "Backend", "Auto_test_gen.py")
                print(f"DEBUG: App.py current directory: {os.getcwd()}")
                print(f"DEBUG: Looking for Auto_test_gen.py at: {script_path}")
                print(f"DEBUG: Auto_test_gen.py exists: {os.path.exists(script_path)}")

                # Step 3: Executing script generation (60%)
                update_progress('generate', 60, 'Processing', 'Optimizing Python code')

                # START OF ENHANCED SUBPROCESS HANDLING
                print(f"Starting subprocess with progress simulation...")

                # Start progress simulation in a separate thread
                progress_thread = threading.Thread(
                    target=simulate_progress_during_subprocess,
                    args=('generate', 65, 80, 8)  # Go from 65% to 80% over 8 seconds
                )
                progress_thread.start()

                # Run the actual subprocess
                output = subprocess.run(["python3", os.path.join(os.getcwd(), "..", "Backend", "Auto_test_gen.py")],
                                        capture_output=True, text=True)

                # Wait for progress thread to complete
                progress_thread.join()

                # END OF ENHANCED SUBPROCESS HANDLING

                print(f"Auto_test_gen.py completed")
                print(f"DEBUG: Subprocess return code: {output.returncode}")
                print(f"DEBUG: Subprocess stderr: '{output.stderr}'")
                print("STDOUT:", output.stdout)

                # Step 4: Processing results (80% → 90%)
                update_progress('generate', 80, 'Processing', 'Processing generated scripts')
                time.sleep(0.8)  # Small delay

                # Continue smooth progress during script processing
                update_progress('generate', 85, 'Processing', 'Reading script files')
                time.sleep(0.6)

                # Extract all generated script names
                matches = re.findall(r"Script generated\s*:\s*(\S+\.py)", output.stdout)

                if not matches:
                    update_progress('generate', 0, 'Error', 'No scripts were generated', True)
                    return jsonify({'success': False, 'message': 'No scripts were generated.'})

                # Continue progress during file reading
                update_progress('generate', 90, 'Processing', 'Organizing test cases')
                time.sleep(0.7)

                # Read all generated scripts
                generated_scripts_info = []
                script_folder = app.config['GENERATED_SCRIPTS_FOLDER']
                print(f"DEBUG: App looking for scripts in: {script_folder}")
                print(f"DEBUG: Generated scripts folder exists: {os.path.exists(script_folder)}")

                # Update progress while processing each script
                total_scripts = len(matches)
                for i, script_name in enumerate(matches):
                    # Show incremental progress from 90% to 95%
                    if total_scripts > 1:
                        script_progress = 90 + (i * 5 // total_scripts)
                        update_progress('generate', script_progress, 'Processing',
                                        f'Processing script {i + 1}/{total_scripts}')
                        time.sleep(0.3)

                    file_path = os.path.join(script_folder, script_name)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                script_content = f.read()

                            # Extract test case name from script name
                            test_case_name = script_name.replace('.py', '').replace('_', ' ').title()

                            generated_scripts_info.append({
                                'id': i + 1,
                                'script_name': script_name,
                                'test_case_name': test_case_name,
                                'file_path': file_path,
                                'code': f'# Generated Python Test Code - {script_name}\n# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n{script_content}'
                            })
                        except Exception as e:
                            generated_scripts_info.append({
                                'id': i + 1,
                                'script_name': script_name,
                                'test_case_name': script_name.replace('.py', ''),
                                'file_path': file_path,
                                'code': f"Error reading file {script_name}: {str(e)}"
                            })
                    else:
                        generated_scripts_info.append({
                            'id': i + 1,
                            'script_name': script_name,
                            'test_case_name': script_name.replace('.py', ''),
                            'file_path': '',
                            'code': f"Script {script_name} was listed but not found on disk."
                        })

                # Final progress steps (95% → 100%)
                update_progress('generate', 95, 'Processing', 'Finalizing test suite')
                time.sleep(0.8)

                update_progress('generate', 98, 'Processing', 'Preparing response')
                time.sleep(0.8)

                # Step 5: Complete (100%)
                update_progress('generate', 100, 'Completed', 'Code generation completed successfully!', True)

            else:
                # If already running, return the current state
                print(f"[INFO] Generation already in progress, returning current state")
                # Return existing generated scripts if available
                if generated_scripts_info:
                    return jsonify({
                        'success': True,
                        'generated_scripts': generated_scripts_info,
                        'total_scripts': len(generated_scripts_info),
                        'message': f'Generation already completed - {len(generated_scripts_info)} script(s) available'
                    })

            return jsonify({
                'success': True,
                'generated_scripts': generated_scripts_info,
                'total_scripts': len(generated_scripts_info),
                'message': f'Successfully generated {len(generated_scripts_info)} Python test script(s)'
            })

        except Exception as e:
            update_progress('generate', 0, 'Error', f'Generation failed: {str(e)}', True)
            return jsonify({'success': False, 'message': f'Generation error: {str(e)}'})

@app.route('/save_code', methods=['POST'])
def save_code():
    """Save generated code to file system"""
    global generated_scripts_info

    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        test_case_id = data.get('test_case_id', None)
        test_case_name = data.get('test_case_name', 'general')

        if not code:
            return jsonify({'success': False, 'message': 'No code to save!'})
        print(f"test_case_id - {test_case_id} generated_scripts_info - {generated_scripts_info}")
        if test_case_id is not None and test_case_id <= len(generated_scripts_info):
            # Multi-test case mode - save specific script
            script_info = generated_scripts_info[test_case_id - 1]
            filepath = script_info['file_path']
            filename = script_info['script_name']
        else:
            # Single test case mode or fallback
            script_dir = app.config['GENERATED_SCRIPTS_FOLDER']
            os.makedirs(script_dir, exist_ok=True)
            script_info = generated_scripts_info[0]
            filepath = script_info['file_path']
            filename = script_info['script_name']

        # Write the code to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        return jsonify({
            'success': True,
            'message': f'Python code saved as {filename}',
            'filename': filename,
            'filepath': filepath
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving file: {str(e)}'})


def remove_ansi_codes(text):
    """Function to strip ANSI escape codes (color codes) from terminal output"""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


@app.route('/execute', methods=['POST'])
def execute_code():
    """Execute all generated test scripts on remote RPI via SSH with real progress tracking"""
    global generated_scripts_info

    # Clean up progress file if exists from previous Run
    try:
        if os.path.exists('progress_execute.json'):
            os.remove('progress_execute.json')
            print("[CLEANUP] Removed progress_execute.json after completion")
    except Exception as e:
        print(f"[CLEANUP] Error removing progress_execute.json: {e}")

    try:
        data = request.get_json()
        test_case_id = data.get('test_case_id', None)

        # Clear previous progress and initialize
        clear_progress('execute')
        update_progress('execute', 0, 'Starting', 'Preparing Python execution environment')

        # Step 1: Preparation (20%)
        update_progress('execute', 20, 'Processing', 'Connecting to test infrastructure')

        # RPI connection details
        rpi_list = [
            {"host": "71.185.253.158", "user": "root", "pass": ""},
            {"host": "65.78.96.246", "user": "root", "pass": ""}
        ]

        MAX_RETRIES = 3
        RETRY_DELAY = 3
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected = False
        connected_host = None

        # Try to connect to any available RPI
        for attempt in range(MAX_RETRIES):
            print(f"[INFO] Connection attempt {attempt + 1}")
            for rpi in rpi_list:
                try:
                    print(f"[INFO] Connecting to {rpi['host']}...")
                    ssh.connect(rpi["host"], username=rpi["user"], password=rpi["pass"], timeout=5)
                    connected = True
                    connected_host = rpi["host"]
                    print(f"[INFO] Connected to {rpi['host']}")
                    break
                except Exception as e:
                    print(f"[ERROR] Connection to {rpi['host']} failed: {e}")
            if connected:
                break
            time.sleep(RETRY_DELAY)

        if not connected:
            update_progress('execute', 0, 'Error', 'Failed to connect to any Raspberry Pi', True)
            return jsonify({'success': False, 'message': 'Failed to connect to the Remote Test Device.'})

        # Step 2: Connection established (40%)
        update_progress('execute', 40, 'Processing', 'Running reviewed Python test cases')

        execution_results = []

        if test_case_id is not None:
            # Execute specific test case
            if test_case_id <= len(generated_scripts_info):
                script_info = generated_scripts_info[test_case_id - 1]
                result = execute_single_script(ssh, script_info)
                execution_results.append(result)
            else:
                ssh.close()
                update_progress('execute', 0, 'Error', f'Test case {test_case_id} not found', True)
                return jsonify({'success': False, 'message': f'Test case {test_case_id} not found.'})
        else:
            # Execute all test cases
            script_folder = app.config['GENERATED_SCRIPTS_FOLDER']
            if not os.path.isdir(script_folder):
                ssh.close()
                update_progress('execute', 0, 'Error', 'Generated scripts folder does not exist', True)
                return jsonify({'success': False, 'message': 'Generated scripts folder does not exist.'})

            # Step 3: Executing scripts (60%)
            update_progress('execute', 60, 'Processing', 'Collecting test results')

            # Execute each generated script
            total_scripts = len(generated_scripts_info)
            for i, script_info in enumerate(generated_scripts_info):
                if os.path.isfile(script_info['file_path']):
                    result = execute_single_script(ssh, script_info)
                    execution_results.append(result)

                    # Update progress based on script execution
                    progress = 60 + (i + 1) * 20 // total_scripts
                    update_progress('execute', progress, 'Processing', f'Executed {i + 1}/{total_scripts} scripts')

        # Step 4: Collecting results (80%)
        update_progress('execute', 80, 'Processing', 'Generating execution output')
        time.sleep(1)  # Allow progress to be visible

        ssh.close()

        # Step 5: Complete (100%)
        update_progress('execute', 100, 'Completed', 'Execution completed successfully!', True)

        return jsonify({
            'success': True,
            'connected_host': connected_host,
            'execution_results': execution_results,
            'total_executed': len(execution_results),
            'message': f'Successfully executed {len(execution_results)} test script(s)'
        })

    except Exception as e:
        update_progress('execute', 0, 'Error', f'Execution failed: {str(e)}', True)
        return jsonify({'success': False, 'message': f'Execution error: {str(e)}'})


def execute_single_script(ssh, script_info):
    """Execute a single script on the remote RPI"""
    try:
        with open(script_info['file_path'], 'r') as f:
            script_content = f.read()

        remote_path = f"/tmp/{script_info['script_name']}"
        print(f"[INFO] Uploading {script_info['script_name']} to {remote_path}")

        # Upload script content via echo command
        escaped_script = script_content.replace("'", "'\"'\"'")
        command = f"echo '{escaped_script}' > {remote_path} && chmod +x {remote_path}"
        ssh.exec_command(command)

        # Execute the script
        print(f"[INFO] Executing {script_info['script_name']}")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        execution_output = stdout.read().decode()
        error_output = stderr.read().decode()

        return {
            'test_case_id': script_info['id'],
            'script_name': script_info['script_name'],
            'test_case_name': script_info['test_case_name'],
            'stdout': remove_ansi_codes(execution_output),
            'stderr': remove_ansi_codes(error_output),
            'success': len(error_output.strip()) == 0
        }

    except Exception as e:
        return {
            'test_case_id': script_info['id'],
            'script_name': script_info['script_name'],
            'test_case_name': script_info['test_case_name'],
            'stdout': '',
            'stderr': f'Execution error: {str(e)}',
            'success': False
        }

@app.route('/review', methods=['POST'])
def review_code():
    """Review Python code quality for individual or all test cases with real progress tracking"""
    # Clean up progress files if exists
    try:
        if os.path.exists('progress_review.json'):
            os.remove('progress_review.json')
            print("[CLEANUP] Removed progress_review.json after completion")
    except Exception as e:
        print(f"[CLEANUP] Error removing progress_review.json: {e}")

    try:
        data = request.get_json()
        test_case_id = data.get('test_case_id', None)

        # Clear previous progress and initialize
        clear_progress('review')
        update_progress('review', 0, 'Starting', 'Scanning Python code structure')

        # Ensure reports directory exists
        reports_dir = os.path.join(os.getcwd(), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        # Step 2: Setup (33%)
        update_progress('review', 33, 'Processing', 'Checking Python best practices')

        # Get the full path to tox
        import shutil
        tox_path = shutil.which('tox')

        if not tox_path:
            tox_path = '/Users/gmajum163@cable.comcast.com/Library/Python/3.9/bin/tox'

        # Step 3: Running analysis (50%)
        update_progress('review', 50, 'Processing', 'Running security analysis')

        # Run tox for code quality analysis
        print(f"[INFO] Running tox from: {tox_path}")
        print(f"[INFO] Current working directory: {os.getcwd()}")

        # Set environment variables that might be needed
        env = os.environ.copy()
        env['PATH'] = f"/Users/gmajum163@cable.comcast.com/Library/Python/3.9/bin:{env.get('PATH', '')}"

        # Step 4: Executing tox (67%)
        update_progress('review', 67, 'Processing', 'Generating Python recommendations')

        run_tox = subprocess.run([tox_path], capture_output=True, text=True,
                                 cwd=os.getcwd(), env=env, timeout=300)

        print(f"[DEBUG] Tox return code: {run_tox.returncode}")
        print(f"[DEBUG] Tox stdout: {run_tox.stdout}")
        print(f"[DEBUG] Tox stderr: {run_tox.stderr}")

        # Step 5: Processing results (83%)
        update_progress('review', 83, 'Processing', 'Compiling final review report')

        # NEW: Handle individual test case reviews vs all test cases
        if test_case_id is not None:
            # Single test case review - read specific summary file
            summary_path = os.path.join(reports_dir, f'summary{test_case_id}.txt')
            summary_content = ""

            try:
                with open(summary_path, 'r') as f:
                    summary_content = f.read()
                print(f"[INFO] Found individual summary at: {summary_path}")
            except FileNotFoundError:
                # Fallback to main summary if individual not found
                main_summary_path = os.path.join(reports_dir, 'summary.txt')
                try:
                    with open(main_summary_path, 'r') as f:
                        summary_content = f.read()
                    print(f"[INFO] Used main summary as fallback: {main_summary_path}")
                except FileNotFoundError:
                    summary_content = f"""CODE REVIEW SUMMARY - TEST CASE {test_case_id}
====================
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANALYSIS STATUS:
- Tox return code: {run_tox.returncode}
- Individual summary file not found at: {summary_path}
- Main summary file not found either

TOX OUTPUT:
{run_tox.stdout}

TOX ERRORS:
{run_tox.stderr}
"""

            # Generate review for specific test case
            review_report = f"""=== INDIVIDUAL TEST CASE ANALYSIS ===
{summary_content}

=== ACTIONS REQUIRED ===
   ✅ 1. Look for [PASS] ✅ or [FAIL] ❌ indicators in the analysis above
   ✅ 2. CHECK "OPEN REPORT" FOR COMPREHENSIVE HTML RESULTS
   ✅ 3. CLICK THE **"EXECUTE CODE"** BUTTON IF NO CRITICAL ISSUES
   ❌ 4. DO NOT PROCEED IF STATIC CODE ANALYSIS FAILS OR SECURITY VULNERABILITIES ARE FOUND"""

            # Step 6: Complete (100%)
            update_progress('review', 100, 'Completed', 'Code review completed successfully!', True)

            return jsonify({
                'success': True,
                'review_report': review_report,
                'test_case_id': test_case_id,
                'message': f'Python code review completed successfully for Test Case {test_case_id}'
            })

        else:
            # Multiple test cases - return individual reports for each
            individual_reports = []

            # Read main summary for overall info
            main_summary_path = os.path.join(reports_dir, 'summary.txt')
            main_summary_content = ""
            try:
                with open(main_summary_path, 'r') as f:
                    main_summary_content = f.read()
            except FileNotFoundError:
                main_summary_content = "Main summary not available"

            # Generate individual reports for each generated script
            for i, script_info in enumerate(generated_scripts_info):
                test_case_id = script_info['id']
                individual_summary_path = os.path.join(reports_dir, f'summary{test_case_id}.txt')

                individual_summary_content = ""
                try:
                    with open(individual_summary_path, 'r') as f:
                        individual_summary_content = f.read()
                    print(f"[INFO] Found individual summary for Test Case {test_case_id}")
                except FileNotFoundError:
                    # Use main summary as fallback
                    individual_summary_content = main_summary_content
                    print(f"[INFO] Using main summary as fallback for Test Case {test_case_id}")

                individual_report = f"""=== INDIVIDUAL ANALYSIS ===
{individual_summary_content}

=== ACTIONS REQUIRED ===
   ✅ 1. Look for [PASS] ✅ or [FAIL] ❌ indicators in the analysis above
   ✅ 2. CHECK "OPEN REPORT" FOR COMPREHENSIVE HTML RESULTS
   ✅ 3. CLICK THE **"EXECUTE CODE"** BUTTON IF NO CRITICAL ISSUES
   ❌ 4. DO NOT PROCEED IF STATIC CODE ANALYSIS FAILS OR SECURITY VULNERABILITIES ARE FOUND"""

                individual_reports.append({
                    'test_case_id': test_case_id,
                    'script_name': script_info['script_name'],
                    'test_case_name': script_info['test_case_name'],
                    'review_report': individual_report
                })

            # Step 6: Complete (100%)
            update_progress('review', 100, 'Completed', 'Code review completed successfully!', True)

            return jsonify({
                'success': True,
                'individual_reports': individual_reports,
                'main_summary': main_summary_content,
                'total_scripts': len(individual_reports),
                'message': f'Python code review completed successfully for all {len(individual_reports)} test case(s)'
            })

    except subprocess.TimeoutExpired:
        update_progress('review', 0, 'Error', 'Code review timed out after 5 minutes', True)
        return jsonify({'success': False, 'message': 'Code review timed out after 5 minutes'})
    except Exception as e:
        update_progress('review', 0, 'Error', f'Review failed: {str(e)}', True)
        return jsonify({'success': False, 'message': f'Review error: {str(e)}'})


@app.route('/open-report')
def open_report():
    """Open the combined HTML report"""
    try:
        return send_from_directory(app.config['REPORT_FOLDER'], 'combinedreport.html')
    except Exception as e:
        return jsonify({'success': False, 'message': f'View report error: {str(e)}'})


@app.route('/download-report')
def download_report():
    """Download the combined HTML report"""
    try:
        return send_from_directory(app.config['REPORT_FOLDER'], 'combinedreport.html', as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Download error: {str(e)}'})


@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'message': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
    try:
        app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Interrupted")
    finally:
        progress_cleanup()