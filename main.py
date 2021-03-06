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
        password = st.text_input("パスワード", type="password")
        password_ = st.text_input("パスワード（確認用）", type="password")
        submitted = st.form_submit_button("登録")
        if submitted:
            if password == password_:
                regist_user(name, password)
            else:
                st.write("パスワードが一致しません。")


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
    elif password == "":
        st.write("パスワードを入力してください。")
        return False
    elif not (confirm_name(name) and confirm_password(name, password)):
        st.write("名前またはパスワードが違います。")
        return False
    return True


def sign_in():
    st.subheader("ログイン")
    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False

    with st.form("ログイン"):
        name = st.text_input("名前")
        password = st.text_input("パスワード", type="password")
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


def calc_standard_calorie(sex, age, activity_level, standard_weight):
    calorie_df = pd.read_csv("calorie.csv", encoding="shift-jis")
    if 18 <= age < 30:
        age_id = 0
    elif 30 <= age < 50:
        age_id = 1
    elif 50 <= age < 65:
        age_id = 2
    elif 65 <= age < 75:
        age_id = 3
    elif 75 <= age:
        age_id = 4
    else:
        st.write("18歳未満には標準カロリーの計算は対応していません。")
        return 0

    if (sex == "男") and (activity_level == "低い（あまり動かない）"):
        standard_calorie = calorie_df.loc[age_id, "m1"] * standard_weight
    elif (sex == "男") and (activity_level == "ふつう（まあまあ動く）"):
        standard_calorie = calorie_df.loc[age_id, "m2"] * standard_weight
    elif (sex == "男") and (activity_level == "高い（かなり動く）"):
        standard_calorie = calorie_df.loc[age_id, "m3"] * standard_weight
    elif (sex == "女") and (activity_level == "低い（あまり動かない）"):
        standard_calorie = calorie_df.loc[age_id, "f1"] * standard_weight
    elif (sex == "女") and (activity_level == "ふつう（まあまあ動く）"):
        standard_calorie = calorie_df.loc[age_id, "f2"] * standard_weight
    elif (sex == "女") and (activity_level == "高い（かなり動く）"):
        standard_calorie = calorie_df.loc[age_id, "f3"] * standard_weight

    return standard_calorie


def estimate_goal():
    with st.form("標準体重の計算"):
        st.write("標準体重と標準カロリーを計算します。")
        sex = st.radio("性別", ("男", "女"))
        height = st.number_input("身長(cm)", value=160, step=1)
        age = st.number_input("年齢", value=18, step=1)
        activity_level = st.radio(
            "身体活動レベル",
            (
                "低い（あまり動かない）",
                "ふつう（まあまあ動く）",
                "高い（かなり動く）",
            ))
        submitted = st.form_submit_button("決定")
        if submitted:
            standard_weight = 22 * (height/100)**2
            st.write("あなたの標準体重：", str(round(standard_weight, 1)), "kg")
            standard_calorie = calc_standard_calorie(
                sex, age, activity_level, standard_weight)
            if standard_calorie:
                st.write(
                    "標準摂取カロリー：",
                    str(round(standard_calorie)), "kcal")
            st.caption((
                "標準体重は、BMIが22となる体重のことで、"
                "最も病気になりにくい体重と言われています。"
            ))
            st.caption((
                "標準摂取カロリーは、標準体重を目指す上での1日の"
                "必要摂取カロリーのことです。"
            ))


def reset_name():
    with st.form("名前の変更"):
        old_name = st.text_input("現在の名前")
        new_name = st.text_input("新しい名前")
        password = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("変更")
        if submitted:
            if new_name == "":
                st.write("新しい名前を入力してください。")
            elif confirm_user(old_name, password):
                old_name = os.path.join("data", old_name)
                new_name = os.path.join("data", new_name)
                os.rename(old_name, new_name)
                st.write("名前を変更しました。")


def reset_password():
    with st.form("パスワードの変更"):
        name = st.text_input("名前")
        old_password = st.text_input("現在のパスワード", type="password")
        new_password = st.text_input("新しいパスワード", type="password")
        new_password_ = st.text_input(
            "新しいパスワード（確認用）", type="password")
        submitted = st.form_submit_button("変更")
        if submitted:
            if new_password == "":
                st.write("新しいパスワードを入力してください。")
            elif new_password != new_password_:
                st.write("新しいパスワードが一致しません。")
            elif confirm_user(name, old_password):
                password_zip_path = os.path.join("data", name, "password.zip")
                pyminizip.compress(
                    "password.txt".encode('cp932'),
                    "", 
                    password_zip_path.encode('cp932'),
                    new_password.encode('cp932'), 
                    1
                )
                st.write("パスワードを変更しました。")


def delete_account():
    if "first_confirmation" not in st.session_state:
        st.session_state.first_confirmation = False

    with st.form("アカウントの削除"):
        name = st.text_input("名前")
        password = st.text_input("パスワード", type="password")
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
        
    st.subheader("標準体重の計算")
    estimate_goal()

    st.subheader("アカウントの操作")
    with st.expander("名前の変更"):
        reset_name()
    with st.expander("パスワードの変更"):
        reset_password()
    with st.expander("アカウントの削除"):
        delete_account()
