import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import re
import time
import telebot

# Token thực của bot
BOT_TOKEN = '7751698576:AAFQloBIbu-CzxZ0k2hiL4qG-x2x7T8857Q' 
bot = telebot.TeleBot(BOT_TOKEN)

# ID của nhóm Telegram
GROUP_ID = -1002174128649

# Hàm để trích xuất thông tin sản phẩm từ trang web
def scrape_website():
    main_url = url_entry.get()
    
    try:
        # Tìm tất cả các liên kết sản phẩm từ trang chính
        product_links = get_product_links(main_url)
        
        if not product_links:
            messagebox.showinfo("Thông báo", "Không tìm thấy liên kết sản phẩm nào.")
            return
        
        # Chuẩn bị file để lưu kết quả
        with open("product_features.txt", 'w', encoding='utf-8') as file:
            file.write(f"Tổng hợp thông tin sản phẩm từ {main_url}\n\n")
        
        # Cập nhật thanh tiến trình
        progress['maximum'] = len(product_links)
        
        # Trích xuất thông tin từ từng trang sản phẩm
        for i, link in enumerate(product_links, 1):
            features = scrape_product_page(link)
            if features:
                save_to_txt(features, link)
            
            # Cập nhật thanh tiến trình và phần trăm
            progress['value'] = i
            percent.set(f"{i/len(product_links)*100:.1f}%")
            update_log(f"Đã xử lý {i}/{len(product_links)} sản phẩm")
            root.update_idletasks()
            time.sleep(0.1)  # Tránh quá tải server
        
        messagebox.showinfo("Thành công", f"Đã trích xuất thông tin từ {len(product_links)} sản phẩm.")
    except requests.RequestException as e:
        messagebox.showerror("Lỗi", f"Không thể tải trang. Lỗi: {str(e)}")

def get_product_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'/product/'))
    return ['https://www.geovision.com.tw' + link['href'] for link in links]

def scrape_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    feature_list = soup.find('ul', class_='rows')
    
    if feature_list:
        return [feature.text.strip() for feature in feature_list.find_all('li')]
    return None

def save_to_txt(features, url):
    with open("product_features.txt", 'a', encoding='utf-8') as file:
        file.write(f"\nURL: {url}\n")
        for feature in features:
            file.write(feature + '\n')
        file.write('\n' + '-'*50 + '\n')

# Giao diện người dùng Tkinter
root = tk.Tk()
root.title("Trích xuất thông tin sản phẩm")
root.geometry("500x350")

# URL input
url_label = ttk.Label(root, text="URL trang tổng hợp sản phẩm:")
url_label.pack(pady=5)
url_entry = ttk.Entry(root, width=50)
url_entry.pack()

# Scrape button
scrape_button = ttk.Button(root, text="Trích xuất thông tin", command=scrape_website)
scrape_button.pack(pady=10)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=5)

# Percent label
percent = tk.StringVar()
percent_label = ttk.Label(root, textvariable=percent)
percent_label.pack()

# Log area
log_label = ttk.Label(root, text="Tiến trình:")
log_label.pack()
log_area = scrolledtext.ScrolledText(root, width=60, height=10)
log_area.pack(pady=5)

def update_log(message):
    log_area.insert(tk.END, message + '\n')
    log_area.see(tk.END)
    root.update_idletasks()

# Telegram bot handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Chào mừng đến với GeoVision Product Bot! Gửi cho tôi mã sản phẩm GeoVision để nhận thông tin chi tiết.")

@bot.message_handler(func=lambda message: True)
def get_product_info(message):
    product_code = message.text.strip()
    product_url = f"https://www.geovision.com.tw/product/{product_code}"
    
    try:
        features = scrape_product_page(product_url)
        if features:
            response = f"Thông tin sản phẩm {product_code}:\n\n"
            for feature in features:
                response += f"• {feature}\n"
        else:
            response = f"Không tìm thấy thông tin cho sản phẩm {product_code}. Vui lòng kiểm tra lại mã sản phẩm."
    except requests.RequestException:
        response = "Xin lỗi, không thể tải thông tin sản phẩm. Vui lòng thử lại sau."
    
    # Gửi phản hồi vào nhóm có ID GROUP_ID
    bot.send_message(GROUP_ID, response)

if __name__ == "__main__":
    # Chạy cả giao diện Tkinter và bot Telegram
    print("Bot đang chạy...")
    bot.polling(none_stop=True)
    root.mainloop()
