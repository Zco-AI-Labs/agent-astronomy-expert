import os
import sys
import subprocess
import shutil

import re

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "hubscape-geap")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Helper to extract the new agent name from app/SKILL.md or app/agent.py
def get_new_agent_name():
    skill_md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "SKILL.md")
    if os.path.exists(skill_md_path):
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r'^name:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
            if match:
                parsed_name = match.group(1).strip()
                if parsed_name and parsed_name != "app" and parsed_name != "custom-agent":
                    return parsed_name.replace('_', '-')
        except Exception as e:
            print(f"Warning: Failed to parse app/SKILL.md for name. Error: {e}")

    agent_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "agent.py")
    if os.path.exists(agent_py_path):
        try:
            with open(agent_py_path, "r", encoding="utf-8") as f:
                code = f.read()
            match = re.search(r'(?:AdkAgent|Agent)\([\s\S]*?name\s*=\s*["\']([^"\']+)["\']', code)
            if match:
                return match.group(1).replace('_', '-')
        except Exception as e:
            print(f"Warning: Failed to parse app/agent.py for name. Error: {e}")
            
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.agent import root_agent
        if root_agent and hasattr(root_agent, "name") and root_agent.name:
            return root_agent.name.replace('_', '-')
    except Exception as e:
        print(f"Warning: Failed to import root_agent. Error: {e}")
        
    return "custom-agent"

# Helper to sync the agent name to all static config files
def sync_agent_name(new_name):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Synchronizing agent name: '{new_name}' across manifests and config files...")
    
    old_names_to_scrub = ["custom-agent", "app"]
    pyproject_path = os.path.join(project_dir, "pyproject.toml")
    if os.path.exists(pyproject_path):
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r'^name\s*=\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
            if match and match.group(1) not in old_names_to_scrub and match.group(1) != new_name:
                old_names_to_scrub.append(match.group(1))
        except Exception as e:
            print(f"Warning: Failed to read old name from pyproject.toml. Error: {e}")

    for old_name in old_names_to_scrub:
        if old_name == new_name:
            continue
            
        replacements = {
            "agents-cli-manifest.yaml": [
                (rf'^name:\s*["\']?{re.escape(old_name)}["\']?', f'name: "{new_name}"')
            ],
            "pyproject.toml": [
                (rf'^name\s*=\s*["\']?{re.escape(old_name)}["\']?', f'name = "{new_name}"')
            ],
            "uv.lock": [
                (rf'^name\s*=\s*["\']?{re.escape(old_name)}["\']?', f'name = "{new_name}"')
            ],
            os.path.join("app", "SKILL.md"): [
                (rf'^name:\s*{re.escape(old_name)}', f'name: {new_name}')
            ],
            os.path.join("deployment", "terraform", "single-project", "variables.tf"): [
                (re.escape(old_name), new_name)
            ],
            os.path.join("deployment", "terraform", "single-project", "vars", "env.tfvars"): [
                (re.escape(old_name), new_name)
            ]
        }
        
        for relative_path, rules in replacements.items():
            file_path = os.path.join(project_dir, relative_path)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    updated_content = content
                    for pattern, repl in rules:
                        updated_content = re.sub(pattern, repl, updated_content, flags=re.MULTILINE)
                            
                    if updated_content != content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)
                        print(f"  Updated {relative_path} ('{old_name}' -> '{new_name}')")
                except Exception as e:
                    print(f"Warning: Failed to update {relative_path}. Error: {e}")

# Helper to sync configuration to agents-cli-manifest.yaml
def sync_config_to_manifest():
    import json
    import yaml
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_dir, "deploy_config.json")
    is_legacy = False
    
    # Check if deploy_config.json does not exist, but legacy config.json does
    if not os.path.exists(config_path):
        legacy_path = os.path.join(project_dir, "config.json")
        if os.path.exists(legacy_path):
            config_path = legacy_path
            is_legacy = True
            print("Using legacy config.json in root for deployment options.")
            
    config_filename = os.path.basename(config_path)
    manifest_path = os.path.join(project_dir, "agents-cli-manifest.yaml")
    
    default_create_params = {
        "deployment_target": "agent_runtime",
        "is_a2a": True,
        "session_type": "in_memory",
        "cicd_runner": "skip",
        "include_data_ingestion": False,
        "datastore": "none",
        "agent_guidance_filename": "GEMINI.md"
    }

    # 1. If configuration file does not exist, extract from manifest or use defaults
    if not os.path.exists(config_path):
        print(f"{config_filename} not found. Extracting create_params from manifest...")
        create_params = default_create_params.copy()
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = yaml.safe_load(f) or {}
                if "create_params" in manifest_data and isinstance(manifest_data["create_params"], dict):
                    create_params = manifest_data["create_params"]
            except Exception as e:
                print(f"Warning: Failed to load manifest to create default {config_filename}. Error: {e}")
        
        config_data = {
            "agents-cli-manifest": {
                "create_params": create_params
            }
        }
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"  Created default {config_filename} successfully.")
        except Exception as e:
            print(f"Warning: Failed to write {config_filename}. Error: {e}")
            return

    # 2. Configuration exists (or was just created). Load and merge into manifest
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f) or {}
    except Exception as e:
        print(f"Error: Failed to parse {config_filename}. Error: {e}")
        return

    nested_manifest = config_data.get("agents-cli-manifest", {})
    if not isinstance(nested_manifest, dict):
        print(f"Warning: 'agents-cli-manifest' in {config_filename} is not a dictionary.")
        nested_manifest = {}
    config_create_params = nested_manifest.get("create_params", {})
    if not isinstance(config_create_params, dict):
        print(f"Warning: 'create_params' in {config_filename} is not a dictionary.")
        config_create_params = {}

    if not os.path.exists(manifest_path):
        print(f"Warning: Manifest file {manifest_path} does not exist. Cannot merge configuration.")
        return

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = yaml.safe_load(f) or {}
        
        if "create_params" not in manifest_data or not isinstance(manifest_data["create_params"], dict):
            manifest_data["create_params"] = {}
        
        for k, v in config_create_params.items():
            manifest_data["create_params"][k] = v
            
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(manifest_data, f, default_flow_style=False, sort_keys=False)
            
        print(f"Successfully merged create_params from {config_filename} into agents-cli-manifest.yaml.")
    except Exception as e:
        print(f"Error: Failed to update agents-cli-manifest.yaml. Error: {e}")

# Helper to verify that project core and utility files match the canonical template
def verify_core_files_up_to_date():
    """
    Verifies that all platform infrastructure files under app/core/ and app/app_utils/
    match the latest canonical version from hubscape-agent-template. If any files are
    outdated, modified, or missing, the deployment is immediately blocked.
    """
    if os.getenv("HUBSCAPE_SKIP_CORE_CHECK") == "1":
        print("⚠️ Warning: HUBSCAPE_SKIP_CORE_CHECK is enabled. Bypassing platform files integrity check.")
        return

    print("🔍 Verifying platform infrastructure files against canonical hubscape-agent-template...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    protected_dirs = ["app/core", "app/app_utils"]

    import hashlib
    import tempfile

    def get_file_hash(filepath):
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    # Determine clone URLs with authentication fallback
    gh_token = os.getenv("GH_TOKEN") or os.getenv("ORG_GITHUB_TOKEN")
    clone_candidates = []
    if gh_token:
        clone_candidates.append(f"https://x-access-token:{gh_token}@github.com/Zco-AI-Labs/hubscape-agent-template.git")
    clone_candidates.append("https://github.com/Zco-AI-Labs/hubscape-agent-template.git")
    clone_candidates.append("git@github.com:Zco-AI-Labs/hubscape-agent-template.git")

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_success = False
        clone_errors = []

        for url in clone_candidates:
            display_url = re.sub(r'https://[^@]+@', 'https://***@', url)
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, temp_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                clone_success = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                err_msg = e.stderr.strip() if hasattr(e, "stderr") and e.stderr else str(e)
                # Clean up any partial clone in temp_dir before trying next candidate
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                clone_errors.append(f"[{display_url}]: {err_msg}")

        if not clone_success:
            print("\n❌ Deployment blocked: Unable to fetch canonical template to verify platform files.")
            print("Troubleshooting details:")
            for err in clone_errors:
                print(f"  {err}")
            print("\n💡 Required Actions:")
            print("  1. Verify you have read access to 'https://github.com/Zco-AI-Labs/hubscape-agent-template'.")
            print("  2. In CI/CD, ensure 'ORG_GITHUB_TOKEN' is configured as an Organization Secret.")
            print("  3. For emergency offline/break-glass deployments, set HUBSCAPE_SKIP_CORE_CHECK=1.")
            sys.exit(1)

        mismatched_files = []
        missing_files = []
        extra_files = []

        for rel_dir in protected_dirs:
            local_dir = os.path.join(project_dir, rel_dir)
            template_dir = os.path.join(temp_dir, rel_dir)

            if not os.path.exists(local_dir):
                missing_files.append(f"{rel_dir}/ (entire directory missing)")
                continue

            if not os.path.exists(template_dir):
                continue

            # Recursively scan all files in the template's protected dir
            for root, _, files in os.walk(template_dir):
                for file in files:
                    if file.endswith((".pyc", ".pyo")) or file == "__pycache__":
                        continue
                    template_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(template_file_path, template_dir)
                    local_file_path = os.path.join(local_dir, rel_path)
                    display_rel_path = os.path.join(rel_dir, rel_path)

                    if not os.path.exists(local_file_path):
                        missing_files.append(display_rel_path)
                    else:
                        template_hash = get_file_hash(template_file_path)
                        local_hash = get_file_hash(local_file_path)
                        if template_hash != local_hash:
                            mismatched_files.append(display_rel_path)

            # Check for any rogue/extra files added inside local protected dir
            for root, _, files in os.walk(local_dir):
                for file in files:
                    if file.endswith((".pyc", ".pyo")) or file == "__pycache__":
                        continue
                    local_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(local_file_path, local_dir)
                    template_file_path = os.path.join(template_dir, rel_path)
                    display_rel_path = os.path.join(rel_dir, rel_path)
                    if not os.path.exists(template_file_path):
                        extra_files.append(display_rel_path)

        if mismatched_files or missing_files or extra_files:
            print("\n" + "=" * 80)
            print("❌ DEPLOYMENT BLOCKED: Project platform files are out of date or have been modified!")
            print("=" * 80)
            print("The following files under 'app/core/' and 'app/app_utils/' differ from canonical template:")
            if mismatched_files:
                print("\nModified / Outdated files:")
                for f in mismatched_files:
                    print(f"  • {f}")
            if missing_files:
                print("\nMissing platform files:")
                for f in missing_files:
                    print(f"  • {f}")
            if extra_files:
                print("\nUnauthorized additional files in platform directories:")
                for f in extra_files:
                    print(f"  • {f}")
            print("\n👉 Please run 'hubscape-adk -u' to upgrade your project files before deploying.")
            print("=" * 80 + "\n")
            sys.exit(1)

        print("✅ Platform files integrity verified: All files in app/core/ and app/app_utils/ match hubscape-agent-template.")


# Helper to resolve HMAC secret for platform registry sync
def get_sync_secret(project_id: str) -> str:
    # 1. Direct environment override
    secret = os.getenv("HUBSCAPE_HMAC_SECRET") or os.getenv("HUBSCAPE_KMS_MASTER_KEY")
    if secret:
        return secret
        
    # 2. Retrieve real production master secret from Google Cloud Secret Manager
    try:
        from google.cloud import secretmanager
        sm_client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/HUBSCAPE_KMS_MASTER_KEY/versions/latest"
        response = sm_client.access_secret_version(request={"name": secret_name})
        resolved = response.payload.data.decode("UTF-8").strip()
        print("🔑 Retrieved HUBSCAPE_KMS_MASTER_KEY from Google Cloud Secret Manager.")
        return resolved
    except Exception as sm_err:
        print(f"ℹ️ Could not fetch HUBSCAPE_KMS_MASTER_KEY from Secret Manager: {sm_err}")
        
    # 3. Standard fallback for local dev environments
    return "hubscape-development-master-key-fallback"


def trigger_platform_sync(project_id: str):
    backend_url = os.getenv("HUBSCAPE_BACKEND_URL", "https://hubscape-backend-w3xi4ozhca-uc.a.run.app")
    secret = get_sync_secret(project_id)
    
    endpoints = ["/admin/agents/sync", "/api/agents/sync"]
    success = False
    
    for endpoint in endpoints:
        url = f"{backend_url.rstrip('/')}{endpoint}"
        print(f"📡 Triggering immediate agent registry sync on platform backend: {url}")
        try:
            import urllib.request
            import urllib.error
            import json
            req = urllib.request.Request(
                url,
                data=b"",
                headers={
                    "X-Hubscape-Secret": secret,
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode())
                print(f"✅ Platform Agent Registry synced successfully: {res_data.get('message', 'Success')}")
                success = True
                break
        except urllib.error.HTTPError as http_err:
            try:
                err_body = http_err.read().decode()
            except Exception:
                err_body = str(http_err)
            print(f"⚠️ Sync call to {url} failed with HTTP {http_err.code}: {err_body}")
        except Exception as e:
            print(f"⚠️ Sync call to {url} failed: {e}")
            
    if not success:
        print("⚠️ Warning: Platform backend sync could not be completed automatically. Verify network access or trigger manual sync in Admin Portal.")


def main():
    # 1. Verify core files are up to date before any action is taken
    verify_core_files_up_to_date()

    # 2. Sync developer-defined config from deploy_config.json to manifest
    sync_config_to_manifest()

    # 3. Resolve the name and run synchronization before deploying
    display_name = get_new_agent_name()
    sync_agent_name(display_name)

    # Run 'uv lock' to properly regenerate and synchronize uv.lock
    uv_path = shutil.which("uv")
    if uv_path:
        print("Running 'uv lock' to synchronize and validate uv.lock...")
        try:
            subprocess.run([uv_path, "lock"], check=True)
            print("  uv.lock successfully updated and synchronized.")
        except Exception as e:
            print(f"Warning: 'uv lock' failed: {e}")
    else:
        print("Warning: 'uv' command not found. Please ensure uv is installed and run 'uv lock' to validate dependency locks.")

    print(f"Deploying {display_name} via native agents-cli...")

    agents_cli_path = shutil.which("agents-cli")
    if not agents_cli_path:
        venv_bin = os.path.dirname(sys.executable)
        fallback_path = os.path.join(venv_bin, "agents-cli")
        if os.path.exists(fallback_path):
            agents_cli_path = fallback_path
    if not agents_cli_path:
        agents_cli_path = "agents-cli"

    iam_profile = "sa-standard-agent"
    try:
        try:
            from google.cloud import firestore
        except ImportError:
            print("ℹ️ google-cloud-firestore not found. Installing dynamically...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "google-cloud-firestore"], check=True)
            from google.cloud import firestore

        db = firestore.Client(project=PROJECT_ID)
        docs = db.collection("agents").where("name", "==", display_name).limit(1).stream()
        doc = next(docs, None)
        if doc:
            iam_profile = doc.to_dict().get("iam_profile") or "sa-standard-agent"
            print(f"ℹ️ Found agent configuration in Firestore. Binding profile: {iam_profile}")
        else:
            print(f"ℹ️ Agent not found in Firestore. Defaulting to profile: {iam_profile}")
    except Exception as e:
        print(f"⚠️ Could not fetch agent profile from Firestore ({e}). Defaulting to profile: {iam_profile}")

    cmd = [
        agents_cli_path, "deploy",
        "--project", PROJECT_ID,
        "--region", LOCATION,
        "--service-name", display_name,
        "--service-account", f"{iam_profile}@{PROJECT_ID}.iam.gserviceaccount.com",
        "--no-confirm-project"
    ]

    env = os.environ.copy()
    venv_bin = os.path.dirname(sys.executable)
    env["PATH"] = f"{venv_bin}{os.path.pathsep}{env.get('PATH', '')}"

    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)
    print("🎉 Deployment completed successfully!")

    trigger_platform_sync(PROJECT_ID)


if __name__ == "__main__":
    main()