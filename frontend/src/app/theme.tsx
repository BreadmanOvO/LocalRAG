import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

export type ThemeId = "company" | "emperor";

export type ThemeRole = {
  id: string;
  department: string;
  title: string;
  responsibility: string;
  focus: string;
};

export type ThemeDefinition = {
  id: ThemeId;
  name: string;
  setupLabel: string;
  leadLabel: string;
  taskHeading: string;
  taskAction: string;
  taskPlaceholder: string;
  roles: ThemeRole[];
};

export const themes: Record<ThemeId, ThemeDefinition> = {
  company: {
    id: "company",
    name: "公司",
    setupLabel: "公司设置",
    leadLabel: "董事长助理",
    taskHeading: "下达新任务",
    taskAction: "下达任务",
    taskPlaceholder: "说明目标、已知信息和你期待的交付结果",
    roles: [
      { id: "chairperson", department: "董事长办公室", title: "董事长", responsibility: "确定目标、优先级与最终取舍", focus: "决策与裁决" },
      { id: "executive_assistant", department: "董事长办公室", title: "董事长助理", responsibility: "接收任务、组织协作与汇总回报", focus: "任务统筹" },
      { id: "strategy_lead", department: "战略发展部", title: "战略负责人", responsibility: "定义问题边界、比较路径与关键风险", focus: "方向判断" },
      { id: "technology_lead", department: "技术委员会", title: "技术负责人", responsibility: "评估技术可行性、资源与实现约束", focus: "技术决策" },
      { id: "project_manager", department: "项目管理办公室", title: "项目经理", responsibility: "拆解交付、安排依赖并跟踪进度", focus: "项目推进" },
      { id: "architect", department: "技术委员会", title: "架构师", responsibility: "设计系统边界、接口和演进路径", focus: "架构设计" },
      { id: "engineer", department: "研发中心", title: "工程师", responsibility: "实现方案、验证行为并处理故障", focus: "实现验证" },
      { id: "researcher", department: "研究院", title: "研究员", responsibility: "检索证据、提出假设并标注不确定性", focus: "研究分析" },
      { id: "data_analyst", department: "数据智能部", title: "数据分析师", responsibility: "分析数据、核验口径与发现异常", focus: "数据洞察" },
      { id: "reviewer", department: "质量与风险委员会", title: "审查员", responsibility: "寻找反例、核查结论与识别风险", focus: "质量审查" },
      { id: "report_writer", department: "董事长办公室", title: "报告撰写员", responsibility: "组织结论、证据和待决事项", focus: "清晰交付" },
    ],
  },
  emperor: {
    id: "emperor",
    name: "当皇上",
    setupLabel: "宫廷设置",
    leadLabel: "内阁大学士",
    taskHeading: "颁布新旨意",
    taskAction: "颁布旨意",
    taskPlaceholder: "说明所要处置的事务、已知线索和期望结果",
    roles: [
      { id: "emperor", department: "御前", title: "皇上", responsibility: "定夺大政、优先次序与最终裁决", focus: "圣裁" },
      { id: "grand_secretary", department: "内阁", title: "内阁大学士", responsibility: "承旨、会商与汇总奏报", focus: "统筹" },
      { id: "chief_eunuch", department: "司礼监", title: "司礼监掌印", responsibility: "传达旨意、督办进度与校核文书", focus: "督办" },
      { id: "minister_personnel", department: "吏部", title: "吏部尚书", responsibility: "评估人事、职责和协作分派", focus: "组织调度" },
      { id: "minister_revenue", department: "户部", title: "户部尚书", responsibility: "核算资源、成本和投入产出", focus: "资源分析" },
      { id: "minister_rites", department: "礼部", title: "礼部尚书", responsibility: "整理沟通、规范与对外表达", focus: "表达规范" },
      { id: "minister_war", department: "兵部", title: "兵部尚书", responsibility: "制定推进策略、应急预案和行动节奏", focus: "行动规划" },
      { id: "minister_justice", department: "刑部", title: "刑部尚书", responsibility: "核查规则、边界和责任风险", focus: "合规审查" },
      { id: "minister_works", department: "工部", title: "工部尚书", responsibility: "审视技术实现、工艺和落地质量", focus: "工程实现" },
      { id: "censor", department: "都察院", title: "都察院御史", responsibility: "提出异议、查验依据和暴露隐患", focus: "独立监察" },
      { id: "academician", department: "翰林院", title: "翰林院学士", responsibility: "考据资料、起草文稿和归纳结论", focus: "考据撰文" },
    ],
  },
};

type ThemeContextValue = {
  theme: ThemeId | null;
  definition: ThemeDefinition | null;
  setTheme: (theme: ThemeId) => void;
};

const storageKey = "betheboss.theme.v1";
const roomThemeStorageKey = "betheboss.room-themes.v1";
const ThemeContext = createContext<ThemeContextValue | null>(null);

function readStoredTheme(): ThemeId | null {
  try {
    const value = window.localStorage.getItem(storageKey);
    return value === "company" || value === "emperor" ? value : null;
  } catch {
    return null;
  }
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setSelectedTheme] = useState<ThemeId | null>(readStoredTheme);
  const setTheme = (nextTheme: ThemeId) => {
    setSelectedTheme(nextTheme);
    try {
      window.localStorage.setItem(storageKey, nextTheme);
    } catch {
      // The active tab can still use the selected theme when persistent storage is unavailable.
    }
  };
  const value = useMemo(() => ({ theme, definition: theme ? themes[theme] : null, setTheme }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

function readRoomThemeMap(): Record<string, ThemeId> {
  try {
    const raw = window.localStorage.getItem(roomThemeStorageKey);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    return Object.fromEntries(Object.entries(parsed).filter(([, value]) => value === "company" || value === "emperor")) as Record<string, ThemeId>;
  } catch {
    return {};
  }
}

export function rememberRoomTheme(roomId: string, theme: ThemeId) {
  try {
    const next = { ...readRoomThemeMap(), [roomId]: theme };
    window.localStorage.setItem(roomThemeStorageKey, JSON.stringify(next));
  } catch {
    // A room remains usable when local preferences cannot be saved.
  }
}

export function roomTheme(roomId: string): ThemeId | null {
  return readRoomThemeMap()[roomId] ?? null;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used inside ThemeProvider");
  return context;
}
