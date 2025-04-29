import pandas as pd
import streamlit as st
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))  
file_path = os.path.join(current_dir, "data.xlsx") 

# 页面配置
st.set_page_config(
    page_title="叉车AMR选型工具",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 读取数据
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path): 
        st.error(f"文件不存在于路径：{file_path}")
        st.stop()
    
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1')
    except Exception as e:
        st.error(f"无法加载数据文件: {str(e)}")
        st.stop()
    
    # 清洗与转换列类型
    df['最大负载kg'] = df['最大负载kg'].astype(str).str.replace('≤', '', regex=False).astype(float)
    df['最大举升高度mm'] = df['最大举升高度mm'].astype(float)
    df['叉腿外宽mm'] = df['叉腿外宽mm'].astype(float)
    
    # Y/N 转换（注意列名大小写）
    yn_columns = ['5G', 'WiFi', '堆高场景', '纯搬运场景', '拉线编码器', '叉尖光电', '叉尖碰撞']  # 确保与实际列名一致
    for col in yn_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
            df[col] = df[col].map({'Y': True, 'N': False})

    return df  # 返回数据

# 加载数据
df = load_data(file_path)

# 初始化 session_state
def init_session_state():
    if 'load_select' not in st.session_state:
        st.session_state.load_select = "不限"
    if 'lift_select' not in st.session_state:
        st.session_state.lift_select = "不限"
    if 'width_select' not in st.session_state:
        st.session_state.width_select = "不限"
    if 'comm_5g' not in st.session_state:
        st.session_state.comm_5g = False
    if 'comm_wifi' not in st.session_state:
        st.session_state.comm_wifi = False
    if 'app_stack' not in st.session_state:
        st.session_state.app_stack = False
    if 'app_move' not in st.session_state:
        st.session_state.app_move = False
    if 'category_select' not in st.session_state:
        st.session_state.category_select = df['类别'].unique().tolist()
    if 'language_select' not in st.session_state:
        st.session_state.language_select = ['中文华睿', '中文中性', '英文华睿', '英文中性', '宁德专用']
    if 'reset' not in st.session_state:
        st.session_state.reset = False

def reset_filters():
    st.session_state.load_select = "不限"
    st.session_state.lift_select = "不限"
    st.session_state.width_select = "不限"
    st.session_state.comm_5g = False
    st.session_state.comm_wifi = False
    st.session_state.app_stack = False
    st.session_state.app_move = False
    st.session_state.category_select = df['类别'].unique().tolist()
    st.session_state.language_select = ['中文华睿', '中文中性', '英文华睿', '英文中性','宁德专用']
    st.session_state.reset = True
    st.rerun()

# 通信筛选
def filter_communication(filtered_df, communication):
    if '5G' in communication:
        filtered_df = filtered_df[filtered_df['5G'] == True]
    if 'WiFi' in communication:
        filtered_df = filtered_df[filtered_df['WiFi'] == True]
    return filtered_df

# 应用场景筛选
def filter_application(filtered_df, application):
    if '堆高场景' in application:
        filtered_df = filtered_df[filtered_df['堆高场景'] == True]
    if '纯搬运场景' in application:
        filtered_df = filtered_df[filtered_df['纯搬运场景'] == True]
    return filtered_df

def main():
    init_session_state()  # 初始化 session_state

    st.title('🚜 叉车AMR选型工具')
    
    if st.button("🔄 重置所有筛选条件"):
        reset_filters()

    # 侧边栏组件
    st.sidebar.header('🎛️ 筛选条件')
    
    with st.sidebar.expander("📐 基本参数", expanded=True):
        # 使用清洗后的列名获取数据
        load_options = ["不限"] + sorted(df['最大负载kg'].dropna().unique().astype(int).tolist())
        st.selectbox(
            "最大负载(kg)", 
            options=load_options, 
            index=load_options.index(st.session_state.load_select),
            key='load_select'
        )
        lift_options = ["不限"] + sorted(df['最大举升高度mm'].dropna().unique().astype(int).tolist())
        st.selectbox(
            "最大举升高度(mm)", 
            options=lift_options, 
            index=lift_options.index(st.session_state.lift_select),
            key='lift_select'
        )
        width_options = ["不限"] + sorted(df['叉腿外宽mm'].dropna().unique().astype(int).tolist())
        st.selectbox(
            "叉腿外宽(mm)", 
            options=width_options, 
            index=width_options.index(st.session_state.width_select),
            key='width_select'
        )
        
    # 通信与场景
    with st.sidebar.expander("📡 功能需求", expanded=True):
        st.write("**通信方式**")
        st.checkbox("5G", value=st.session_state.comm_5g, key="comm_5g")
        st.checkbox("WiFi", value=st.session_state.comm_wifi, key="comm_wifi")

        st.write("**应用场景**")
        st.checkbox("堆高场景", value=st.session_state.app_stack, key="app_stack")
        st.checkbox("纯搬运场景", value=st.session_state.app_move, key="app_move")

    # 高级选项
    with st.sidebar.expander("⚙️ 高级选项"):
        st.multiselect(
            "产品类别",
            options=df['类别'].unique().tolist(),
            default=st.session_state.category_select,
            key='category_select'
        )

        st.multiselect(
            "语言支持",
            ['中文华睿', '中文中性', '英文华睿', '英文中性','宁德专用'],
            default=st.session_state.language_select,
            key='language_select'
        )

    filtered_df = df.copy()
    
    # 数值筛选
    if st.session_state.load_select != "不限":
        filtered_df = filtered_df[filtered_df['最大负载kg'] >= float(st.session_state.load_select)]
    if st.session_state.lift_select != "不限":
        filtered_df = filtered_df[filtered_df['最大举升高度mm'] >= float(st.session_state.lift_select)]
    if st.session_state.width_select != "不限":
        filtered_df = filtered_df[filtered_df['叉腿外宽mm'] <= float(st.session_state.width_select)]

    # 功能筛选
    comms = [x for x in ['5G', 'WiFi'] if st.session_state.get(f'comm_{x.lower()}', False)]
    apps = [x for x in ['堆高场景', '纯搬运场景'] if st.session_state.get(f'app_{"stack" if x == "堆高场景" else "move"}', False)]

    filtered_df = filter_communication(filtered_df, comms)
    filtered_df = filter_application(filtered_df, apps)

    # 高级筛选
    filtered_df = filtered_df[
        (filtered_df['类别'].isin(st.session_state.category_select)) &
        (filtered_df['属性'].isin(st.session_state.language_select))
    ]

    # 显示结果
    st.subheader("📋 筛选结果")
    st.dataframe(filtered_df if not filtered_df.empty else "没有符合条件的产品")

if __name__ == "__main__":
    main()