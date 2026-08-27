# Windows 本地运行指南

这套流程面向 Windows、PowerShell 和 NVIDIA GPU。命令均从仓库根目录执行，Python 环境固定为 `.venv`。Qwen3-4B 的 Transformers BF16 + LoRA 路径建议准备 16 GB 显存；QLoRA 训练和模型合并耗时较长，先运行各脚本的 `-CheckOnly` 可以只检查参数和本地文件。

## 1. Python、CUDA 与运行时配置

```powershell
.\quickstart\windows\01-check-environment.ps1 -InstallDependencies
```

脚本会检查 Python 3.11/3.12、NVIDIA 驱动、PyTorch CUDA、`.venv` 和 `config/runtime_models.json`。云端密钥和本地服务 token 只从环境变量读取，不写入 JSON：

```powershell
[Environment]::SetEnvironmentVariable(
  "LOCALRAG_CLOUD_API_KEY",
  "填入云端 API Key",
  "User"
)
[Environment]::SetEnvironmentVariable(
  "LOCALRAG_MODEL_API_TOKEN",
  "填入一段随机长字符串",
  "User"
)
```

旧版 `runtime_models.json` 如果还含明文 `api_key`，可执行一次迁移：

```powershell
.\quickstart\windows\01-check-environment.ps1 -MigrateRuntimeConfig
```

迁移会把旧密钥写入 Windows 用户级环境变量，并把 JSON 升级为三角色配置。命令结束后重新打开 PowerShell，让用户级环境变量进入新进程。

## 2. 下载基础模型

默认从 Hugging Face 下载 Qwen3-4B：

```powershell
.\quickstart\windows\02-download-model.ps1
```

网络访问 Hugging Face 不稳定时可改用 ModelScope：

```powershell
.\.venv\Scripts\python.exe -m pip install modelscope
.\quickstart\windows\02-download-model.ps1 -Source ModelScope
```

只检查当前权重是否完整：

```powershell
.\quickstart\windows\02-download-model.ps1 -CheckOnly
```

向量检索还需要 `BAAI/bge-m3` 和 `BAAI/bge-reranker-base`，下载方法相同：

```powershell
.\quickstart\windows\02-download-model.ps1 `
  -ModelId BAAI/bge-m3 `
  -Output models/bge-m3

.\quickstart\windows\02-download-model.ps1 `
  -ModelId BAAI/bge-reranker-base `
  -Output models/bge-reranker-base
```

## 3. 准备默认语料和微调数据

仓库已包含清洗后的 100 篇默认语料和 `source_registry.json`，但不提交 Chroma 索引。下面的命令会：

1. 把 203 条训练数据拆成 183 条训练集和 20 条验证集；
2. 按 `doc_type_aware` 策略重建默认语料索引；
3. 更新 `config/active_corpus.json`，让 Streamlit 直接读取新索引。

```powershell
.\quickstart\windows\03-prepare-data.ps1
```

索引构建会加载 BGE-M3，并处理全部语料。只准备微调数据时使用：

```powershell
.\quickstart\windows\03-prepare-data.ps1 -SkipIndex
```

只核对行数和已有文件：

```powershell
.\quickstart\windows\03-prepare-data.ps1 -CheckOnly
```

### 使用自己的语料

正文建议先清洗为 Markdown，再在 registry 中为每篇文档增加一条记录。最少要保证以下字段存在：

```json
{
  "source_id": "paper-example-001",
  "path_or_url": "data/sources/papers/example.md",
  "doc_type": "paper",
  "title": "Example Paper",
  "origin_url": "https://example.com/paper",
  "version": "2026-01"
}
```

`source_id` 必须稳定且唯一；`path_or_url` 在本地语料场景下填写仓库相对路径；`doc_type` 可使用 `official_doc`、`paper`、`report`、`standard` 或 `untyped`。修改 registry 后重新运行 `03-prepare-data.ps1`。

## 4. 4-bit QLoRA 微调

先安装项目记录使用的 LLaMA-Factory 0.9.5，并执行前置检查：

```powershell
.\quickstart\windows\04-train-qlora.ps1 `
  -InstallLlamaFactory `
  -CheckOnly
```

确认输出为 `train_rows=183`、`validation_rows=20`、`cuda_available=True` 后开始训练：

```powershell
.\quickstart\windows\04-train-qlora.ps1
```

训练配置位于 `finetune/llamafactory_configs/localrag_sft_full_qlora.yaml`，核心参数是 Qwen3-4B、bitsandbytes 4-bit、LoRA rank 8 / alpha 16、1 epoch。输出写入：

```text
saves/Qwen3-4B-Thinking/lora/localrag_sft_full_qlora
```

仓库已有报告中的微调指标来自实际评测的 E6.1 本地微调模型，不代表基础 Qwen3-4B，也不自动代表按本节重新训练出的 adapter。新 adapter 应重新执行第 7 步。

## 5. 合并模型与可选 GGUF

检查 adapter 和导出配置：

```powershell
.\quickstart\windows\05-export-model.ps1 -CheckOnly
```

合并 LoRA：

```powershell
.\quickstart\windows\05-export-model.ps1
```

合并结果写入 `artifacts/models/localrag-sft-full-merged`。如需 GGUF，先安装 llama.cpp，再执行其官方转换和量化工具：

```powershell
.\.venv\Scripts\python.exe `
  .\tools\llama.cpp\<版本>\source\convert_hf_to_gguf.py `
  .\artifacts\models\localrag-sft-full-merged `
  --outfile .\artifacts\models\localrag-sft-full-f16.gguf `
  --outtype f16

& .\tools\llama.cpp\<版本>\bin\llama-quantize.exe `
  .\artifacts\models\localrag-sft-full-f16.gguf `
  .\artifacts\models\localrag-sft-full-q4_k_m.gguf `
  Q4_K_M
```

主运行路径使用基础模型 + LoRA adapter，不要求先合并或量化。GGUF 适合显存更紧张、需要 llama.cpp 的环境。

## 6. 本地模型服务启动方法

仓库记录的 E6.1 adapter 已存在时：

```powershell
.\quickstart\windows\06-start-service.ps1 `
  -Profile e6_1_adapter_bf16
```

按第 4 步重新训练后：

```powershell
.\quickstart\windows\06-start-service.ps1 `
  -Profile full_sft_adapter_bf16
```

脚本会生成或校验 manifest，把 profile 的 `model_id` 和端口写入三个角色的 local 配置，然后在 `127.0.0.1:8001` 启动服务。服务保持前台运行，另开一个 PowerShell 继续后续步骤。

只检查 adapter、manifest 和端口参数：

```powershell
.\quickstart\windows\06-start-service.ps1 -CheckOnly
```

## 7. 评测模型

先跑一次快速生成检查：

```powershell
.\quickstart\windows\07-evaluate-model.ps1 -Mode Smoke
```

再运行 10 条固定质量集：

```powershell
.\quickstart\windows\07-evaluate-model.ps1 `
  -Mode Quality `
  -Profile adapter_bf16 `
  -Manifest model_deployment/manifests/e6_1_input_manifest.json
```

若评测的是 `full_sft_adapter_bf16`，将 `-Profile` 改为一个新的运行名，并把 `-Manifest` 指向 `model_deployment/manifests/full_sft_input_manifest.json`。结果写入 `results/model_quality/`。

## 8. 配置三个模型角色

`config/runtime_models.json` 分别维护 Planner、RAG 生成和会话摘要。每个角色都配置一组 cloud 和 local endpoint，再用 `route` 选择当前路径：

```json
{
  "route": "local",
  "cloud": {
    "provider": "sensenova",
    "base_url": "https://token.sensenova.cn/v1",
    "model": "sensenova-6.7-flash-lite",
    "api_key_env": "LOCALRAG_CLOUD_API_KEY"
  },
  "local": {
    "base_url": "http://127.0.0.1:8001/v1",
    "model": "localrag-qwen3-4b-e6.1",
    "api_token_env": "LOCALRAG_MODEL_API_TOKEN",
    "tool_calling_verified": true
  }
}
```

三个角色都只接受 `local` 或 `cloud`。Planner 走本地时采用非流式 local-first 调用，invocation 异常就转到该角色的 cloud 模型；RAG 和摘要由 Gateway 按错误类型处理，流式请求只有在本地尚未输出内容时才允许转 cloud。三个角色可以指向同一端口和同一模型；消息由每次请求携带，不会因为共用服务而串会话，但请求会竞争同一个单实例队列。也可以为不同角色启动不同端口的服务。

Streamlit 侧边栏只切换三个角色的 `route`，模型名和 endpoint 仍在 JSON 中维护。切换结果会写回当前 `LOCALRAG_RUNTIME_CONFIG` 指向的文件；未设置该变量时写回 `config/runtime_models.json`。研究任务执行期间切换控件会禁用。

## 9. 启动 Streamlit

另开 PowerShell，重新载入用户级密钥并启动：

```powershell
$env:LOCALRAG_CLOUD_API_KEY = [Environment]::GetEnvironmentVariable("LOCALRAG_CLOUD_API_KEY", "User")
$env:LOCALRAG_MODEL_API_TOKEN = [Environment]::GetEnvironmentVariable("LOCALRAG_MODEL_API_TOKEN", "User")
.\.venv\Scripts\python.exe -m streamlit run app_qa.py --server.fileWatcherType none
```

页面默认读取 `config/active_corpus.json` 指向的索引。E6.1 profile 已通过本地 `rag_search` tool-calling smoke，启动脚本会把 Planner 的 `tool_calling_verified` 写为 `true`；重新训练的 full-SFT adapter 在单独完成相同验证前保持 `false`。Planner 本地 invocation 异常会转到同角色 cloud 模型；RAG 和摘要的降级则受 Gateway 错误分类和首 token 边界约束。
