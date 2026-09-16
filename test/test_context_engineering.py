from dataclasses import dataclass

from agent_platform.runtime.context_engineering import (
    HANDOFF_MAX_TOKENS,
    ROOM_MEMORY_MAX_TOKENS,
    build_handoff_packet,
    prepare_room_memory,
)


@dataclass
class _Turn:
    sequence: int
    agent_id: str
    content: str


@dataclass
class _Message:
    message_id: str
    role: str
    content: str


def test_handoff_packet_is_bounded_and_preserves_traceable_fields():
    marker = "source-paper-001"
    content = "\n".join([
        "结论：采用显式交接包。",
        f"来源：{marker}",
        "风险：下游仍需核对输入。",
        *(f"冗长原始上下文 {index} " + "内容" * 80 for index in range(300)),
    ])

    packet = build_handoff_packet(_Turn(2, "planner", content), target_agent_id="executor", task="实现任务")

    assert packet.source_sequence == 2
    assert packet.source_agent_id == "planner"
    assert packet.target_agent_id == "executor"
    assert packet.compressed is True
    assert packet.delivered_tokens <= HANDOFF_MAX_TOKENS + 150
    assert len(packet.summary) < len(content)
    assert marker in packet.evidence_refs
    assert any("风险" in item for item in packet.open_questions)


def test_room_memory_uses_bounded_view_and_message_references():
    messages = [
        _Message(f"message-{index}", "user" if index % 2 == 0 else "assistant", f"第 {index} 轮 " + "上下文" * 500)
        for index in range(20)
    ]

    view = prepare_room_memory(messages)

    assert view.compressed is True
    assert view.tokens_before > view.tokens_after
    assert view.tokens_after <= ROOM_MEMORY_MAX_TOKENS
    assert view.message_refs
    assert len(view.message_refs) <= 18
    assert "message-19" in view.text


def test_room_memory_can_exclude_current_message():
    messages = [_Message("old", "user", "旧约束"), _Message("current", "user", "本轮任务")]

    view = prepare_room_memory(messages, exclude_message_id="current")

    assert view.message_refs == ("old",)
    assert "旧约束" in view.text
    assert "本轮任务" not in view.text
