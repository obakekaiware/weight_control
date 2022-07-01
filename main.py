from collections import UserDict
import os
import shutil
import pyminizip
import zipfile
import json
import time

import streamlit as st
import pandas as pd
import json


def regist_user(name, password):
    user_dir = os.path.join("data", name)
    if name == "":
        st.write("名前を入力してください。")
    elif os.path.exists(user_dir):
        st.write((
            f"'{name}' は既に使われています。"
            "別の名前にしてください。"
        ))
    elif password == "":
        st.write("パスワードを入力してください。")
    else:
        os.makedirs(user_dir)
        pyminizip.compress(
            "password.txt".encode('cp932'),
            "", 
            os.path.join(user_dir, "password.zip").encode('cp932'),
            password.encode('cp932'), 
            1
        )
        st.write("登録完了！")


def sign_up():
    with st.form("初回登録"):
        name = st.text_input("名前")
        password = st.text_input("パスワード")
        submitted = st.form_submit_button("登録")
        if submitted:
            regist_user(name, password)


def confirm_name(name):
    user_dir = os.path.join("data", name)
    return os.path.exists(user_dir)


def confirm_password(name, password):
    user_dir = os.path.join("data", name)
    password_zip_path = os.path.join(user_dir, "password.zip")
    try:
        pyminizip.uncompress(
            password_zip_path.encode('cp932'),
            password.encode('cp932'),
            "",
            0
        )
    except Exception:
        # パスワード認証失敗
        return False
    # パスワード認証成功
    return True


def confirm_user(name, password):
    if name == "":
        st.write("名前を入力してください。")
        return False
    elif not confirm_name(name):
        st.write("名前が登録されていません。")
        return False
    elif password == "":
        st.write("パスワードを入力してください。")
        return False
    elif not confirm_password(name, password):
        st.write("パスワードが違います。")
        return False
    return True


def sign_in():
    st.subheader("ログイン")
    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False

    with st.form("ログイン"):
        name = st.text_input("名前")
        password = st.text_input("パスワード")
        submitted = st.form_submit_button("ログイン")
        if submitted:
            if confirm_user(name, password):
                st.session_state.signed_in = True
                st.write("ログインしました。")
            else:
                st.write("ログインできませんでした。")
    return name, password


def compress_weight_file(weight_csv_path, weight_zip_path, password):
    pyminizip.compress(
        weight_csv_path.encode('cp932'),
        "",
        weight_zip_path.encode('cp932'),
        password.encode('cp932'),
        1
    )
    os.remove(weight_csv_path)


def uncompress_weight_file(weight_zip_path, password):
    if os.path.exists(weight_zip_path):
        user_dir = os.path.dirname(weight_zip_path)
        pyminizip.uncompress(
            weight_zip_path.encode('cp932'),
            password.encode('cp932'),
            user_dir.encode('cp932'),
            0
        )
        os.chdir(os.path.join("..", ".."))
    else:
        weight_df = pd.DataFrame(columns=["日にち", "体重"])
        weight_csv_path = os.path.join("data", name, "weight.csv")
        weight_df.to_csv(weight_csv_path)


def regist_weight(weight_csv_path):
    st.subheader("体重の入力")
    with st.form("体重の入力"):
        date = st.date_input("日にち")

        weight_df = pd.read_csv(
            weight_csv_path, index_col="日にち", parse_dates=True)

        if len(weight_df):
            weight_init = weight_df.iloc[-1, 0]
        else:
            weight_init = 50.0
        weight = st.number_input(
            "体重", value=weight_init, format="%.1f", step=0.1)

        if len(weight_df):
            goal_init = weight_df.iloc[0, 1]
        else:
            goal_init = 50.0
        goal = st.number_input(
            "目標", value=goal_init, format="%.1f", step=0.1)

        submitted = st.form_submit_button("登録")
        if submitted:
            weight_df.loc[date, "体重"] = weight
            weight_df["目標"] = goal
            weight_df = weight_df[["体重", "目標"]]
            weight_df.to_csv(weight_csv_path)
            st.write("登録完了！")


def plot_weight(weight_csv_path):
    weight_df = pd.read_csv(weight_csv_path)
    if len(weight_df) > 0:
        weight_df = pd.read_csv(
            weight_csv_path, index_col='日にち', parse_dates=True)
        st.line_chart(weight_df)


def delete_account():
    if "first_confirmation" not in st.session_state:
        st.session_state.first_confirmation = False

    with st.form("アカウントの削除"):
        name = st.text_input("名前")
        password = st.text_input("パスワード")
        submitted = st.form_submit_button("削除")
        if submitted:
            if confirm_user(name, password):
                st.session_state.first_confirmation = True

    if st.session_state.first_confirmation:
        with st.form("再確認"):
            st.write("きれいさっぱり消してしまっても大丈夫ですか？")
            submitted = st.form_submit_button("はい")
            if submitted:
                shutil.rmtree(os.path.join("data", name))
                st.write("アカウントはきれいさっぱり消えました。")


if __name__ == "__main__":
    st.title("ポッドキャストゆるダイエット部")
    st.write("ゆるく体重管理などをしていくアプリです。")
    os.makedirs("data", exist_ok=True)
    # 空のzipファイルを作成し、今後パスワード確認に使う。
    with open("password.txt", "w") as file:
        file.write((
            "これをパスワード付きzipファイルに変換し、"
            "今後パスワード確認に使う。"
        ))

    with st.expander("初回登録はこちら"):
        sign_up()

    name, password = sign_in()

    if st.session_state.signed_in == True:
        weight_csv_path = os.path.join("data", name, "weight.csv")
        weight_zip_path = os.path.join("data", name, "weight.zip")
        uncompress_weight_file(weight_zip_path, password)
        regist_weight(weight_csv_path)
        plot_weight(weight_csv_path)
        compress_weight_file(weight_csv_path, weight_zip_path, password)
        
    with st.expander("アカウントの削除"):
        delete_account()
