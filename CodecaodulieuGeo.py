import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog

# Hàm để lấy thông tin sản phẩm và lưu vào file Excel
def scrape_and_save(url):
    try:
        # Gửi yêu cầu đến trang chính để lấy danh sách các sản phẩm
        response = requests.get(url)
        response.encoding = 'utf-8'
        html_content = response.text

        # Phân tích HTML của trang chính
        soup = BeautifulSoup(html_content, "html.parser")

        # Lấy tất cả các liên kết đến các trang sản phẩm
        product_links = []
        
        # Lớp chứa các liên kết sản phẩm
        products = soup.find_all('a', class_='product-title')  # Kiểm tra lớp này

        if not products:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy sản phẩm nào! Vui lòng kiểm tra lại cấu trúc HTML.")
            return

        for product in products:
            product_url = product['href']
            if not product_url.startswith("http"):
                product_url = "https://www.geovision.com.tw" + product_url
            product_links.append(product_url)

        # In ra số lượng liên kết sản phẩm để kiểm tra
        print(f"Đã tìm thấy {len(product_links)} sản phẩm.")

        # Truy cập từng trang sản phẩm và lấy thông tin
        product_data = []

        for product_url in product_links:
            response = requests.get(product_url)
            response.encoding = 'utf-8'
            product_html = response.text
            product_soup = BeautifulSoup(product_html, "html.parser")
            
            # Lấy tên sản phẩm
            product_name = product_soup.find('h1', class_='product-title').get_text(strip=True)
            
            # Lấy mô tả kỹ thuật
            specifications = product_soup.find('div', class_='product-specs')  # Lớp chứa thông số kỹ thuật
            spec_details = []
            
            if specifications:
                for spec in specifications.find_all('li'):
                    spec_details.append(spec.get_text(strip=True))

            # In ra để kiểm tra thông tin sản phẩm
            print(f"Product: {product_name}, Specs: {spec_details}")
            
            # Lưu thông tin sản phẩm vào danh sách
            product_data.append({
                "Product Name": product_name,
                "Specifications": "\n".join(spec_details)
            })

        # Lưu dữ liệu vào file Excel
        if product_data:
            df = pd.DataFrame(product_data)
            df.to_excel("geovision_all_products.xlsx", index=False)
            messagebox.showinfo("Thành công", "Dữ liệu đã được lưu vào geovision_all_products.xlsx")
        else:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu sản phẩm để lưu.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

# Hàm xử lý nút bấm bắt đầu
def on_start_button_click():
    url = simpledialog.askstring("Nhập URL", "Vui lòng nhập đường dẫn web:")
    if url:
        scrape_and_save(url)

# Tạo giao diện bằng Tkinter
def create_gui():
    window = tk.Tk()
    window.title("GeoVision Scraper")
    
    # Tạo nút bấm để thực hiện việc lấy dữ liệu
    scrape_button = tk.Button(window, text="Bắt đầu lấy dữ liệu", command=on_start_button_click, width=30, height=2)
    scrape_button.pack(pady=20)
    
    window.mainloop()

# Chạy giao diện
if __name__ == "__main__":
    create_gui()
