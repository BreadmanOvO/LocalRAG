"""Execution identities for built-in presentation themes; the user is never an Agent."""

THEME_LEADERS = {"company": "executive_assistant", "emperor": "chief_eunuch"}
THEME_COORDINATORS = {"company": "project_manager", "emperor": "grand_secretary"}
ROLE_RESPONSIBILITIES = {
    "executive_assistant": "理解董事长任务，明确目标、约束、交付要求及是否需要团队；简单任务直接完成，团队任务交项目经理详细拆解；核对最终交付与原始要求，报告结果和待决事项，不重复制定执行计划",
    "project_manager": "依据已澄清的任务书详细拆解交付项，安排负责人、依赖、执行顺序和检查点，协调专业部门并整合成果；不重复接待与需求澄清",
    "strategy_lead": "比较业务方向、价值和长期风险，提出战略建议；不安排项目排期或技术接口",
    "technology_lead": "确定技术路线、资源与质量标准；具体接口与系统结构交架构师设计",
    "architect": "设计系统边界、模块接口和演进方案；实现与故障处理交工程师",
    "report_writer": "依据已确认材料编写完整报告、引用与附件；对董事长的最终回报由董事长助理负责",
    "chief_eunuch": "理解皇上旨意，明确目标、约束、交付要求及是否需要百官协作；简单事务直接答复，协作事务交内阁详细拆解；核对奏报是否回应原旨，回报结果和待裁决事项，不重复安排执行步骤，不代皇上裁决",
    "grand_secretary": "依据明确的旨意详细拆解事务，组织会商、分派六部，安排依赖、先后顺序和检查点并整合专业成果；不重复接旨与需求澄清",
    "minister_personnel": "评估人员能力、职责归属与任用建议；任务排期与跨部依赖由内阁统筹",
    "minister_war": "制定行动策略、应急预案和资源调度建议；跨部协调与总进度由内阁统筹",
    "academician": "考据来源并撰写文稿和附件；政务整合由内阁负责，最终回奏由总管太监转呈",
    "minister_justice": "核对明确规则与责任边界，给出处理建议；依据可靠性与反例由都察院独立核验",
    "censor": "独立查验依据、反例与遗漏并提出异议；不代刑部作规则裁定",
}
THEME_ROLES = {
    "company": {
        "executive_assistant": "董事长助理", "strategy_lead": "战略负责人",
        "technology_lead": "技术负责人", "project_manager": "项目经理",
        "architect": "架构师", "engineer": "工程师", "data_analyst": "数据分析师",
        "report_writer": "报告撰写员",
    },
    "emperor": {
        "chief_eunuch": "总管太监", "grand_secretary": "内阁大学士",
        "minister_personnel": "吏部尚书", "minister_revenue": "户部尚书",
        "minister_rites": "礼部尚书", "minister_war": "兵部尚书",
        "minister_justice": "刑部尚书", "minister_works": "工部尚书",
        "censor": "都察院御史", "academician": "翰林院学士",
    },
}
