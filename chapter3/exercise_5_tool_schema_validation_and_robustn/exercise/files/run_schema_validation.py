"""Harness for exercise 5: input validation in a hashing tool."""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 5 (schema validation)", FILES)
    module = load_listing(FILES / "01_schema_validation_agent.py", "schema_validation")
    calculate = module.calculate_hash

    sha = calculate("test_data", "sha256")
    h.check("sha256" in sha or len(sha) == 64, "the sha256 digest is returned")
    md5 = calculate("test_data", "md5")
    h.check("md5" in md5 or len(md5) == 32, "the md5 digest is returned")

    rejected = calculate("test_data", "sha1")
    h.contains(rejected, "sha1", "the rejected algorithm is named")
    h.check("sha256" in rejected and "md5" in rejected,
            "the error lists the supported algorithms")

    too_big = calculate("x" * 1025, "sha256")
    h.contains(too_big, "1024", "the size guard names the limit")
    h.check(too_big != sha, "an oversized input is rejected, not hashed")

    same = calculate("test_data", "sha256")
    h.equal(same, sha, "hashing is deterministic")

    h.write_json("result.json", {
        "sha256": sha,
        "md5": md5,
        "rejected": rejected,
        "oversized": too_big,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (schema validation)", FILES).crash())
