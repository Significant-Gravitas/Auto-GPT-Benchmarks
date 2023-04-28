from pathlib import Path

# ./Auto-GPT-Benchmarks/src/autogpt/benchmarks/
HERE = Path(__file__).parent
# ./Auto-GPT-Benchmarks/
PROJECT = HERE.parent.parent.parent
# ./Auto-GPT-Benchmarks/config/ai_settings.yaml
AI_SETTINGS = PROJECT / "config" / "ai_settings.yaml"
