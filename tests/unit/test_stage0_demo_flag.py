"""Paper runs must not carry the demo speed hack.

Why this file was written
-------------------------
The interactive dashboard would show a stalled car sitting at 0 m/s for the rest
of a long run whenever the failsafe stepped down to NOMINAL after a fault, and
an audience cannot see a loop react to anything if nothing is moving. The fix
was one line: while NOMINAL and speed < 1 m/s, snap the plant's true speed back
to the reference. The line lives at the bottom of ``training.closed_loop
.drive_closed_loop``'s per-tick body.

That same function is called by every benchmark, every experiment under
``experiments/phase5_od8_h7/`` and every integration test. If the hack fires in
those runs, the measurement is not the system under study: it is a system that
silently re-injects momentum into the plant whenever the guard relaxes, which
would confound both the E18-R3c "monitor goes silent under sustained fault"
result and the E21 "L1 catches it in 5 ticks" baseline.

Stage 0 of the 19 September 2026 handoff (§8) therefore requires the hack to
sit behind a keyword-only flag, default off, and to be turned on only by the
two demo entry points. This test enforces both halves so a future refactor
that reintroduces the mutation, or a benchmark that starts passing
``demo_speed_assist=True``, is caught before it publishes another number.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from training.closed_loop import drive_closed_loop

REPO_ROOT = Path(__file__).resolve().parents[2]

# Only these two files may pass ``demo_speed_assist=True``. Anything else --
# benchmarks, experiments, tools, tests -- must leave the default. The list is
# kept small on purpose: adding an entry is a review decision, not a refactor.
DEMO_CALLERS_ALLOWED_TO_ENABLE = frozenset(
    {
        Path("demo/dashboard.py"),
        Path("demo/narrate.py"),
    }
)

# Paths under which no file may pass ``demo_speed_assist=True``. Every published
# number in the paper is produced by code under one of these directories, so a
# violation here is what would silently reintroduce the confound.
PAPER_RUN_DIRECTORIES = ("benchmarks", "experiments", "tools", "tests", "training")


def test_the_flag_exists_and_defaults_to_off() -> None:
    """``drive_closed_loop`` must expose the flag and default it to ``False``.

    The default is the load-bearing half: every caller that does not name the
    argument gets the paper-run behaviour, so a caller added by a future
    experiment cannot forget the safe choice. If the default flips or the
    parameter is renamed, this test fails and the reviewer is asked to make
    that decision deliberately.
    """
    signature = inspect.signature(drive_closed_loop)
    assert "demo_speed_assist" in signature.parameters, (
        "drive_closed_loop must expose demo_speed_assist as a keyword-only "
        "parameter; Stage 0 of the 19 Sep 2026 handoff moved the plant-speed "
        "reset behind this flag."
    )
    parameter = signature.parameters["demo_speed_assist"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, (
        "demo_speed_assist must be keyword-only so a caller cannot enable it "
        "by accident through positional argument shuffling."
    )
    assert parameter.default is False, (
        "demo_speed_assist must default to False -- benchmarks and experiments "
        "that do not name it must get the paper-run behaviour."
    )


def _iter_python_files_under(directory: Path) -> list[Path]:
    """Every ``*.py`` under ``directory``, sorted, excluding caches."""
    return sorted(
        path
        for path in directory.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _calls_enabling_demo_speed_assist(module_path: Path) -> list[int]:
    """Line numbers where a call passes ``demo_speed_assist=True`` literally.

    We match the AST rather than the source text so a comment mentioning the
    keyword, or a keyword formatted across several lines, is handled the same
    way. Anything other than a literal ``True`` -- a variable, an expression
    -- also counts as enabled here: the safe default is the *absence* of the
    keyword, and any other spelling is a decision that must be reviewed.
    """
    try:
        source = module_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        tree = ast.parse(source, filename=str(module_path))
    except SyntaxError:
        return []
    hits: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "demo_speed_assist":
                continue
            value = keyword.value
            if isinstance(value, ast.Constant) and value.value is False:
                continue
            hits.append(keyword.lineno)
    return hits


def test_no_paper_run_directory_enables_the_demo_speed_hack() -> None:
    """No file under a paper-run directory may pass ``demo_speed_assist=True``.

    Enumerated the failures rather than asserting a boolean so a reviewer can
    read the offending file and line in the assertion, and add a deliberate
    exemption -- or, more likely, remove the call -- rather than guess.
    """
    violations: list[str] = []
    for directory_name in PAPER_RUN_DIRECTORIES:
        directory = REPO_ROOT / directory_name
        if not directory.exists():
            continue
        for module_path in _iter_python_files_under(directory):
            # This test file naturally mentions the keyword; skip itself.
            if module_path.resolve() == Path(__file__).resolve():
                continue
            for line in _calls_enabling_demo_speed_assist(module_path):
                relative = module_path.relative_to(REPO_ROOT)
                violations.append(f"  {relative}:{line}")
    assert not violations, (
        "The demo speed hack must not run in paper-adjacent code. The following "
        "call sites pass demo_speed_assist=True or a non-False value, which "
        "would silently re-inject momentum into the plant while the failsafe "
        "is NOMINAL:\n" + "\n".join(violations)
    )


def test_only_the_two_named_demo_files_may_enable_the_hack() -> None:
    """Every ``demo_speed_assist=True`` call site must be an allow-listed file.

    ``demo/`` is not a paper-run directory, so the previous test does not scan
    it; this test scans the whole repo and asserts that any file which does
    enable the hack is one of the two entry points the handoff names. If the
    demo grows a third entry point that legitimately needs the assist, add it
    to ``DEMO_CALLERS_ALLOWED_TO_ENABLE`` above -- a one-line review decision.
    """
    unexpected_enablers: list[str] = []
    for module_path in _iter_python_files_under(REPO_ROOT):
        if module_path.resolve() == Path(__file__).resolve():
            continue
        if ".venv" in module_path.parts or "site-packages" in module_path.parts:
            continue
        relative = module_path.relative_to(REPO_ROOT)
        hits = _calls_enabling_demo_speed_assist(module_path)
        if not hits:
            continue
        if relative in DEMO_CALLERS_ALLOWED_TO_ENABLE:
            continue
        for line in hits:
            unexpected_enablers.append(f"  {relative}:{line}")
    assert not unexpected_enablers, (
        "demo_speed_assist=True is allow-listed to demo/dashboard.py and "
        "demo/narrate.py only. Unexpected callers:\n"
        + "\n".join(unexpected_enablers)
        + "\n\nIf this is intentional, add the file to "
        "DEMO_CALLERS_ALLOWED_TO_ENABLE and explain in the commit message."
    )


def test_both_named_demo_entry_points_do_enable_the_hack() -> None:
    """The two demo entry points must actually pass ``demo_speed_assist=True``.

    Symmetric to the previous test: the allow-list is the closed set of files
    that may enable the hack, and this test asserts each file on the list
    actually does. If someone removes the keyword from dashboard.py or
    narrate.py -- perhaps thinking it was leftover -- the demo will silently
    stall on the first stop, and the reviewer will be asked to decide whether
    the removal was deliberate or the allow-list is now stale.
    """
    missing: list[str] = []
    for relative in sorted(DEMO_CALLERS_ALLOWED_TO_ENABLE):
        module_path = REPO_ROOT / relative
        if not module_path.exists():
            missing.append(f"  {relative}: file does not exist")
            continue
        if not _calls_enabling_demo_speed_assist(module_path):
            missing.append(f"  {relative}: allow-listed but no True call site")
    assert not missing, (
        "Every allow-listed demo file must pass demo_speed_assist=True:\n"
        + "\n".join(missing)
    )


@pytest.mark.parametrize("assist", [False, True])
def test_the_flag_threads_through_and_does_not_crash(assist: bool) -> None:
    """A trivial drive with the flag off and on both complete.

    A regression that raised inside the guarded block -- an off-by-one
    references ``plant._state`` at the wrong index, say -- would only surface
    if the guard's condition were reachable at all. This runs a short drive
    with each setting to prove the parameter threads through the call site
    without exception. The behavioural distinction between the two -- whether
    a stalled plant gets snapped back to reference speed -- is enforced by
    the guard's inspection tests above; a short drive from the default seed
    almost certainly never stalls, so we do not assert on the speed here.
    """
    result = drive_closed_loop(policy=None, ticks=20, demo_speed_assist=assist)
    assert result.issued >= 0
