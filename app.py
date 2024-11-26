import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 페이지 제목
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>반도체 시뮬레이터</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>MOSFET 및 BJT의 동작 특성을 시뮬레이션하고 3D 구조를 시각화합니다.</p>", unsafe_allow_html=True)

# 상태 초기화 및 버튼
if 'selected_device' not in st.session_state:
    st.session_state.selected_device = None

# 버튼 UI
st.sidebar.header("메뉴 선택")
if st.sidebar.button("MOSFET 3D 시뮬레이터"):
    st.session_state.selected_device = "MOSFET_3D"
if st.sidebar.button("About MOSFET"):
    st.session_state.selected_device = "MOSFET_DESC"
if st.sidebar.button("BJT 시뮬레이터"):
    st.session_state.selected_device = "BJT"

# MOSFET 3D 시뮬레이터
if st.session_state.selected_device == "MOSFET_3D":
    st.sidebar.header("⚙️ MOSFET 파라미터")
    st.sidebar.markdown("---")
    W = st.sidebar.slider("채널 폭 (W) [µm]", 0.5, 20.0, 10.0, step=0.5)
    L = st.sidebar.slider("채널 길이 (L) [µm]", 0.5, 20.0, 10.0, step=0.5)
    Vgs = st.sidebar.slider("Gate-Source Voltage (Vgs) [V]", 0.0, 5.0, 1.5, step=0.1)
    n_conc = st.sidebar.slider("N-type 농도 (상대 값)", 1e15, 1e17, 1e16, step=1e15)
    p_conc = st.sidebar.slider("P-type 농도 (상대 값)", 1e15, 1e17, 1e16, step=1e15)
    Vds_values = np.linspace(0, 5, 100)

    # N-type과 P-type의 색상 계산
    nColor = int(255 - (n_conc / 1e17) * 255)
    pColor = int(255 - (p_conc / 1e17) * 255)

    # 드레인 전류 계산 함수
    def calculate_id(Vgs, Vds, W, L, n_conc, p_conc):
        mu_n = 0.05  # 이동도 (cm^2/Vs)
        Cox = 2.3e-8  # 산화막 캐패시턴스 (F/cm^2)
        W_cm = W * 1e-4  # µm to cm
        L_cm = L * 1e-4  # µm to cm
        mu_eff = mu_n * (n_conc / p_conc)  # 이동도에 농도 영향을 반영
        if Vgs < 1.0:  # 임계 전압 Vth
            return 0
        elif Vds < Vgs - 1.0:
            return mu_eff * Cox * (W_cm / L_cm) * ((Vgs - 1.0) * Vds - (Vds ** 2) / 2)
        else:
            return 0.5 * mu_eff * Cox * (W_cm / L_cm) * (Vgs - 1.0) ** 2

    # 3D 모델 시각화 코드
    st.markdown("### 3D MOSFET 구조")
    st.write("아래의 3D 모델은 MOSFET의 기본적인 구조를 보여줍니다. 각 부분은 N-type, P-type, 소스, 드레인, 게이트, 산화막을 나타냅니다.")
    three_js_script = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        let scene, camera, renderer, controls;

        function initMOSFET() {{
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
            camera.position.set(1, 1, 3);
            camera.lookAt(0, 0, 0);

            renderer = new THREE.WebGLRenderer({{ alpha: true }});
            renderer.setSize(400, 300);
            document.getElementById('3d-simulation').appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.enableZoom = true;

            function addObjectWithEdges(geometry, material, position) {{
                const object = new THREE.Mesh(geometry, material);
                object.position.set(...position);
                scene.add(object);

                const edges = new THREE.EdgesGeometry(geometry);
                const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({{ color: 0x000000 }}));
                line.position.set(...position);
                scene.add(line);
            }}

            const nTypeGeometry = new THREE.BoxGeometry({W}, 0.5, {L});
            const nTypeMaterial = new THREE.MeshBasicMaterial({{ color: `rgb(0, 0, {nColor})` }});
            addObjectWithEdges(nTypeGeometry, nTypeMaterial, [0, -0.25, 0]);

            const pTypeGeometry = new THREE.BoxGeometry({W}, 0.5, {L});
            const pTypeMaterial = new THREE.MeshBasicMaterial({{ color: `rgb({pColor}, 0, 0)` }});
            addObjectWithEdges(pTypeGeometry, pTypeMaterial, [0, 0.25, 0]);

            const sourceGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
            const sourceMaterial = new THREE.MeshBasicMaterial({{ color: 0x777777 }});
            addObjectWithEdges(sourceGeometry, sourceMaterial, [-0.7, 0.25, 0]);

            const drainGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
            const drainMaterial = new THREE.MeshBasicMaterial({{ color: 0x777777 }});
            addObjectWithEdges(drainGeometry, drainMaterial, [0.7, 0.25, 0]);

            const gateGeometry = new THREE.BoxGeometry({W}, 0.2, 0.5);
            const gateMaterial = new THREE.MeshBasicMaterial({{ color: 0xaaaaaa }});
            addObjectWithEdges(gateGeometry, gateMaterial, [0, 0.55, 0]);

            const oxideGeometry = new THREE.BoxGeometry({W}, 0.05, {L});
            const oxideMaterial = new THREE.MeshBasicMaterial({{ color: 0x00ff00, transparent: true, opacity: 0.3 }});
            addObjectWithEdges(oxideGeometry, oxideMaterial, [0, 0.4, 0]);

            animate();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}

        initMOSFET();
    }});
    </script>

    <div id="3d-simulation" style="width: 400px; height: 300px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 10px;"></div>
    """
    st.components.v1.html(three_js_script, height=350)

    # 드레인 전류 계산 및 그래프 생성
    Id_values = [calculate_id(Vgs, Vds, W, L, n_conc, p_conc) for Vds in Vds_values]

    fig, ax = plt.subplots()
    ax.plot(Vds_values, Id_values, label=f"Vgs = {Vgs} V, W = {W:.1f} µm, L = {L:.1f} µm")
    ax.set_xlabel("Drain-Source Voltage (Vds) [V]")
    ax.set_ylabel("Drain Current (Id) [A]")
    ax.set_title("MOSFET Output Characteristics")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()
    st.pyplot(fig)

# About MOSFET
elif st.session_state.selected_device == "MOSFET_DESC":
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>About MOSFET</h2>", unsafe_allow_html=True)
    st.write("아래는 MOSFET의 다양한 구조를 보여주는 그림들입니다:")

    # 사진과 각각의 설명을 추가
    descriptions = [
        "자연 산화막 제거 : 대기중의 산소와 si가 결합하여 Si02의 자연 산화막 생성.",
        "초기 세정 : 세정공정을 통하여 산화막 제거",
        "습식 산화 : 원하는 만큼의 두께로 SiO2 산화막을 성장",
        "PR 도포 : 웨이퍼에 패턴 형성을 위해 PR을 도포",
        "노광 : 패턴이 그려진 '포토마스크'를 웨이퍼 위에 위치시키고 자외선을 조사하여 PR의 상태를 선택적으로 변화",
        "현상 : 노광된 부분을 분해하여 제거하며 이때 PR에 포토 마스크와 동일한 패턴이 형성 \n\n 하드베이크 : 잔류 용제를 제거하여 밀착력을 향상시키고 경도를 높여 다음의 식각 공정에서 식각 용액에 대한 내구성을 높임",
        "식각 : PR이 남아있는 부분은 식각용액에 의해 식각 되지 않고 PR이 벗겨진 부분만 선택적으로 식각 \n\n  산화막에 PR에 새겨진 포토마스크의 패턴과 같은 패턴이 전사",
        "PR 박리: 패턴형성이 끝났으므로 PR을 박리하여 제거 ☜ 세정공정을 활용",
        "불순물 도핑 : MOSFET의 Source와 Drain을 만들기 위해 불순물을 포함하고 있는 물질을 도포 → 산화막이 없는 부분으로부터 불순물이 주입 → 열처리를 하여 불순물을 웨이퍼로 확산 \n\n ➡️ n타입의 Source와 Drain 형성",
        "Gate의 산화막을 형성하기 위해 다시 'PR 도포-소프트 베이크-노광-현상-하드베이크-식각-PR 박리-세정-건식 산화-세정'을 거침 \n\n ➡️ Source,Gate,Drain에 단자를 형성하기 위해 PR까지 도포한 모습 → 게이트 산화막이 형성",
        "단자를 형성하기 위해 'PR 코팅-소프트 베이크-현상-하드 베이크-식각-PR 박리-세정'을 거쳐 패턴을 전사 → Al이나 Al-Si를 증착시키고 세정하여 단자를 형성 → 단자를 분리시키기 위해 PR도포",
        "단자 분리를 위해 '소프트 베이크-노광-현상-하드 베이크-알루미늄 식각-PR 박리-세정'과정 진행 \n\n Anneamling 과정 진행 : N well과 금속 전극의 밀착력을 향상시켜 접촉 저항 감소",
        "Anneling 이후 알루미늄이 최상단에 공기중에 노출되어 산화되어 저항이 커짐 \n\n ➡️ Si3N4(실리콘나이트라이드)를 사용한 보호 산화막을 코팅하여 알루미늄 접촉 저항을 감소"
    ]
          # List of image URLs from GitHub
    image_urls = [
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%201.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%202.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%203.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%204.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%205.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%206.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%207.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%208.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%209.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%2010.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%2011.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%2012.png",
        "https://raw.githubusercontent.com/LiCHANHUI/mosfet-images/main/MOSFET%20%EC%82%AC%EC%A7%84%2013.png"

        # Add more URLs...
    ]

     
     

    for i, (url, description) in enumerate(zip(image_urls, descriptions), start=1):
        st.image(url, caption=f"MOSFET 구조 {i}번", use_column_width=True)
        st.markdown(f"**▶** {description}")



# BJT 시뮬레이터
elif st.session_state.selected_device == "BJT":
    st.title("BJT Common-Base Configuration Simulator")

    default_params = {
        "I_S": 1e-14,
        "V_T": 0.026,
        "V_CB_min": 0,
        "V_CB_max": 20,
        "I_E_min": 0.001,
        "I_E_max": 0.005
    }

    # Reset 버튼
    if st.sidebar.button("Reset to Defaults"):
        I_S = default_params["I_S"]
        V_T = default_params["V_T"]
        V_CB_min = default_params["V_CB_min"]
        V_CB_max = default_params["V_CB_max"]
        I_E_min = default_params["I_E_min"]
        I_E_max = default_params["I_E_max"]
    else:
        st.sidebar.header("Adjust Input Characteristics Parameters")
        I_S = st.sidebar.slider("Saturation Current (I_S, A)", 1e-15, 1e-12, default_params["I_S"], format="%.2e")
        V_T = st.sidebar.slider("Thermal Voltage (V_T, V)", 0.01, 0.05, default_params["V_T"], step=0.001)
        V_CB_min = st.sidebar.slider("Min Collector-Base Voltage (V_CB, V)", 0, 20, default_params["V_CB_min"], step=1)
        V_CB_max = st.sidebar.slider("Max Collector-Base Voltage (V_CB, V)", 0, 20, default_params["V_CB_max"], step=1)
        I_E_min = st.sidebar.slider("Min Emitter Current (I_E, A)", 1e-4, 0.01, default_params["I_E_min"], step=1e-4, format="%.4f")
        I_E_max = st.sidebar.slider("Max Emitter Current (I_E, A)", 1e-4, 0.01, default_params["I_E_max"], step=1e-4, format="%.4f")

    col1, col2 = st.columns(2)

    # Input Characteristics
    with col1:
        st.subheader("Input Characteristics")
        fig, ax = plt.subplots()
        V_BE_values = np.linspace(0, 1, 200)
        V_CB_values = np.linspace(V_CB_min, V_CB_max, 3)

        for V_CB in V_CB_values:
            I_E_values = I_S * (np.exp(V_BE_values / V_T) - 1) * (1 + V_CB / (V_CB + V_T))
            ax.plot(V_BE_values, I_E_values * 1e3, label=f"V_CB = {V_CB:.1f} V")

        ax.set_xlabel("V_BE (V)")
        ax.set_ylabel("I_E (mA)")
        ax.set_title("V_BE - I_E Curve")
        ax.legend()
        ax.grid()
        st.pyplot(fig)

    # Output Characteristics
    with col2:
        st.subheader("Output Characteristics")
        fig, ax = plt.subplots()
        V_CB_values = np.linspace(0, 10, 200)
        I_E_values = np.linspace(I_E_min, I_E_max, 3)

        for I_E in I_E_values:
            I_C_values = I_E * (1 - np.exp(-V_CB_values / V_T))
            ax.plot(V_CB_values, I_C_values * 1e3, label=f"I_E = {I_E * 1e3:.1f} mA")

        ax.set_xlabel("V_CB (V)")
        ax.set_ylabel("I_C (mA)")
        ax.set_title("V_CB - I_C Curve")
        ax.legend()
        ax.grid()
        st.pyplot(fig)
