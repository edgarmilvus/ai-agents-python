"""Harness for the tool-schema example.

The listing is deterministic: a function, the schema the model reads, and a
simulated dispatch. The harness checks that the two agree — which is the whole
point of the chapter's pitfall.
"""
import contextlib
import io
import json
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 1 (tool schema)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_tool_schema.py", "tool_schema")
    printed = log.getvalue()

    h.equal(module.celsius_to_fahrenheit(0), 32.0, "0 C is 32 F")
    h.equal(module.celsius_to_fahrenheit(100), 212.0, "100 C is 212 F")
    h.equal(module.celsius_to_fahrenheit(25), 77.0, "25 C is 77 F")

    schema = module.tool_schema
    h.equal(schema["name"], module.celsius_to_fahrenheit.__name__,
            "the schema names the function it describes")
    h.equal(list(schema["parameters"]["properties"]), ["celsius"],
            "the schema exposes the argument the function actually takes")
    h.equal(schema["parameters"]["required"], ["celsius"],
            "the argument is required in both places")

    # Calling the function the way the schema tells a model to call it.
    h.equal(module.celsius_to_fahrenheit(**{"celsius": 25.0}), 77.0,
            "the schema's key can be used as a keyword argument")
    h.contains(printed, "77.00 F", "the simulated agent reports the converted value")

    h.write_json("schema.json", {
        "function": module.celsius_to_fahrenheit.__name__,
        "schema": schema,
        "sample": {"input_celsius": 25, "output_fahrenheit": module.celsius_to_fahrenheit(25)},
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (tool schema)", FILES).crash())
