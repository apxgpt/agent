# JINX 企业级智能体系统与 Web 控制台

**JINX** 智能自主代理系统，配备交互式 Web 控制台，实时可视化认知循环、执行日志、计划状态以及架构决策。

---

## 项目目录结构

在将 JINX 集成到您的工作项目时，目录层级应保持如下结构：

```text
您的工作项目/
├── .agent/                    # JINX 智能体目录
│   ├── JINX.yaml              # 智能体最新状态（自动更新）
│   ├── jinx.py                # 用于启动智能体的命令行主入口
│   ├── jinx_run_state.yaml    # 运行时的活跃状态与对话/工具调用日志
│   ├── src/
│   │   └── jinx/              # JINX 核心逻辑及模块
│   │
│   └── webagent/              # 可视化 Web 面板（即本系统）
│       ├── package.json       # 项目依赖与运行脚本
│       ├── server.ts          # Express + Vite 后端服务
│       ├── tsconfig.json
│       ├── vite.config.ts
│       ├── index.html
│       ├── src/               # React (TypeScript) 客户端应用
│       └── ...
```

---

## 1. 运行并设置 Python 智能体 (JINX)

### 环境依赖
* Python 3.10 或更高版本
* 已安装 `pip` 包管理器

### 初始化与运行
进入您工作项目的根目录 (`您的工作项目/`) 并启动智能体，传入具体的开发任务。首次运行时，脚本会自动为您下载所需的第三方依赖包 (`pydantic` 和 `pyyaml`)：

```bash
python .agent/jinx.py "创建一个自定义用户身份验证系统"
```

智能体会开始运行其认知循环，不断执行迭代，利用工具创建/修改代码文件，并将其工作进度保存至 `.agent/JINX.yaml` 及 `.agent/jinx_run_state.yaml`。

---

## 2. 运行并设置 Web 控制面板 (webagent)

该 Web 应用程序采用 **React + Express + Vite** 技术栈，实时监听 JINX 智能体的后台行为，展示执行步骤、终端输出、工具调用记录以及源文件比对。

### 步骤 1: 进入网页端目录
在您主项目的根目录下，跳转至 webagent 目录：
```bash
cd .agent/webagent
```

### 步骤 2: 安装 Node.js 依赖
确保您的系统已安装 Node.js (推荐 v18+)。运行以下命令安装所需依赖：
```bash
npm install
```

### 步骤 3: 启动开发模式 (Vite HMR + Express)
运行开发服务器。该命令会自动启动 Express 后端，并将 Web 客户端和端口绑定在 **3301**：
```bash
npm run dev
```
打开浏览器并访问：**`http://localhost:3301`**

### 步骤 4: 生产环境打包与运行
若要在生产环境中编译和部署该网站：
```bash
# 编译打包项目
npm run build

# 运行生产服务
npm run start
```

---

## 核心功能面板

1. **Cognitive Loop (认知循环)**：
   实时监测智能体活跃状态（感知、计划、执行、校验）、运行总时长、当前 PID 以及系统资源占用率。
2. **Multi-Step Plan (多步计划)**：
   互动式查看执行链条、测试运行结果，以及智能体在每轮优化中通过的需求指标。
3. **Workspace Insights (工作区洞察：事实、债务与待办)**：
   * **已知事实 (Scope Facts)** —— 智能体识别出的当前开发限制与系统背景事实。
   * **待办需求 (Open Requirements)** —— 仍待解决的系统或功能目标。
   * **技术债务 (Design Debt)** —— 开发期间做出的折中妥协或临时的应对方案。
4. **Terminal Console & RPC Log (终端与 RPC 审计)**：
   全面追踪大模型的所有工具调用交互（读写文件、运行 Bash）以及实时输出流。
5. **File Browser & Diff Viewer (文件树与代码比对)**：
   随时浏览智能体全新编写的代码，并使用高对比色左右对比直观显示文件改动 (`diff`)。
