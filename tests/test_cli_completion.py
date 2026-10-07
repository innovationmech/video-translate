"""Exercise shell completion through the real CLI entry point."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def cli_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env.pop("_ARGCOMPLETE", None)
    return env


def complete(line, tmp_path, monkeypatch):
    output = tmp_path / "completions.txt"
    env = cli_env()
    env.update(
        _ARGCOMPLETE="1",
        _ARGCOMPLETE_IFS="\n",
        _ARGCOMPLETE_SUPPRESS_SPACE="1",
        _ARGCOMPLETE_STDOUT_FILENAME=str(output),
        COMP_LINE=line,
        COMP_POINT=str(len(line)),
    )
    monkeypatch.chdir(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "video_translate"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    return output.read_text().splitlines()


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("video-translate --sou", {"--source", "--source-only", "--source-first"}),
        ("video-translate video.mp4 --model m", {"medium"}),
        ("video-translate --translator o", {"openai"}),
        ("video-translate --source j", {"ja"}),
        ("video-translate -t z", {"zh"}),
        ("video-translate --summary-lang k", {"ko"}),
        ("video-translate --target=zh", {"--target=zh"}),
        ("video-translate --hw-accel v", {"videotoolbox"}),
    ],
)
def test_completion_candidates(line, expected, tmp_path, monkeypatch):
    assert set(complete(line, tmp_path, monkeypatch)) == expected


def test_video_path_completion(tmp_path, monkeypatch):
    (tmp_path / "movie clip.mp4").touch()
    assert complete("video-translate mov", tmp_path, monkeypatch) == ["movie\\ clip.mp4"]


def test_output_completes_only_directories(tmp_path, monkeypatch):
    (tmp_path / "output-dir").mkdir()
    (tmp_path / "output-file.txt").touch()
    assert complete("video-translate -o out", tmp_path, monkeypatch) == ["output-dir/"]


@pytest.mark.parametrize("option", ["--api-key", "--font-size", "--llm-model"])
def test_freeform_values_do_not_suggest_files(option, tmp_path, monkeypatch):
    (tmp_path / "private-file.txt").touch()
    assert complete(f"video-translate {option} pri", tmp_path, monkeypatch) == []


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_print_completion_without_video_or_api_key(shell):
    env = cli_env()
    env.pop("DEEPSEEK_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, "-m", "video_translate", "--print-completion", shell],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()
    executable = shutil.which(shell)
    if executable:
        syntax = subprocess.run(
            [executable, "-n"], input=result.stdout, capture_output=True, text=True
        )
        assert syntax.returncode == 0, syntax.stderr


def test_normal_invocation_still_requires_video():
    result = subprocess.run(
        [sys.executable, "-m", "video_translate"],
        env=cli_env(),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "video" in result.stderr
