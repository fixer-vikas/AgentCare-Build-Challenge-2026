from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_deliverables_exist():
    required_files = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "migrations" / "001_initial_schema.sql",
        PROJECT_ROOT / "scripts" / "seed_sample_data.py",
        PROJECT_ROOT / "docs" / "ARCHITECTURE.md",
    ]

    for path in required_files:
        assert path.exists(), f"Missing required project asset: {path.relative_to(PROJECT_ROOT)}"


def test_readme_contains_setup_and_architecture_sections():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Local setup" in readme
    assert "## Architecture" in readme
    assert "## Agents and tools" in readme
