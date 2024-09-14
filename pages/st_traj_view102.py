import streamlit as st
from ase.io import read
import py3Dmol
import tempfile
import os
import time

# タイトル
st.title("Trajectory Viewer with py3Dmol")

# カメラの設定を保存する変数
if "angle_x" not in st.session_state:
    st.session_state.angle_x = -90
if "angle_y" not in st.session_state:
    st.session_state.angle_y = 0
if "angle_z" not in st.session_state:
    st.session_state.angle_z = 0
if "zoom" not in st.session_state:
    st.session_state.zoom = 0.4
if "translate_x" not in st.session_state:
    st.session_state.translate_x = -70.0
if "translate_y" not in st.session_state:
    st.session_state.translate_y = -170.0
if "translate_z" not in st.session_state:
    st.session_state.translate_z = 0.0
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "style" not in st.session_state:
    st.session_state.style = 'stick'  # デフォルトのスタイルを'stick'に設定
if "playing" not in st.session_state:
    st.session_state.playing = False  # 再生中かどうかを管理

# Trajectoryファイルのアップロード
st.subheader("Upload Trajectory File")
uploaded_file = st.file_uploader("Choose a Trajectory file", type=["traj", "xyz"])

if uploaded_file is not None:
    # アップロードされたファイルを読み込む
    trajectory = read(uploaded_file, index=':')
    st.write(f"Loaded {len(trajectory)} frames from the trajectory.")

    # レイアウトを設定する
    col1, col2 = st.columns([3, 1])  # 3:1の比率でカラムを設定

    with col1:
        # Trajectoryフレームをpy3Dmolで3D表示
        frame = st.slider("Select Frame", 0, len(trajectory) - 1, st.session_state.frame)
        selected_atoms = trajectory[frame]
        
        # 選択したフレームをXYZ形式で一時ファイルに書き出し
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_traj_xyz:
            selected_atoms.write(tmp_traj_xyz.name)
            traj_xyz_file = tmp_traj_xyz.name

        # Trajectoryフレームをpy3Dmolで3D表示
        with open(traj_xyz_file, 'r') as f_traj:
            traj_xyz_data = f_traj.read()

        view_traj = py3Dmol.view(width=500, height=600)
        view_traj.addModel(traj_xyz_data, 'xyz')
        
        # ユーザーが選択したスタイルを反映
        if st.session_state.style == 'stick':
            view_traj.setStyle({'stick': {}})
        elif st.session_state.style == 'sphere':
            view_traj.setStyle({'sphere': {}})

        # カメラの角度とズームを設定
        view_traj.rotate(st.session_state.angle_x, 'x')
        view_traj.rotate(st.session_state.angle_y, 'y')
        view_traj.rotate(st.session_state.angle_z, 'z')
        view_traj.zoom(st.session_state.zoom)

        # カメラの並行移動を設定
        view_traj.translate(st.session_state.translate_x, st.session_state.translate_y, st.session_state.translate_z)

        # 3DビューをHTMLとして表示
        view_traj_html = view_traj._make_html()
        st.components.v1.html(view_traj_html, height=600, scrolling=True)

        # 一時ファイルの削除
        os.remove(traj_xyz_file)

    with col2:
        # スタイルの選択
        st.session_state.style = st.radio(
            "Select Visualization Style",
            options=['stick', 'sphere'],
            index=0 if st.session_state.style == 'stick' else 1
        )

        # フォームで表示角度と位置を指定
        with st.form(key='camera_form', clear_on_submit=True):
            st.write("Set the view parameters:")
            col1, col2 = st.columns([1, 1])
            with col1:
                angle_x = st.number_input("Rotate X", min_value=-180, max_value=180, value=st.session_state.angle_x, key="angle_x")
                angle_y = st.number_input("Rotate Y", min_value=-180, max_value=180, value=st.session_state.angle_y, key="angle_y")
                angle_z = st.number_input("Rotate Z", min_value=-180, max_value=180, value=st.session_state.angle_z, key="angle_z")
            with col2:
                zoom = st.number_input("Zoom", min_value=0.1, max_value=10.0, value=st.session_state.zoom, key="zoom")
                translate_x = st.number_input("Translate X", value=st.session_state.translate_x, key="translate_x")
                translate_y = st.number_input("Translate Y", value=st.session_state.translate_y, key="translate_y")
                translate_z = st.number_input("Translate Z", value=st.session_state.translate_z, key="translate_z")
            submit_button = st.form_submit_button("Apply")

            if submit_button:
                # フォームで指定された角度、ズーム、並行移動を保存
                st.session_state.angle_x = angle_x
                st.session_state.angle_y = angle_y
                st.session_state.angle_z = angle_z
                st.session_state.zoom = zoom
                st.session_state.translate_x = translate_x
                st.session_state.translate_y = translate_y
                st.session_state.translate_z = translate_z

        # フレームを1つずつ増加させるボタン
        if st.button("Next Frame"):
            if st.session_state.frame < len(trajectory) - 1:
                st.session_state.frame += 1
            else:
                st.session_state.frame = 0  # ループして最初のフレームに戻る

        # フレームを連続再生するPlayボタン
        if st.button("Play"):
            st.session_state.playing = True

        # 停止ボタン
        if st.button("Stop"):
            st.session_state.playing = False

        # フレームが連続的に増加する処理
        if st.session_state.playing:
            if st.session_state.frame < len(trajectory) - 1:
                st.session_state.frame += 1
            else:
                st.session_state.frame = 0  # 最後のフレームに到達したら最初に戻る
            time.sleep(0.2)  # 0.2秒ごとにフレームを更新
            st.rerun()  # フレームを更新して再レンダリング

    # フレームの状態を更新
    frame = st.session_state.frame
