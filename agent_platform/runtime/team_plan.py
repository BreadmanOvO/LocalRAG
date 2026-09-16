"""Compile collaboration strategies into explicit, observable DAGs."""

from dataclasses import replace
from .team_scheduler import TeamStep
from agent_platform.personas.themes import THEME_COORDINATORS


_HANDOFF_FORMAT = """
这是阶段工作，不直接面向用户。结尾必须提供可交接的小结，至少包含：
1. 已确认结论或决策；
2. 使用的证据/来源/产物引用（没有则明确写无）；
3. 尚未解决的问题或风险；
4. 建议下游执行的下一步。
不要复制完整对话，不要输出与本步骤无关的背景。
""".strip()


def build_team_plan(architecture, bindings, chair, members, goal, persona_theme=None, room_memory=""):
    steps: list[TeamStep] = []

    def add(binding, title, instruction, dependencies=(), *, final_output=False):
        sequence = len(steps) + 1

        def prompt(outputs):
            shared = "\n\n".join(packet.render() for packet in outputs.values())
            context = f"\n\n上游交接包（不是完整对话，只能按需使用）：\n{shared}" if shared else ""
            memory = f"\n\n房间记忆摘要（按引用读取，不是完整对话）：\n{room_memory}" if not outputs and room_memory else ""
            format_instruction = "" if final_output else f"\n\n{_HANDOFF_FORMAT}"
            return f"原始任务：{goal}\n\n本步骤：{instruction}{memory}{context}{format_instruction}"

        steps.append(TeamStep(sequence, binding.agent_id, title, tuple(dependencies), prompt, final_output))
        return sequence

    specialists = [bindings[m.agent_id] for m in members]
    final = "核对原始目标与交付要求，给出完整答复；明确依据、未完成项和待决事项，不把计划当作已执行，不只转述部门报告。"
    if architecture == "direct":
        add(chair, "直接处理", "直接完成任务，只输出给用户的最终答复。", final_output=True)
    elif architecture == "swarm":
        brief = add(chair, "理解并路由", "理解任务、明确验收条件，并决定启动蜂群并行探索。")
        branches = [add(b, "独立探索", f"按本职独立探索：{b.spec.responsibility}。返回成果、证据缺口和建议。", [brief]) for b in specialists]
        add(chair, "核对并汇总", final, [brief, *branches], final_output=True)
    elif architecture == "adversarial":
        brief = add(chair, "理解并路由", "理解任务、明确争议焦点与验收条件，并启动对抗协作。")
        proposal = add(specialists[0], "提出方案", "提出方案，明确依据、假设和可证伪点。", [brief])
        objection = add(specialists[1], "独立质疑", "对方案逐条质疑，给出反例和未满足的要求。", [proposal])
        add(chair, "综合裁量", final + "保留尚未解决的争议，不把共识视为正确性证据。", [brief, proposal, objection], final_output=True)
    elif architecture in {"graph", "heterogeneous"}:
        root = add(chair, "明确任务", "明确交付要求，划分可独立处理的工作项。")
        branches = []
        for binding in specialists:
            instruction = f"按职责完成自己的工作项：{binding.spec.responsibility}，返回专业成果。"
            if architecture == "heterogeneous":
                capabilities = ", ".join(binding.spec.capabilities + binding.spec.modalities)
                instruction += f"当前模型声明能力：{capabilities}。仅分析实际提供的输入；缺少附件、工具或能力时报告缺口，不虚构已处理。"
            branches.append(add(binding, "能力分工" if architecture == "heterogeneous" else "执行分支", instruction, [root]))
        add(chair, "汇合交付", final, [root, *branches], final_output=True)
    elif persona_theme:
        coordinator = bindings[THEME_COORDINATORS[persona_theme]]
        specialist = next((b for b in specialists if b.agent_id != coordinator.agent_id), coordinator)
        brief = add(chair, "理解任务", "形成任务书：目标、已有信息、约束、交付形式和完成标准。缺失信息须标明，不虚构要求，不制定详细执行步骤。")
        plan = add(coordinator, "详细拆解", "依据任务书详细拆解工作项、依赖和检查点，不重复需求澄清。实际参与成员：" + ", ".join(b.display_name for b in bindings.values()), [brief])
        work = add(specialist, "专业执行", "执行自己负责的工作，返回专业成果、依据和未解决问题，不只复述计划。", [brief, plan])
        add(chair, "核对交付", final, [brief, plan, work], final_output=True)
    else:
        plan = add(chair, "制定计划", "给出步骤、依赖和验收条件。")
        work = add(specialists[0], "执行工作", "执行计划中自己负责的工作，返回事实、证据和缺口。", [plan])
        add(chair, "核对交付", final, [plan, work], final_output=True)
    if steps and not steps[-1].final_output:
        steps[-1] = replace(steps[-1], final_output=True)
    return steps
