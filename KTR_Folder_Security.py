"""
Copyright (c) 2024 [github.com/Yeonjaeman]
All rights reserved.

This program is licensed under the MIT License.
You may obtain a copy of the License at
https://opensource.org/licenses/MIT

Description:
KTR_Folder_Security is a folder encryption and management tool.
"""

import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet

# 키를 파일에 저장
def save_key(key):
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    os.system('attrib +h +s +r "secret.key"')  # 숨김, 시스템, 읽기 전용 속성 설정

# 키를 파일에서 로드
def load_key():
    if os.path.exists("secret.key"):
        return open("secret.key", "rb").read()
    else:
        key = Fernet.generate_key()
        save_key(key)
        return key

# 암호화 함수
def encrypt(folder_name):
    key = load_key()
    fernet = Fernet(key)
    encrypted_name = fernet.encrypt(folder_name.encode()).decode()
    return encrypted_name

# 복호화 함수
def decrypt(encrypted_name):
    key = load_key()
    fernet = Fernet(key)
    decrypted_name = fernet.decrypt(encrypted_name.encode()).decode()
    return decrypted_name

# folders.json 파일 로드
def load_folders():
    if os.path.exists("folders.json"):
        with open("folders.json", "r") as f:
            return json.load(f)['folders']
    else:
        # 초기 데이터 구조
        data = {"folders": []}
        with open("folders.json", "w") as f:
            json.dump(data, f)
        os.system('attrib +h +s +r "folders.json"')
        return data['folders']

# 비밀번호 유효성 검사
def is_valid_password(password):
    return password.isdigit() and len(password) == 4

# 폴더 생성
def create_folder():
    dialog = tk.Toplevel(root)
    dialog.title("비밀번호 입력")

    set_icon(dialog)

    tk.Label(dialog, text="폴더 이름 입력:").grid(row=0, column=0, padx=10, pady=10)
    folder_name_entry = tk.Entry(dialog)
    folder_name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="비밀번호 입력 (4자리 숫자):").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(dialog, show='*')
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="비밀번호 확인:").grid(row=2, column=0, padx=10, pady=10)
    confirm_password_entry = tk.Entry(dialog, show='*')
    confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

    def on_submit():
        original_name = folder_name_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if original_name and password and is_valid_password(password):
            if password == confirm_password:
                add_folder(original_name, password)
                update_folder_buttons()
                dialog.destroy()
            else:
                messagebox.showerror("오류", "비밀번호가 일치하지 않습니다.")
        else:
            messagebox.showerror("오류", "비밀번호는 4자리 숫자여야 합니다.")

    tk.Button(dialog, text="확인", command=on_submit).grid(row=3, columnspan=2, pady=10)

# 폴더 추가
def add_folder(original_name, password):
    encrypted_name = encrypt(original_name)
    folders.append({
        "original_name": original_name,
        "encrypted_name": encrypted_name,
        "password": password
    })

    # folders.json에 파일 내용 쓰기
    save_folders()

    if not os.path.exists(encrypted_name):
        os.mkdir(encrypted_name)
        os.system(f'attrib +h +s +r "{encrypted_name}"')  # 숨김, 시스템, 읽기 전용 속성 설정

    messagebox.showinfo("성공", f"{original_name} 폴더가 추가되었습니다.")

# 폴더 새로고침
def update_folder_buttons():
    # 기존 버튼 제거
    for button in folder_buttons:
        button.destroy()
    folder_buttons.clear()

    folders = load_folders()

    # 폴더 선택 버튼 생성
    for i, folder in enumerate(folders):
        row = i // 2 + 3
        column = i % 2
        button = tk.Button(root, text=folder['original_name'], image=folder_icon, compound=tk.LEFT, command=lambda i=i: prompt_password(folders, i), width=120)
        button.grid(row=row, column=column, padx=5, pady=5)
        folder_buttons.append(button)

# 비밀번호 입력 프롬프트 창
def prompt_password(folders, choice):
    input_password = simpledialog.askstring("비밀번호 입력", f"{folders[choice]['original_name']}의 비밀번호를 입력하세요:", show='*')
    if input_password:
        check_password(folders, choice, input_password)

# 비밀번호 확인 함수
def check_password(folders, choice, input_password):
    if input_password == folders[choice]['password']:
        encrypted_folder = folders[choice]['encrypted_name']  # 암호화된 폴더 이름
        os.system(f'start "" "{encrypted_folder}"')  # 암호화된 폴더 열기
    else:
        messagebox.showerror("접근 거부", "비밀번호를 다시 입력해주세요.")

# 폴더 삭제 함수
def delete_folder():

    # 폴더 선택 창 생성
    delete_window = tk.Toplevel(root)
    delete_window.title("폴더 삭제")

    # 아이콘 설정
    set_icon(delete_window)

    tk.Label(delete_window, text="삭제할 폴더를 선택하세요", font=("Arial", 12)).pack(pady=10)

    # 리스트 박스 생성
    folder_listbox = tk.Listbox(delete_window, width=50)
    for folder in folders:
        folder_listbox.insert(tk.END, folder['original_name'])
    folder_listbox.pack(pady=10)

    # 비밀번호 입력 및 삭제 확인
    def confirm_delete():
        selected_index = folder_listbox.curselection()
        if selected_index:
            selected_folder = folders[selected_index[0]]

            input_password = simpledialog.askstring("비밀번호 입력", f"{selected_folder['original_name']}의 비밀번호를 입력하세요:",
                                                    show='*')
            if input_password:
                if input_password == selected_folder['password']:
                    if messagebox.askyesno("삭제 확인", f"{selected_folder['original_name']} 폴더를 정말로 삭제하시겠습니까?"):
                        encrypted_name = selected_folder['encrypted_name']
                        try:
                            os.system(f'rmdir /s /q "{encrypted_name}"')  # 폴더 삭제
                            folders.remove(selected_folder)  # 목록에서 삭제
                            save_folders()  # 변경 사항 저장
                            update_folder_buttons()  # 버튼 갱신
                            messagebox.showinfo("삭제 완료", f"{selected_folder['original_name']} 폴더가 삭제되었습니다.")
                            delete_window.destroy() # 삭제 창 닫기
                        except Exception as e:
                            messagebox.showerror("오류", f"폴더 삭제 중 오류가 발생했습니다: {e}")
                else:
                    messagebox.showerror("접근 거부", "비밀번호가 맞지 않습니다.")
        else:
            messagebox.showwarning("선택 오류", "삭제할 폴더를 선택하세요.")

    # 삭제 버튼
    tk.Button(delete_window, text="삭제", command=confirm_delete).pack(pady=10)

# 폴더 목록 저장 함수
def save_folders():
    os.system('attrib -h -s -r "folders.json"')  # 속성 제거
    with open("folders.json", "w") as f:
        json.dump({"folders": folders}, f)
    os.system('attrib +h +s +r "folders.json"')  # 속성 다시 설정

# 아이콘 설정 함수
def set_icon(window):
    window.iconbitmap("favicon.ico")  # 아이콘 파일 경로 설정

# GUI 설정
def open_login():
    global root, folder_icon, folder_buttons, folders

    folders = load_folders()
    root = tk.Tk()
    root.title("KTR Folder Security Program Ver 0.1")

    # 아이콘 설정
    set_icon(root)

    # 폴더 아이콘 로드
    folder_icon = tk.PhotoImage(file="folder_icon.png")

    # 아이콘 크기 조절
    folder_icon = folder_icon.subsample(16)
    
    # 버튼을 저장할 리스트
    folder_buttons = []

    tk.Label(root, text="Option", font=("Arial", 12, "bold"), width=50).grid(row=0, column=0, columnspan=2, pady=10)

    # 폴더 생성 버튼
    tk.Button(root, text="+Create", font=("Arial", 12, "bold"), fg="blue", image=folder_icon, compound=tk.LEFT, command=create_folder, width=120).grid(row=1, column=0, pady=10)

    # 폴더 삭제 버튼
    tk.Button(root, text="-Delete", font=("Arial", 12, "bold"), fg="red", image=folder_icon, compound=tk.LEFT, command=delete_folder, width=120).grid(row=1, column=1, pady=10)

    tk.Label(root, text="Select Folder", font=("Arial", 12, "bold"), width=50).grid(row=2, column=0, columnspan=2, pady=10)

    # 폴더 버튼 생성
    update_folder_buttons()

    # 저작권 표시 레이블 추가
    copyright_label = tk.Label(root, text="Copyright (c) 2024 QAU운영팀 - All rights reserved.", font=("Arial", 8), fg="gray")
    copyright_label.grid(row=100, column=0, columnspan=2, pady=10)

    root.mainloop()

open_login()