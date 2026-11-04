class WriterAgent:
    def run(self) -> str:
        return "a draft"


class EditorAgent:
    def run(self, draft: str) -> str:
        return draft


def pipeline():
    writer, editor = WriterAgent(), EditorAgent()
    return editor.run(writer.run())
