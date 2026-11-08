# -*- coding: utf-8 -*-
"""Metadata for the rebuilt radiation knowledge site.

Only editorial metadata lives here (titles, one-line descriptions, tags,
levels, dates). All article bodies are extracted verbatim from the original
HTML files in _build/orig/ at build time.
"""

SITE = {
    "name": "辐射备忘录",
    "name_full": "辐射及辐射测量仪器备忘录",
    "tagline": "辐射 · 探测器 · 测量",
    "description": "一个关于电离辐射、辐射探测与测量仪器的中文知识库。包含基础概念、剂量与单位、仪器类型、设备评测、能谱查看工具与参考文献。",
    "email": "XkXiaoYi475@outlook.com",
    "blog": "http://blog.xkxiaoyi.ink/",
    "database": "http://database.xkxiaoyi.ink/",
    "copyright": "Retpaĝo @ 2022-2024.XiaoYi No One Knows the Future",
    "credit": "Powered by XiaoYi &amp; Mikage",
    "content_updated": "2024-06-28",
}

# id, label, nav label, hub, blurb, number, icon
SECTIONS = {
    "basics": {
        "label": "基础知识",
        "nav": "基础知识",
        "hub": "base.html",
        "blurb": "从单位、本底与屏蔽开始，建立一套可靠的辐射概念。",
        "number": "01",
        "icon": "atom",
    },
    "measurement": {
        "label": "测量与仪器",
        "nav": "测量与仪器",
        "hub": "info/index.html",
        "blurb": "剂量、计数率、能量补偿，以及不同类型探测器的工作方式。",
        "number": "02",
        "icon": "gauge",
    },
    "reviews": {
        "label": "仪器评测",
        "nav": "仪器评测",
        "hub": "reviews.html",
        "blurb": "盖革管、闪烁体与半导体仪器的长期使用记录与对比。",
        "number": "03",
        "icon": "list",
    },
    "articles": {
        "label": "文章与笔记",
        "nav": "文章",
        "hub": "article.html",
        "blurb": "实验记录、采购笔记、核素故事与站点回顾。",
        "number": "04",
        "icon": "book",
    },
    "tools": {
        "label": "工具与数据",
        "nav": "工具",
        "hub": "tools.html",
        "blurb": "能谱查看、误差模拟、射程计算与数据检索入口。",
        "number": "05",
        "icon": "tools",
    },
    "about": {
        "label": "关于本站",
        "nav": "关于",
        "hub": "about.html",
        "blurb": "站点说明、联系方式、更新日志与完整的页面索引。",
        "number": "06",
        "icon": "info",
    },
    "archive": {
        "label": "站点存档",
        "nav": "存档",
        "hub": "sitemap.html",
        "blurb": "为兼容旧链接而保留的旧版页面与重复页面。",
        "number": "07",
        "icon": "archive",
    },
}

NAV_ORDER = ["basics", "measurement", "reviews", "articles", "tools", "about"]

SUBSECTIONS = {
    "units": "单位与读数",
    "life": "辐射与生活",
    "shielding": "屏蔽与衰减",
    "medical": "医学与健康",
    "usage": "测量与使用",
    "dose": "剂量与单位",
    "instruments": "仪器类型与清单",
    "gm": "盖革计数器",
    "scint": "闪烁体计数器",
    "semi": "半导体与个人剂量计",
    "fieldnotes": "实验与记录",
    "nuclei": "核素与现象",
    "site": "站点记录",
    "spectrum": "能谱查看",
    "simulation": "模拟与计算",
    "reference": "数据与参考",
    "legacy": "旧版页面",
}

# ---------------------------------------------------------------------------
# Every legacy HTML page (except WESViewer viewer workspaces, handled by their
# own template) must appear here.  "title" is the visible H1; "card" is the
# shorter label used in listings.
# ---------------------------------------------------------------------------
PAGES = {
    # ---------------- basics ----------------
    "Sv.html": dict(
        title="在此之前你需要知道的",
        card="辐射单位与仪表读数",
        section="basics", sub="units", level="入门",
        tags=["单位", "Sv", "伦琴", "贝克勒尔", "盖革计数器"],
        summary="从希沃特、伦琴、贝克勒尔到电子伏特，梳理辐射测量中最常用的单位，以及仪表读数的基本含义。",
    ),
    "radioactivity in life.html": dict(
        title="生活中常见的放射性来源",
        card="生活中常见的放射性来源",
        section="basics", sub="life", level="入门",
        tags=["钾-40", "氡", "钍", "铀", "本底"],
        summary="钾盐、石材、雨水、飞行、烟雾探测器与老式仪表——日常生活中可能遇到的放射性来源与测量记录。",
        image="img/lhj.jpg",
    ),
    "background_radiation.html": dict(
        title="背景辐射",
        card="背景（本底）辐射",
        section="basics", sub="life", level="入门",
        tags=["本底", "宇宙线", "氡", "人造辐射"],
        summary="本底辐射的来源：宇宙线、地表与建筑材料、氡，以及约占 3% 的人造贡献。",
    ),
    "pb.html": dict(
        title="辐射屏蔽",
        card="辐射屏蔽",
        section="basics", sub="shielding", level="入门",
        tags=["α射线", "β射线", "γ射线", "中子", "康普顿散射"],
        summary="α、β、γ 与中子射线的穿透力和屏蔽材料；区分辐射强度衰减与光子能量。",
        image="img/radiation_ch_8.png",
    ),
    "PB_gamma.html": dict(
        title="辐射衰减（γ射线）",
        card="辐射衰减（γ射线）",
        section="basics", sub="shielding", level="进阶",
        tags=["距离平方反比", "点源", "线源", "面源", "屏蔽"],
        summary="点源、线源与平面源的距离衰减规律，以及 γ 射线屏蔽中“数量减少而非能量减少”的含义。",
        image="img/PB_gamma/PB1.png",
    ),
    "braking_radiation.html": dict(
        title="韧致辐射",
        card="韧致辐射",
        section="basics", sub="shielding", level="进阶",
        tags=["Bremsstrahlung", "X射线管", "β衰变", "连续谱"],
        summary="带电粒子减速产生的连续 X 射线谱，以及 X 射线管与 β 衰变中的轫致辐射。",
        image="img/220px-Bremsstrahlung.svg.png",
    ),
    "rn.html": dict(
        title="氡",
        card="氡",
        section="basics", sub="life", level="进阶",
        tags=["Rn-222", "衰变链", "室内空气", "肺癌"],
        summary="氡的物理性质、同位素、平衡关系、水平差异与健康风险。",
        image="img/2887ee907dc9427192e502723b6a1b4a.png",
    ),
    "info/info011.html": dict(
        title="医用 X 射线",
        card="医用 X 射线",
        section="basics", sub="medical", level="入门",
        tags=["X射线", "医学影像", "剂量", "NCRP"],
        summary="常见医用 X 光检查的典型剂量、X 射线的成像原理，以及减少暴露的方法。",
    ),
    "info/info012.html": dict(
        title="CT 扫描",
        card="CT 扫描",
        section="basics", sub="medical", level="入门",
        tags=["CT", "断层成像", "剂量", "NCRP"],
        summary="CT 扫描的辐射剂量、成像原理，以及与其他检查方式的比较。",
    ),
    "info/info013.html": dict(
        title="介入性透视手术",
        card="介入性透视手术",
        section="basics", sub="medical", level="入门",
        tags=["透视", "介入手术", "剂量", "NCRP"],
        summary="介入性透视手术的剂量范围、工作方式与防护考虑。",
    ),
    "tips/cs137.html": dict(
        title="Cs-137 与原子时代的葡萄酒",
        card="Cs-137 与葡萄酒年代",
        section="basics", sub="life", level="入门",
        tags=["Cs-137", "γ能谱", "葡萄酒", "年代鉴定"],
        summary="为什么一瓶 1945 年前的葡萄酒不该含有 Cs-137——用低水平 γ 谱学鉴定年份的故事。",
    ),
    "tips/xray.html": dict(
        title="X 射线",
        card="X 射线",
        section="basics", sub="medical", level="入门",
        tags=["X射线", "γ射线", "医学影像", "工业检测"],
        summary="X 射线的来源、与 γ 射线的区别，以及在医学与工业中的应用。",
    ),

    # ---------------- measurement ----------------
    "info/info008.html": dict(
        title="正确的使用盖革计数器",
        card="正确的使用盖革计数器",
        section="measurement", sub="usage", level="入门",
        tags=["盖革计数器", "空气剂量率", "污染", "β射线"],
        summary="使用盖革计数器测量空气剂量率的注意事项：仪器污染、β 射线、测量误差与异常读数。",
        image="img/measured_value_comparison_radiation_error.png",
    ),
    "info/info001.html": dict(
        title="关于能量补偿",
        card="关于能量补偿",
        section="measurement", sub="usage", level="进阶",
        tags=["能量补偿", "能量响应", "剂量率", "闪烁体"],
        summary="能量补偿为什么重要：探测器能量响应、补偿方式，以及没有补偿时的读数偏差。",
    ),
    "info/info017.html": dict(
        title="每分钟计数（CPM）",
        card="每分钟计数（CPM）",
        section="measurement", sub="dose", level="入门",
        tags=["CPM", "CPS", "计数率", "剂量率"],
        summary="CPM 与 CPS 的定义，以及计数率与剂量率之间为何不能直接换算。",
    ),
    "info/info018.html": dict(
        title="等效剂量",
        card="等效剂量与辐射权重因子",
        section="measurement", sub="dose", level="专业",
        tags=["等效剂量", "辐射权重因子", "ICRP", "Q(L)"],
        summary="等效剂量、辐射权重因子与计算方法，附 ICRP 权重因子表。",
        image="img/2023-01-08 231556.jpg",
    ),
    "info/info019.html": dict(
        title="有效剂量",
        card="有效剂量",
        section="measurement", sub="dose", level="专业",
        tags=["有效剂量", "组织权重因子", "内照射", "外照射"],
        summary="有效剂量、组织权重因子、内外照射路径与计算方式。",
    ),
    "info/info022.html": dict(
        title="用盖革计数器测量 β 射线时的错误指示",
        card="β 射线测量中的错误指示",
        section="measurement", sub="usage", level="进阶",
        tags=["β射线", "盖革计数器", "Sv/h", "表面污染"],
        summary="为什么盖革计数器把 β 射线计入后会出现高估十倍的 Sv/h 读数，以及正确的测量方式。",
    ),
    "info/info023.html": dict(
        title="白话辐射剂量单位 Gy 和 Sv 的异同",
        card="Gy 与 Sv 的异同",
        section="measurement", sub="dose", level="入门",
        tags=["Gy", "Sv", "吸收剂量", "当量剂量", "有效剂量"],
        summary="用直白的方式解释 Gy 与 Sv 的共同点与差异，以及比释动能、吸收剂量、当量剂量和有效剂量。",
    ),
    "detector.html": dict(
        title="辐射测量仪器的类型",
        card="辐射测量仪器的类型",
        section="measurement", sub="instruments", level="进阶",
        tags=["GM管", "闪烁体", "半导体", "电离室", "能量分辨率"],
        summary="GM 管、闪烁体、半导体与电离室的测量原理、灵敏度、能量分辨率与适用场景，附核素辐射类型表。",
        image="img/inspector alert kuwetka.jpg",
    ),
    "detector_list.html": dict(
        title="辐射仪器列表",
        card="辐射仪器列表",
        section="measurement", sub="instruments", level="进阶",
        tags=["仪器清单", "价格", "能量补偿", "推荐指数"],
        summary="按使用目的、能量补偿、报警与价格整理的辐射仪器清单。",
        image="img/vn.png",
    ),
    "detector_list_2.html": dict(
        title="辐射仪器推荐（闪烁体机型）",
        card="辐射仪器推荐（闪烁体）",
        section="measurement", sub="instruments", level="进阶",
        tags=["闪烁体", "NaI", "推荐", "价格"],
        summary="闪烁体机型的功能、量程、灵敏度与价格对照表。",
    ),

    # ---------------- reviews ----------------
    "info2/Thermo_EPD MK2.html": dict(
        title="电子个人剂量计 Thermo Fisher Scientific EPD MK2+ 评测",
        card="Thermo EPD MK2+",
        section="reviews", sub="semi", level="进阶",
        tags=["个人剂量计", "半导体", "Hp(10)", "Thermo Fisher"],
        summary="Thermo Fisher 电子个人剂量计：宽能响、Hp(10)/Hp(0.07)、β 测量与佩戴方向。",
        image="img/Thermo_EPD MK2/A1.jpg", date="2024/1/8",
        specs=["半导体", "Hp(10)", "1 μSv–16 Sv"],
    ),
    "info2/RJ_RJ31-6503.html": dict(
        title="闪烁体计数器 仁机 RJ31-6503 评测",
        card="仁机 RJ31-6503",
        section="reviews", sub="scint", level="进阶",
        tags=["闪烁体", "CsI", "个人剂量计", "能量补偿"],
        summary="最便宜的 CsI 闪烁体计数器之一：体积、灵敏度、能响与读数表现。",
        image="img/RJ RJ31-6503/A1.jpg", date="2024/1/6",
        specs=["CsI 闪烁体", "Hp(10)", "IPX4"],
    ),
    "info2/Imdetek_RAM-01.html": dict(
        title="半导体计数器 imdetek RAM-01 评测",
        card="imdetek RAM-01",
        section="reviews", sub="semi", level="进阶",
        tags=["CZT", "半导体", "个人剂量计", "小型化"],
        summary="CZT 半导体个人剂量计：55 g 机身、Hp(10)、快速响应与一周续航。",
        image="img/imdetek RAM-01/A1.jpg", date="2023/12/27",
        specs=["CZT 半导体", "55 g", "7 天续航"],
    ),
    "info2/Polimaster_PM1405.html": dict(
        title="盖革计数器 Polimaster PM1405 评测",
        card="Polimaster PM1405",
        section="reviews", sub="gm", level="进阶",
        tags=["GM管", "β测量", "Hp(10)", "PC软件"],
        summary="可测 β 的 GM 管巡测仪：三种测量模式、Hp(10)、PC 软件与高量程。",
        image="img/Polimaster PM1405/A1.jpg", date="2023/12/14",
        specs=["GM 管", "β + γ", "100 mSv/h"],
    ),
    "info2/Polimaster_PM1621.html": dict(
        title="盖革计数器 Polimaster PM1621 评测",
        card="Polimaster PM1621",
        section="reviews", sub="gm", level="进阶",
        tags=["GM管", "个人剂量计", "IP67", "宽能响"],
        summary="Polimaster 个人剂量计：IP67、AA 电池 12 个月、宽能响与型号差异。",
        image="img/Polimaster PM1621/A1.jpg", date="2023/12/10",
        specs=["GM 管", "IP67", "10 keV–20 MeV"],
    ),
    "info2/RADIACODE_RADIACODE102.html": dict(
        title="闪烁体计数器 RADIACODE 102 评测",
        card="RADIACODE 102",
        section="reviews", sub="scint", level="进阶",
        tags=["闪烁体", "能谱", "核素分析", "长续航"],
        summary="带能谱的闪烁体剂量计：200 小时续航、核素分析、地图记录与 β 测量。",
        image="img/RADIACODE102/A1.jpg", date="2023/10/9",
        specs=["CsI 闪烁体", "能谱", "200 小时"],
    ),
    "info2/KB_NEW_KB6011.html": dict(
        title="盖革计数器 空霸 NEW KB6011 评测",
        card="空霸 NEW KB6011",
        section="reviews", sub="gm", level="进阶",
        tags=["GM管", "KB6011", "直方图", "β测量"],
        summary="新版空霸 KB6011：铝合金外壳、直方图、β 测量与响应速度。",
        image="img/NEW KB6011/KB1.jpg", date="2023/05/7",
        specs=["GM 管", "81 g", "1200 mAh"],
    ),
    "info2/SMACH_RG1000.html": dict(
        title="盖革计数器 SMACH RG1000 评测",
        card="SMACH RG1000",
        section="reviews", sub="gm", level="进阶",
        tags=["GM管", "国产", "能量补偿", "统计测量"],
        summary="国产 GM 管剂量计：能量补偿、统计测量、β 测量与方向特性。",
        image="img/SMACH RG1000/RG1.jpg", date="2023/05/24",
        specs=["GM 管", "Hp(10)", "统计测量"],
    ),
    "info2/KB_KB6011.html": dict(
        title="盖革计数器 空霸 KB6011 评测",
        card="空霸 KB6011（旧版）",
        section="reviews", sub="gm", level="进阶",
        tags=["GM管", "KB6011", "Huahe M4011", "能量补偿"],
        summary="空霸 KB6011 旧版：Huahe M4011 管、硬件能量补偿与直方图。",
        image="img/KB60111.jpg",
        specs=["GM 管", "M4011", "铝箔补偿"],
    ),
    "info2/FNIRSI_GC-01.html": dict(
        title="盖革计数器 FNIRSI GC-01 评测",
        card="FNIRSI GC-01",
        section="reviews", sub="gm", level="入门",
        tags=["GM管", "入门", "直方图", "加固外壳"],
        summary="500 元级 GM 管计数器：加固外壳、直方图、声音与反应速度。",
        image="img/FNIRSI1.jpg", date="2023/6/27",
        specs=["GM 管", "0.01 μSv/h–10 mSv/h", "1100 mAh"],
    ),

    # ---------------- articles ----------------
    "article/info001.html": dict(
        title="盖革计数器中的 β 射线的异常值",
        card="β 射线导致的 23 倍异常读数",
        section="articles", sub="fieldnotes", level="进阶",
        tags=["β射线", "空气剂量率", "Inspector+"],
        summary="同时接收 β 与 γ 时，为什么空气剂量率会显示高出 23 倍的异常值。",
        date="2022/11/1",
    ),
    "article/info002.html": dict(
        title="采购铝块",
        card="采购铝块：为 β 屏蔽准备吸收片",
        section="articles", sub="fieldnotes", level="入门",
        tags=["铝", "β屏蔽", "轫致辐射", "吸收片"],
        summary="用不同厚度的铝块屏蔽 β 射线，并为能谱测量准备吸收片。",
        image="img/article/LV1.jpg", date="2023/5/31",
    ),
    "article/info003.html": dict(
        title="盖革计数器 TERRA MKS-05 简单操作使用说明",
        card="TERRA MKS-05 操作说明",
        section="articles", sub="fieldnotes", level="入门",
        tags=["MKS-05", "操作说明", "报警阈值"],
        summary="TERRA MKS-05 的开机、模式切换、报警阈值与按键操作说明。",
        date="2023/9/30",
    ),
    "article/info004.html": dict(
        title="仪表的灵敏度越高越好吗？",
        card="灵敏度越高越好吗？",
        section="articles", sub="fieldnotes", level="进阶",
        tags=["灵敏度", "盖革管", "闪烁体", "实用性"],
        summary="灵敏度不等于实用性：盖革管与闪烁体在不同射线与场景下的差异。",
        date="2023/11/29",
    ),
    "article/info005.html": dict(
        title="野狼 V1019 氚手表",
        card="野狼 V1019 氚手表",
        section="articles", sub="fieldnotes", level="入门",
        tags=["氚", "T100", "手表", "自发光"],
        summary="野狼 V1019 氚手表、T25/T100 的含义与夜光表现。",
        image="img/T100/A1.jpg", date="2024/2/21",
    ),
    "other/info005.html": dict(
        title="网站一周年！",
        card="网站一周年：仪器、数据与回顾",
        section="articles", sub="site", level="入门",
        tags=["站点回顾", "仪器收藏", "访问数据"],
        summary="建站一周年的回顾：访问数据、仪器收藏与主观推荐。",
        image="img/other/info005/A1.jpg", date="2023/12/12",
    ),
    "other/info001.html": dict(
        title="中子温度",
        card="中子温度与能量区间",
        section="articles", sub="nuclei", level="专业",
        tags=["中子", "热中子", "快中子", "麦克斯韦分布"],
        summary="中子能量分布区间：快中子、热中子、超热中子与各自的能量定义。",
    ),
    "other/info002.html": dict(
        title="花岗岩",
        card="花岗岩的放射性",
        section="articles", sub="nuclei", level="入门",
        tags=["花岗岩", "氡", "建筑材料", "国家标准"],
        summary="花岗岩的放射性、氡析出与建筑材料放射性标准。",
    ),
    "other/info003.html": dict(
        title="Fusor",
        card="Fusor：桌面核聚变装置",
        section="articles", sub="nuclei", level="进阶",
        tags=["Fusor", "惯性静电约束", "核聚变", "中子源"],
        summary="Fusor 惯性静电约束聚变装置的结构、原理与常见误解。",
        image="https://upload.wikimedia.org/wikipedia/commons/c/c1/Fusor_running.jpg",
    ),
    "net.html": dict(
        title="辐射噪点",
        card="辐射噪点是什么样",
        section="articles", sub="nuclei", level="入门",
        tags=["辐射噪点", "图像传感器", "电离"],
        summary="网络图片中的辐射噪点与真实探测器噪点的区别。",
        image="img/fs1.png",
    ),
    "history.html": dict(
        title="更新日志历史",
        card="2022–2023 更新历史",
        section="about", sub="site", level="入门",
        tags=["更新日志", "站点历史"],
        summary="2022 年 12 月至 2023 年 1 月的站点改动记录。",
    ),

    # ---------------- tools ----------------
    "tool/WESViewer/index.html": dict(
        title="辐射光谱显示工具 WESViewer",
        card="WESViewer 能谱查看器",
        section="tools", sub="spectrum", level="进阶",
        tags=["能谱", "WESViewer", "HTML5", "BG扣除"],
        summary="在浏览器中查看、比较与扣除本底的光谱工具，支持读取 XML 光谱数据与核素信息。",
        image="tool/WESViewer/icon.png", date="2024/2/11",
        tool=True,
    ),
    "tool/error simulation.html": dict(
        title="辐射测量仪器（盖革计数器）的误差模拟",
        card="误差模拟",
        section="tools", sub="simulation", level="进阶",
        tags=["泊松分布", "误差", "模拟", "盖革计数器"],
        summary="用泊松统计模拟盖革计数器达到指定误差所需的时间，并绘制误差收敛曲线。",
        tool=True, wide=True,
    ),
    "tool/jitter simulation.html": dict(
        title="辐射测量装置（盖革计数器）误差恒定的测量值抖动模拟",
        card="测量值抖动模拟",
        section="tools", sub="simulation", level="进阶",
        tags=["统计抖动", "误差阈值", "灵敏度"],
        summary="模拟恒定剂量下测量值的统计抖动，以及误差阈值如何影响读数。",
        tool=True, wide=True,
    ),
    "tool/beta ray range calculation.html": dict(
        title="β 射线射程计算工具",
        card="β 射线射程计算",
        section="tools", sub="simulation", level="进阶",
        tags=["β射线", "射程", "铝", "空气", "水", "混凝土"],
        summary="计算 β 粒子在铝、空气、水、混凝土中的最大射程，并支持自定义材料密度。",
        tool=True, wide=True,
    ),
    "tool/info004.html": dict(
        title="辐射测量仪器的灵敏度",
        card="灵敏度与读数稳定性",
        section="tools", sub="simulation", level="进阶",
        tags=["灵敏度", "刷新间隔", "平均", "模拟"],
        summary="模拟灵敏度、刷新间隔与平均时间对读数稳定性和响应速度的影响。",
        tool=True, wide=True,
    ),
    "info/info010[X].html": dict(
        title="数据库与核数据入口",
        card="数据库与核数据",
        section="tools", sub="reference", level="专业",
        tags=["裂变产额", "IAEA", "PGAA", "中子俘获截面"],
        summary="裂变产额、IAEA 数据、PGAA 瞬发伽马与中子俘获截面图谱的入口（原数据库链接）。",
    ),
    "修正关于KB6011型辐射计能量响应的方案.pdf": dict(
        title="修正关于 KB6011 型辐射计能量响应的方案",
        card="KB6011 能量响应修正方案（PDF）",
        section="articles", sub="research", level="专业",
        tags=["KB6011", "能量响应", "研究", "PDF"],
        summary="关于 KB6011 型辐射计能量响应修正方案的研究文档（PDF，1.0 MB）。",
        kind="pdf", date="2024/6/28",
    ),

    # ---------------- archive / legacy ----------------
    "cs137.html": dict(
        title="Cs-137（旧版）",
        card="Cs-137（旧版重复页面）",
        section="archive", sub="legacy", level="入门",
        tags=["Cs-137", "存档"],
        summary="与 tips/cs137.html 内容相同的旧版页面，保留以兼容旧链接。",
        canonical="tips/cs137.html",
    ),
    "xray.html": dict(
        title="X 射线（旧版）",
        card="X 射线（旧版重复页面）",
        section="archive", sub="legacy", level="入门",
        tags=["X射线", "存档"],
        summary="与 tips/xray.html 内容相同的旧版页面，保留以兼容旧链接。",
        canonical="tips/xray.html",
    ),
    "other/info004.html": dict(
        title="辐射噪点（旧版）",
        card="辐射噪点（旧版重复页面）",
        section="archive", sub="legacy", level="入门",
        tags=["辐射噪点", "存档"],
        summary="与 net.html 内容相同的旧版页面；其图片路径在原站点中即已失效。",
        canonical="net.html",
    ),
    "关于辐射和辐射探测器的文章.html": dict(
        title="关于辐射和辐射探测器的文章（旧版）",
        card="文章索引（旧版入口）",
        section="archive", sub="legacy", level="入门",
        tags=["文章索引", "存档"],
        summary="文章索引的早期版本，只列出了第一篇文章，保留以兼容旧链接。",
        canonical="article.html",
    ),
    "Untitled-1.html": dict(
        title="旧版主页存档",
        card="旧版主页与完整目录",
        section="archive", sub="legacy", level="入门",
        tags=["旧版主页", "目录", "更新日志", "存档"],
        summary="改版前的完整站点目录与更新日志，作为历史记录保留。",
    ),
    "Ju.html": dict(
        title="超大蜜柑（",
        card="超大蜜柑（",
        section="archive", sub="legacy", level="入门",
        tags=["存档", "照片"],
        summary="一张超大蜜柑的照片页面；原图 img/ju.jfif 在旧站中已缺失。",
    ),
}

# Pages whose content is authored by the new design rather than extracted.
GENERATED_HUBS = {
    "index.html": dict(title=SITE["name"], section="home"),
    "base.html": dict(title="基础知识", section="basics"),
    "info/index.html": dict(title="测量与仪器", section="measurement"),
    "reviews.html": dict(title="仪器评测", section="reviews"),
    "article.html": dict(title="文章与笔记", section="articles"),
    "other/index.html": dict(title="其他与专题", section="articles"),
    "tools.html": dict(title="工具与数据", section="tools"),
    "about.html": dict(title="关于本站", section="about"),
    "search.html": dict(title="搜索", section="search"),
    "sitemap.html": dict(title="站点地图", section="archive"),
    "changelog.html": dict(title="更新日志", section="about"),
}

# WESViewer isotope landing pages
WES_GALLERY = {
    "tool/WESViewer/isotope/Am-241/index.html": ("镅-241", "离子烟感报警器", "不含其他放射性同位素"),
    "tool/WESViewer/isotope/Co-60/index.html": ("钴-60", "钴磁盘源", "不含其他放射性同位素"),
    "tool/WESViewer/isotope/Cs-137/index.html": ("铯-137", "用于闪烁体自校准的 Cs 源", "不含其他放射性同位素"),
    "tool/WESViewer/isotope/Lu-176/index.html": ("镥-176", "氧化镥", "以纯净形式存在，不含其他同位素"),
    "tool/WESViewer/isotope/Ra-226/index.html": ("镭-226", "镭开关", ""),
    "tool/WESViewer/isotope/Th-232/index.html": ("钍-232", "中国产“负离子”吊坠 / 钨钍电极", "以纯净形式存在，不含其他同位素"),
}

# WESViewer spectral viewer workspaces (kept functional, wrapped in new shell)
WES_VIEWERS = {
    "tool/WESViewer/isotope/Am-241/Am-241/index.html": ("离子烟感报警器", "Am-241", "CsI 5.5%"),
    "tool/WESViewer/isotope/Co-60/Co-60/index.html": ("钴磁盘源", "Co-60", ""),
    "tool/WESViewer/isotope/Cs-137/Cs-137/index.html": ("Cs-137 校准源", "Cs-137", ""),
    "tool/WESViewer/isotope/Lu-176/Lu-176_Lutetium oxide/index.html": ("氧化镥", "Lu-176", ""),
    "tool/WESViewer/isotope/Ra-226/Ra-226_switch/index.html": ("镭开关", "Ra-226", "CsI 5.5%"),
    "tool/WESViewer/isotope/Th-232/Th-232_pendant/index.html": ("中国产“负离子”吊坠", "Th-232", ""),
    "tool/WESViewer/isotope/Th-232/Th-232_WT_electrode/index.html": ("钨钍电极", "Th-232", ""),
    "tool/WESViewer/rain/index.html": ("雨天样本光谱", "降雨沉降", ""),
    "tool/WESViewer/list/index.html": ("各类核素的光谱图", "多核素", ""),
}

# Navigation and footer link groups
FOOTER_GROUPS = [
    ("知识板块", [
        ("基础知识", "base.html"),
        ("测量与仪器", "info/index.html"),
        ("仪器评测", "reviews.html"),
        ("文章与笔记", "article.html"),
    ]),
    ("索引与工具", [
        ("工具与数据", "tools.html"),
        ("全部页面", "sitemap.html"),
        ("更新日志", "changelog.html"),
        ("搜索", "search.html"),
    ]),
    ("关于", [
        ("关于本站", "about.html"),
        ("联系方式", "about.html#contact"),
        ("外部博客", "http://blog.xkxiaoyi.ink/"),
        ("数据库", "http://database.xkxiaoyi.ink/"),
    ]),
]

# A small, factual set of starting points on the home page
PATHS = [
    {
        "level": "第一次接触",
        "title": "从单位和本底开始",
        "desc": "先知道读数代表什么，再理解环境中的辐射水平。",
        "steps": ["Sv.html", "background_radiation.html", "pb.html", "info/info008.html"],
    },
    {
        "level": "准备买仪器",
        "title": "先看类型，再看评测",
        "desc": "理解探测器差异，然后用真实使用记录缩小选择范围。",
        "steps": ["detector.html", "detector_list.html", "reviews.html", "tool/error simulation.html"],
    },
    {
        "level": "深入技术细节",
        "title": "剂量、β 测量与能谱",
        "desc": "从能量补偿到有效剂量，再到用能谱确认核素。",
        "steps": ["info/info001.html", "info/info022.html", "info/info019.html", "tool/WESViewer/index.html"],
    },
]

FEATURED_REVIEWS = [
    "info2/Thermo_EPD MK2.html",
    "info2/RADIACODE_RADIACODE102.html",
    "info2/Polimaster_PM1405.html",
]
