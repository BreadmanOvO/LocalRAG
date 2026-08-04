from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "model_deployment/install_llama_cpp.ps1",
    ROOT / "model_deployment/convert_gguf.ps1",
    ROOT / "model_deployment/quantize_gguf.ps1",
    ROOT / "model_deployment/launch_llama.ps1",
)


class DeploymentScriptTests(unittest.TestCase):
    def test_scripts_parse_and_have_fail_closed_contract(self):
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                source = script.read_text(encoding="utf-8")
                self.assertIn("[CmdletBinding(SupportsShouldProcess = $true", source)
                self.assertIn('$ErrorActionPreference = "Stop"', source)
                self.assertIn("Resolve-Path -LiteralPath", source)
                self.assertIn("$LASTEXITCODE", source)
                command = (
                    "$errors = $null; "
                    f"[System.Management.Automation.Language.Parser]::ParseFile('{script}', "
                    "[ref]$null, [ref]$errors) | Out-Null; "
                    "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
                )
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", command],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)

    def test_install_requires_hashes_and_official_urls(self):
        source = SCRIPTS[0].read_text(encoding="utf-8")
        for field in (
            "BinaryAssetUrl",
            "BinarySha256",
            "CudaRuntimeAssetUrl",
            "CudaRuntimeSha256",
            "SourceArchiveUrl",
            "SourceArchiveSha256",
        ):
            self.assertIn(field, source)
        self.assertGreaterEqual(source.count("Get-FileHash"), 1)
        self.assertIn("tools/llama.cpp", source)
        self.assertIn("llama-server.exe", source)
        self.assertIn("llama-quantize.exe", source)
        self.assertIn("convert_hf_to_gguf.py", source)
        self.assertIn("$SegmentThresholdBytes = 64MB", source)
        self.assertIn("archive size mismatch", source)
        self.assertIn("segmented archive part size mismatch", source)

    def test_conversion_and_quantization_write_manifests(self):
        conversion = SCRIPTS[1].read_text(encoding="utf-8")
        quantization = SCRIPTS[2].read_text(encoding="utf-8")
        self.assertIn("--outtype f16", conversion)
        self.assertIn("--artifact-profile gguf_f16", conversion)
        self.assertIn("Q4_K_M", quantization)
        self.assertIn("--artifact-profile gguf_q4_k_m", quantization)
        for source in (conversion, quantization):
            self.assertIn("artifacts/models", source)
            self.assertIn("model_deployment/manifests", source)

    def test_launcher_is_loopback_only_and_has_two_explicit_modes(self):
        source = SCRIPTS[3].read_text(encoding="utf-8")
        self.assertIn('ValidateSet("ValidationF16", "ReleaseQ4")', source)
        self.assertNotIn('"0.0.0.0"', source)
        self.assertIn('"127.0.0.1"', source)
        self.assertIn('"--ctx-size", "40960"', source)
        self.assertIn('"--n-gpu-layers", "999"', source)
        self.assertIn('"--parallel", "1"', source)
        self.assertIn("--llama-base-url", source)


if __name__ == "__main__":
    unittest.main()
