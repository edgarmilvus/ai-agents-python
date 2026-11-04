"""An in-memory stand-in for the LangSmith client.

The chapter's listings talk to LangSmith: `create_run` opens the root span of a
trace, `list_runs` feeds the dataset builder, `create_dataset` and `create_example`
write the evaluation set. None of that can happen in a test run — it needs an
account, a key and a network — so the harness hands the listing this object
instead. It keeps the same call shapes and records what the listing asked for.
"""
import uuid


class Run:
    def __init__(self, name, run_type, inputs=None, project_name=None, tags=None,
                 metadata=None, outputs=None, status="completed"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.run_type = run_type
        self.inputs = inputs or {}
        self.outputs = outputs
        self.project_name = project_name
        self.tags = list(tags or [])
        self.metadata = dict(metadata or {})
        self.status = status


class _RunContext:
    """What `with client.create_run(...) as run:` hands back."""

    def __init__(self, run):
        self.run = run

    def __enter__(self):
        return self.run

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.run.status = "error"
        return False


class Dataset:
    def __init__(self, name, description=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.examples = []


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.runs = []
        self.datasets = {}
        self.created_runs = []
        self.created_examples = []

    # --- traces -----------------------------------------------------------
    def create_run(self, name=None, run_type="chain", inputs=None, project_name=None,
                   tags=None, metadata=None, **kwargs):
        run = Run(name or "run", run_type, inputs=inputs, project_name=project_name,
                  tags=tags, metadata=metadata)
        self.runs.append(run)
        self.created_runs.append(run)
        return _RunContext(run)

    def update_run(self, run):
        return run

    def list_runs(self, project_name=None, run_type=None, filter=None, **kwargs):
        return iter([run for run in self.runs if run.status == "completed"])

    # --- datasets ---------------------------------------------------------
    def create_dataset(self, dataset_name, description="", **kwargs):
        if dataset_name in self.datasets:
            raise ValueError(f"dataset {dataset_name!r} already exists")
        dataset = Dataset(dataset_name, description)
        self.datasets[dataset_name] = dataset
        return dataset

    def read_dataset(self, dataset_name=None, dataset_id=None, **kwargs):
        if dataset_name is not None:
            return self.datasets[dataset_name]
        for dataset in self.datasets.values():
            if dataset.id == dataset_id:
                return dataset
        raise KeyError(dataset_id)

    def create_example(self, dataset_id=None, inputs=None, outputs=None, **kwargs):
        for dataset in self.datasets.values():
            if dataset.id == dataset_id:
                example = {"inputs": inputs, "outputs": outputs}
                dataset.examples.append(example)
                self.created_examples.append(example)
                return example
        raise KeyError(dataset_id)


def seed_run(client, name, inputs, outputs, tags=None, project_name="Agent-Policy-Drift"):
    """A completed run the dataset builder can pick up."""
    run = Run(name, "agent", inputs=inputs, project_name=project_name,
              tags=tags or ["policy-A"], outputs=outputs)
    client.runs.append(run)
    return run
