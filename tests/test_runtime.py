import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from lmty.models.schema import Task
from lmty.runtime.engine import AttachmentRuntime
from lmty.runtime.package import load_package


PACKAGE = Path(__file__).parents[1] / "examples" / "frontend.lmty"


class RuntimeTests(unittest.TestCase):
    def test_package_loads(self):
        package = load_package(PACKAGE)
        self.assertEqual(package.manifest.name, "frontend")
        self.assertEqual(package.manifest.minimum_access, "B0")

    def test_visual_route_selects_browser_and_verifier(self):
        runtime = AttachmentRuntime(load_package(PACKAGE))
        result = runtime.infer(Task("t1", "Reproduzir layout visual responsivo", "visual_ui"))
        self.assertIn("render", result.route)
        self.assertIn("browser", result.decision.tools_enabled)
        self.assertTrue(result.verification["passed"])

    def test_state_is_reused(self):
        runtime = AttachmentRuntime(load_package(PACKAGE))
        runtime.infer(Task("t1", "Criar componente React", "implementation"), session_id="s1")
        runtime.infer(Task("t2", "Corrigir bug", "bug"), session_id="s1")
        self.assertEqual(runtime.state["s1"]["calls"], 2)
        self.assertEqual(len(runtime.export_traces()), 2)


if __name__ == "__main__":
    unittest.main()
