"""Opt-in smoke tests against real AI services (API charges apply)."""

import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from functools import partial
from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch


# Keep discovery safe: only the explicit command-line entry point enables calls.
ENABLED_APIS = set()
TARGET_MODELS = {}
MODELS_FILE = Path(__file__).with_name("models.yaml")
RESULTS_DIR = Path(__file__).with_name("results")
JST = timezone(timedelta(hours=9), "JST")
API_SETTINGS = {
    "OpenAI": ("OPENAI_MODEL", ("OPENAI_API_KEY",)),
    "AzureOpenAI": (
        "AZURE_OPENAI_MODEL",
        ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"),
    ),
    "Claude": ("CLAUDE_MODEL", ("ANTHROPIC_API_KEY",)),
    "Gemini": ("GEMINI_MODEL", ("GEMINI_API_KEY",)),
}


def setUpModule():
    """Show installed SDK versions once before running this module's tests."""
    print(f"Run started: {datetime.now(JST).isoformat(timespec='seconds')}", file=sys.stderr)
    print("SDK versions:", file=sys.stderr)
    for package in ("openai", "anthropic", "google-genai"):
        try:
            installed_version = version(package)
        except PackageNotFoundError:
            installed_version = "not installed"
        print(f"  {package}: {installed_version}", file=sys.stderr)
    print(file=sys.stderr)


class Tee:
    """Write console output to a UTF-8 log as it is produced."""

    def __init__(self, console, log):
        self.console = console
        self.log = log

    def write(self, text):
        self.console.write(text)
        self.log.write(text)
        self.log.flush()
        return len(text)

    def flush(self):
        self.console.flush()
        self.log.flush()


def run_logged_tests():
    started = datetime.now(JST)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = RESULTS_DIR / f"agent_live_{started:%Y%m%d_%H%M%S_%f}.log"
    with log_path.open("x", encoding="utf-8") as log:
        with redirect_stdout(Tee(sys.stdout, log)), redirect_stderr(Tee(sys.stderr, log)):
            print(f"Result log: {log_path.resolve()}", file=sys.stderr)
            try:
                program = unittest.main(
                    module=__name__, argv=[sys.argv[0]], verbosity=2, exit=False,
                )
                return 0 if program.result.wasSuccessful() else 1
            except KeyboardInterrupt:
                print("\nInterrupted by user (KeyboardInterrupt).", file=sys.stderr)
                return 130
            finally:
                print(f"Run finished: {datetime.now(JST).isoformat(timespec='seconds')}", file=sys.stderr)


class AgentLiveTests(unittest.TestCase):
    def __init__(self, methodName="test_generation", *, api=None, model=None,
                 api_key_envvar=None, endpoint_envvar=None):
        super().__init__(methodName)
        self.api = api
        self.model = model
        self.api_key_envvar = api_key_envvar
        self.endpoint_envvar = endpoint_envvar

    def __str__(self):
        if self.api:
            label = f"{self.api} / {self.model or '(environment model)'}"
            if self.api_key_envvar:
                label += f" [{self.api_key_envvar}, {self.endpoint_envvar}]"
            return label
        return super().__str__()

    def test_generation(self):
        api = self.api
        if api not in ENABLED_APIS:
            self.skipTest("Real API calls are disabled or this service was not selected")

        model_env, required_envs = API_SETTINGS[api]
        if api == "AzureOpenAI" and self.api_key_envvar:
            required_envs = (self.api_key_envvar, self.endpoint_envvar)
        model = self.model or os.environ.get(model_env, "").strip()
        missing = [
            name for name in required_envs
            if not os.environ.get(name, "").strip()
        ]
        if not model:
            missing.append(model_env)
        self.assertFalse(
            missing,
            f"{api}: missing environment variables: {', '.join(missing)}",
        )

        # Import only after opt-in and configuration checks. No GUI is loaded.
        src_path = str(Path(__file__).resolve().parents[1] / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from agent import Agent
        from config import AIConfig, Config, ModeConfig, WindowConfig

        mode = ModeConfig(
            label="API smoke test",
            system_prompt="Reply briefly in one short sentence.",
            user_prompt="Give a short greeting to the following person:",
        )
        ai_config = AIConfig(api=api, model=model)
        if api == "AzureOpenAI" and self.api_key_envvar:
            ai_config.azure_api_key_envvar = self.api_key_envvar
            ai_config.azure_endpoint_envvar = self.endpoint_envvar
        config = Config(
            ai=ai_config,
            window=WindowConfig(),
            modes=[mode],
        )
        if api == "Gemini":
            from google import genai
            from google.genai import types

            # Still use the real SDK client; only override its HTTP settings.
            # HttpOptions.timeout is in milliseconds; attempts includes the first call.
            client_factory = partial(
                genai.Client,
                http_options=types.HttpOptions(
                    timeout=60_000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            with patch("agent.genai.Client", client_factory):
                agent = Agent(config)
        else:
            agent = Agent(config)
        self.addCleanup(agent.client.close)
        result = agent.generate_text("Alice", mode)

        self.assertIsInstance(result, str)
        self.assertTrue(result.strip(), f"{api}: response text was empty")


class ServiceTestSuite(unittest.TestSuite):
    """Print a service summary immediately after its model tests finish."""

    def __init__(self, api):
        super().__init__()
        self.api = api

    def run(self, result, debug=False):
        before = (result.testsRun, len(result.failures), len(result.errors), len(result.skipped))
        super().run(result, debug=debug)
        total, failures, errors, skipped = (
            after - start for after, start in zip(
                (result.testsRun, len(result.failures), len(result.errors), len(result.skipped)),
                before,
            )
        )
        failed = failures + errors
        succeeded = max(0, total - failed - skipped)
        stream = getattr(result, "stream", sys.stderr)
        print(
            f"{self.api} summary: total={total}, succeeded={succeeded}, "
            f"failed={failed} (failures={failures}, errors={errors}), skipped={skipped}",
            file=stream,
        )
        print(file=stream)
        stream.flush()
        return result


def load_tests(loader, tests, pattern):
    """Build one independent test per service/model, including for discovery."""
    suite = unittest.TestSuite()
    for api in API_SETTINGS:
        if ENABLED_APIS and api not in ENABLED_APIS:
            continue
        service_suite = ServiceTestSuite(api)
        models = TARGET_MODELS.get(api, [None])
        for model in models:
            settings = model if isinstance(model, dict) else {"model": model}
            service_suite.addTest(AgentLiveTests(api=api, **settings))
        suite.addTest(service_suite)
    return suite


def load_model_lists(apis):
    """Validate all selected lists before making any API calls."""
    import yaml

    with MODELS_FILE.open(encoding="utf-8") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            raise ValueError(f"Invalid YAML in {MODELS_FILE}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("models.yaml must contain a mapping keyed by service name")
    unknown = set(data) - set(API_SETTINGS)
    if unknown:
        raise ValueError(f"Unknown services in models.yaml: {', '.join(sorted(map(str, unknown)))}")
    targets = {}
    for api in apis:
        models = data.get(api)
        if not isinstance(models, list) or not models:
            raise ValueError(f"{api}: add a non-empty model list to {MODELS_FILE}")
        entries = []
        for model in models:
            if isinstance(model, str) and model.strip():
                entry = {"model": model.strip()}
            elif api == "AzureOpenAI" and isinstance(model, dict):
                fields = {"model", "api_key_envvar", "endpoint_envvar"}
                if set(model) != fields or any(
                    not isinstance(value, str) or not value.strip()
                    for value in model.values()
                ):
                    raise ValueError(
                        "AzureOpenAI: each mapping requires model, api_key_envvar "
                        "and endpoint_envvar as non-empty strings"
                    )
                entry = {key: value.strip() for key, value in model.items()}
                for key in ("api_key_envvar", "endpoint_envvar"):
                    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", entry[key]):
                        raise ValueError(f"AzureOpenAI: {key} must be an environment variable name")
            else:
                raise ValueError(f"{api}: invalid model entry (expected a non-empty model ID)")
            # A deployment on a different endpoint is a separate test target.
            if entry not in entries:
                entries.append(entry)
        targets[api] = entries
    return targets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-live-api", action="store_true",
        help="Enable real API calls (API charges apply).",
    )
    parser.add_argument(
        "--api", action="append", choices=list(API_SETTINGS),
        help="Service to test; repeat to select multiple. Default: all services.",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--all-models", action="store_true",
        help="Test every model in tests/models.yaml for the selected services.",
    )
    selection.add_argument(
        "--model", help="Test a single model ID; requires exactly one --api.",
    )
    args = parser.parse_args()
    if (args.api or args.all_models or args.model is not None) and not args.run_live_api:
        parser.error("--api, --all-models and --model require --run-live-api")
    if args.model is not None:
        if not args.api or len(args.api) != 1:
            parser.error("--model requires exactly one --api")
        if not args.model.strip():
            parser.error("--model must not be empty")
    if args.run_live_api:
        apis = list(dict.fromkeys(args.api or API_SETTINGS))
        if args.all_models:
            try:
                TARGET_MODELS.update(load_model_lists(apis))
            except (OSError, ValueError) as error:
                parser.error(str(error))
        elif args.model is not None:
            model = args.model.strip()
            if apis[0] == "AzureOpenAI":
                try:
                    entries = load_model_lists(apis)["AzureOpenAI"]
                except (OSError, ValueError) as error:
                    parser.error(str(error))
                matches = [entry for entry in entries if entry["model"] == model]
                if not matches:
                    parser.error(f"AzureOpenAI: deployment {model!r} was not found in models.yaml")
                TARGET_MODELS[apis[0]] = matches
            else:
                TARGET_MODELS[apis[0]] = [model]
        else:
            for api in apis:
                TARGET_MODELS[api] = [os.environ.get(API_SETTINGS[api][0], "").strip() or None]
        ENABLED_APIS.update(apis)
    sys.exit(run_logged_tests())
