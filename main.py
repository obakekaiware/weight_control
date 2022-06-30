from collections import UserDict
import os
import shutil
import pyminizip
import zipfile
import json

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
            "password.txt",
            "", 
            os.path.join(user_dir, "password.zip"),
            password, 
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
        pyminizip.uncompress(password_zip_path, password, "", 0)
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
    with st.form("ログイン"):
        name = st.text_input("名前")
        password = st.text_input("パスワード")
        submitted = st.form_submit_button("ログイン")
        if submitted:
            if confirm_user(name, password):
                st.write("ログインしました。")
            else:
                st.write("ログインできませんでした。")
    return name, password


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



    #         path = os.path.join("data", name, "weight.csv")
    #     if os.path.exists(path):
    #             weight_df = pd.read_csv(path)
    #         else:
    #             weight_df = pd.DataFrame(columns=["weight"], index=[today])

    # path = os.path.join("data", "kaiware", "weight.csv")
    # if os.path.exists(path):
    #     weight_df = pd.read_csv(path, index_col='date', parse_dates=True)
    # else:
    #     weight_df = pd.DataFrame(columns=["date", "体重", "目標"])
    #     weight_df['date'] = pd.to_datetime(weight_df['date'])
    #     weight_df = weight_df.set_index("date")

    # with st.form("体重入力"):
    #     date = st.date_input("日にち")

    #     if len(weight_df):
    #         weight_init = weight_df.iloc[-1, 0]
    #     else:
    #         weight_init = 50.0
    #     weight = st.number_input(
    #         "体重", value=weight_init, format="%.1f", step=0.1)

    #     if len(weight_df):
    #         goal_init = weight_df.iloc[0, 1]
    #     else:
    #         goal_init = 50.0
    #     goal = st.number_input(
    #         "目標", value=goal_init, format="%.1f", step=0.1)

    #     submitted = st.form_submit_button("登録")
    #     if submitted:
    #         st.write("登録完了！")
    #         weight_df.loc[date, "体重"] = weight
    #         weight_df["目標"] = goal
    #         weight_df.to_csv(path)

    #         weight_df = pd.read_csv(path, index_col='date', parse_dates=True)
    #         st.dataframe(weight_df)
    #         # st.line_chart(weight_df.rename(
    #         #     columns={"date": "index"}).set_index("index"))
    #         st.line_chart(weight_df, width=1)



    # clicked = st.button("Initialize")
    # if clicked:
    #     weight_df = pd.read_csv(path)
    #     weight_df = pd.DataFrame(columns=["date", "体重", "目標"])
    #     weight_df['date'] = pd.to_datetime(weight_df['date'])
    #     weight_df = weight_df.set_index("date")
    #     weight_df.to_csv(path)

    with st.expander("アカウントの削除"):
        delete_account()
