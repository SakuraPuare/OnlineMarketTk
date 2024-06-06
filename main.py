import asyncio
import json
import os
import pickle
import sys
import tkinter as tk
from io import BytesIO
from tkinter import filedialog, font, messagebox, ttk

import httpx
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from tqdm import tqdm


class Product:
    def __init__(self, name, price, image=None):
        self.name = name
        self.price = price
        self.image = image

    def __repr__(self):
        return f"<Goods {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cart = []
        self.role = "user"

    def __eq__(self, value: object) -> bool:
        return self.username == value.username

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def add_to_cart(self, product):
        self.cart.append(product)

    def checkout(self):
        total_amount = sum(float(item.price) for item in self.cart)
        self.cart = []
        return total_amount


class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.role = "admin"


users: list[User] = []  # 用户数据：username -> password
products: list[Product] = []  # 商品数据：[{id, title, price, image_path}, ...]


FONT_SIZE = 14
if 'linux' in sys.platform:
    FONT_SIZE = 16  # 更大的字体适配 Linux


async def load_image_async(image_url):
    async with httpx.AsyncClient() as client:
        response = await client.get('http://img13.360buyimg.com/n1/' + image_url)
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        img_width, img_height = image.size
        new_width = min(100, img_width)
        new_height = int((new_width / img_width) * img_height)
        image = image.resize((new_width, new_height))
        return image


async def get_product_data(keyword):
    url = f'https://re.jd.com/search?keyword={keyword}&enc=utf-8'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script', type='text/javascript')

        if response.status_code == 200:
            data = scripts[1].text.strip().split('var pageData = ')[-1][:-1]
            return json.loads(data).get('result', [])
        else:
            messagebox.showerror(
                "错误", f"{response.status_code}, 无法获取数据")
            return []


# 保存和加载数据的帮助函数
def init_data():
    global users, products
    if not os.path.exists('data.pkl'):
        users = [User("admin", "admin")]
        save_data()


def save_data():
    with open('data.pkl', 'wb') as f:
        pickle.dump((users, products), f)


def load_data():
    global users, products
    if os.path.exists('data.pkl'):
        with open('data.pkl', 'rb') as f:
            users, products = pickle.load(f)
            pass


init_data()


class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="思源黑体",
                                    size=FONT_SIZE)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack()

        self.username = tk.Entry(
            self.login_frame, width=30, font=self.default_font)
        self.username.grid(row=0, column=1, padx=5, pady=5)
        self.password = tk.Entry(
            self.login_frame, width=30, show='*', font=self.default_font)
        self.password.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="用户名：").grid(
            row=0, column=0, padx=5, pady=5)
        tk.Label(self.login_frame, text="密码：").grid(
            row=1, column=0, padx=5, pady=5)

        button_label = tk.Label(self.login_frame)
        button_label.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        login_button = tk.Button(
            button_label, text="登录", command=self.login)
        login_button.pack(side="left", padx=5, pady=5)

        register_button = tk.Button(
            button_label, text="注册", command=self.register)
        register_button.pack(side="left", padx=5, pady=5)

    def login(self):
        username = self.username.get()
        password = self.password.get()
        user = User(username, password)
        for u in users:
            if u == user and u.password == user.password:
                if username == "admin":
                    self.master.switch_frame(AdminPanel, u)
                else:
                    self.master.switch_frame(UserPanel, u)
                return
        else:
            messagebox.showerror("错误", "用户名或密码错误", parent=self)

    def register(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        # sanity check
        if not username or not password:
            messagebox.showerror("错误", "用户名或密码不能为空", parent=self)
            return
        user = User(username, password)

        if user not in users:
            users.append(user)
            save_data()
            messagebox.showinfo("提示", "注册成功", parent=self)
        else:
            messagebox.showerror("错误", "用户名已存在", parent=self)


class UserPanel(tk.Frame):
    def __init__(self, master=None, user=None):
        super().__init__(master)
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="思源黑体",
                                    size=FONT_SIZE)
        self.master = master
        self.user: User = user
        self.pack()
        self.create_widgets()

        self.selected_panel = None
        self.refresh_product_list()

    def create_widgets(self):
        button_label = tk.Label(self)
        button_label.pack()

        self.add_to_cart_btn = tk.Button(
            button_label, text="添加至购物车", command=self.add_to_cart)
        self.add_to_cart_btn.pack(side="left", padx=5, pady=5)

        self.show_cart_btn = tk.Button(
            button_label, text="查看购物车", command=self.show_cart)
        self.show_cart_btn.pack(side="left", padx=5, pady=5)

        self.clear_cart_btn = tk.Button(
            button_label, text="清空购物车", command=self.clear_cart)
        self.clear_cart_btn.pack(side="left", padx=5, pady=5)

        self.checkout_btn = tk.Button(
            button_label, text="结算", command=self.checkout)
        self.checkout_btn.pack(side="left", padx=5, pady=5)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
            add='+'
        )

        # bottom
        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add this line to occupy full width and height
        self.pack(fill="both", expand=True)

        # Bind mouse wheel to scroll the canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def save_data(self):
        users[users.index(self.user)] = self.user
        save_data()

    def show_cart(self):
        if not self.user.cart:
            messagebox.showwarning("警告", "购物车为空", parent=self)
            return

        cart_items = "\n".join(
            [f"{item.name} - 价格: ¥{item.price}" for item in self.user.cart])
        messagebox.showinfo("购物车", cart_items, parent=self)

    def add_to_cart(self):
        if hasattr(self, 'selected_product') and self.selected_product:
            self.user.add_to_cart(self.selected_product)
            self.save_data()
            messagebox.showinfo(
                "提示", f"{self.selected_product.name} 已添加至购物车", parent=self)
        else:
            messagebox.showwarning("警告", "请选择一个商品", parent=self)

    def clear_cart(self):
        self.user.cart.clear()
        self.save_data()
        messagebox.showinfo("提示", "购物车已清空", parent=self)

    def checkout(self):
        if not self.user.cart:
            messagebox.showwarning("警告", "购物车为空", parent=self)
            return

        total_amount = self.user.checkout()
        messagebox.showinfo("合计", f"总金额：￥{total_amount}", parent=self)
        self.save_data()

    def refresh_product_list(self):
        row = 0
        for product in products:
            photo = ImageTk.PhotoImage(product.image)

            self.frame = tk.Frame(self.scrollable_frame,
                                  borderwidth=2, relief="groove")
            self.frame.grid(row=row, column=0, padx=10,
                            pady=10, columnspan=4, sticky="we")

            panel = tk.Label(self.frame, image=photo)
            panel.image = photo  # keep a reference to avoid garbage collection
            panel.grid(row=0, column=0, padx=10, pady=10)
            panel.bind("<Button-1>", lambda event, p=product,
                       f=self.frame: self.select_product(p, f))

            name_label = tk.Label(self.frame, text=product.name, wraplength=620,
                                  font=('Arial', FONT_SIZE))
            name_label.grid(row=0, column=1, sticky='w', columnspan=2)
            name_label.bind("<Button-1>", lambda event, p=product,
                            f=self.frame: self.select_product(p, f))

            price_label = tk.Label(self.frame, text=f"价格: ¥{product.price}", font=(
                'Arial', FONT_SIZE))
            price_label.grid(row=0, column=3, sticky='e')
            price_label.bind("<Button-1>", lambda event,
                             p=product, f=self.frame: self.select_product(p, f))

            row += 1

    def select_product(self, product, frame):
        if self.selected_panel is not None:
            # Reset the previous selected panel's background
            self.selected_panel.config(bg="white")

        self.selected_product = product
        self.selected_panel = frame
        # Highlight the selected panel
        self.selected_panel.config(bg="lightblue")

        print(f"Selected product: {product.name}")


class AdminPanel(tk.Frame):
    def __init__(self, master=None, user=None):
        super().__init__(master)
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="思源黑体",
                                    size=FONT_SIZE)
        self.master = master
        self.user = user
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.admin_notebook = ttk.Notebook(self)
        self.admin_notebook.pack(padx=5, pady=5)

        # 用户管理
        self.user_frame = tk.Frame(self.admin_notebook)
        self.admin_notebook.add(self.user_frame, text="用户管理")

        # 显示用户列表：
        self.user_list = tk.Listbox(self.user_frame)
        self.user_list.pack(padx=5, pady=5)
        self.refresh_user_list()

        self.add_user_btn = tk.Button(
            self.user_frame, text="添加用户", command=self.create_user_window)
        self.add_user_btn.pack(padx=5, pady=5)

        self.del_user_btn = tk.Button(
            self.user_frame, text="删除用户", command=self.delete_user)
        self.del_user_btn.pack(padx=5, pady=5)

        # 商品管理
        self.product_frame = tk.Frame(self.admin_notebook)
        self.admin_notebook.add(self.product_frame, text="商品管理")

        self.title_entry = tk.Entry(
            self.product_frame, width=30, font=self.default_font)
        self.title_entry.grid(row=0, column=1, padx=5,
                              pady=5, sticky="nsew", columnspan=2)
        self.price_entry = tk.Entry(
            self.product_frame, width=30, font=self.default_font)
        self.price_entry.grid(row=1, column=1, padx=5,
                              pady=5, sticky="nsew", columnspan=2)
        self.image_path = ""

        tk.Label(self.product_frame, text="标题：").grid(
            row=0, column=0, padx=5, pady=5)
        tk.Label(self.product_frame, text="价格：").grid(
            row=1, column=0, padx=5, pady=5)

        button_label = tk.Label(self.product_frame)
        button_label.grid(row=2, column=0, columnspan=3,
                          padx=5, pady=5, sticky="nsew")

        self.add_product_btn = tk.Button(
            button_label, text="添加商品", command=self.add_product)
        self.add_product_btn.pack(side="left", padx=5, pady=5)

        self.del_product_btn = tk.Button(
            button_label, text="删除商品", command=self.delete_product)
        self.del_product_btn.pack(side="left", padx=5, pady=5)

        self.clear_product_btn = tk.Button(
            button_label, text="清空商品", command=self.clear_product)
        self.clear_product_btn.pack(side="left", padx=5, pady=5)

        self.search_button = tk.Button(
            button_label, text="搜索", command=self.create_search_window)
        self.search_button.pack(side="left", padx=5, pady=5)

        # Center the button label
        button_label.grid_columnconfigure(0, weight=1)

        self.product_list = tk.Listbox(self.product_frame, width=50, height=20)
        self.product_list.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self.refresh_product_list()

    def clear_product(self):
        products.clear()
        self.refresh_product_list()
        save_data()

    def close_search_window(self):
        self.search_window.destroy()

    def create_search_window(self):
        self.search_window = tk.Toplevel(self)
        self.search_window.title("搜索商品")
        self.search_window.geometry("800x400")
        self.search_window.protocol(
            "WM_DELETE_WINDOW", self.close_search_window)

        self.search_label = tk.Label(self.search_window, text="关键字：")
        self.search_label.pack(padx=5, pady=5)
        self.search_entry = tk.Entry(
            self.search_window, font=self.default_font)
        self.search_entry.pack(padx=5, pady=5)

        self.search_button = tk.Button(
            self.search_window, text="搜索", command=self.search_product)
        self.search_button.pack(padx=5, pady=5)

        self.refresh_product_list()

    def search_product(self):
        asyncio.run(self.search_product_())

    async def search_product_(self):
        keyword = self.search_entry.get().strip()
        if keyword:
            try:
                data = await get_product_data(keyword)
                url = [i.get('image_url', None) for i in data]
                title = [i.get('ad_title_text', None) for i in data if i]
                price = [i.get('price', None) or i.get(
                    'sku_price') or 0 for i in data if i]
                tasks = [asyncio.create_task(load_image_async(i)) for i in url]
                # as_completed(tasks)
                for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                    await task
                image = [task.result() for task in tasks]
                product_set = set(products)
                for i in range(len(title)):
                    product = Product(title[i], price[i], image[i])
                    if product not in product_set:
                        products.append(product)
                self.refresh_product_list()
                messagebox.showinfo("提示", "搜索完成", parent=self.search_window)
                self.close_search_window()
            except Exception as e:
                messagebox.showerror(
                    "错误", f"{e}, 无法获取数据", parent=self.search_window)
        else:
            messagebox.showerror("错误", "关键字不能为空", parent=self.search_window)

    def refresh_user_list(self):
        self.user_list.delete(0, tk.END)
        for user in users:
            self.user_list.insert(tk.END, user)

    def create_user_window(self):
        self.user_window = tk.Toplevel(self)
        self.user_window.title("添加用户")
        self.user_window.geometry("500x400")
        self.user_window.protocol("WM_DELETE_WINDOW", self.close_user_window)

        self.username_label = tk.Label(self.user_window, text="用户名：")
        self.username_label.pack(padx=5, pady=5)
        self.username_entry = tk.Entry(
            self.user_window, font=self.default_font)
        self.username_entry.pack(padx=5, pady=5)

        self.password_label = tk.Label(self.user_window, text="密码：")
        self.password_label.pack(padx=5, pady=5)
        self.password_entry = tk.Entry(
            self.user_window, show="*", font=self.default_font)
        self.password_entry.pack(padx=5, pady=5)

        self.add_user_button = tk.Button(
            self.user_window, text="添加用户", command=self.add_user)
        self.add_user_button.pack(padx=5, pady=5)

    def close_user_window(self):
        self.user_window.destroy()

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        # sanity check
        if not username or not password:
            messagebox.showerror("错误", "用户名或密码不能为空", parent=self.user_window)
            return
        new_user = User(username, password)
        if new_user in users:
            messagebox.showerror("错误", "用户名已存在", parent=self.user_window)
        else:
            users.append(new_user)
            save_data()
            self.refresh_user_list()
            messagebox.showinfo("提示", "用户已添加", parent=self.user_window)
            self.close_user_window()

    def delete_user(self):
        selection = self.user_list.curselection()
        if selection:
            user_to_delete = users[selection[0]]
            if user_to_delete.username != "admin":
                users.remove(user_to_delete)
                print(users)
                save_data()
                self.refresh_user_list()
                messagebox.showinfo("提示", "用户已删除", parent=self)
            else:
                messagebox.showerror("错误", "不能删除管理员账号", parent=self)

    def refresh_product_list(self):
        save_data()
        self.product_list.delete(0, tk.END)
        for product in products:
            self.product_list.insert(
                tk.END, f"{product.name[:20]}... - 价格: ¥{product.price}")

    def add_product(self):
        title = self.title_entry.get().strip()
        price = self.price_entry.get().strip()

        # sanity check
        if not title or not price:
            messagebox.showerror("错误", "标题或价格不能为空", parent=self)
            return

        image_path = filedialog.askopenfilename()
        if not image_path:
            return

        image = Image.open(image_path)
        image.thumbnail((100, 100))

        price = float(price)

        if title and price and image_path:
            new_product = Product(title, price, image)
            products.append(new_product)
            save_data()
            self.refresh_product_list()
            messagebox.showinfo("提示", "商品已添加", parent=self)

    def delete_product(self):
        selection = self.product_list.curselection()
        if selection:
            product_to_delete = products[selection[0]]
            products.remove(product_to_delete)
            save_data()
            self.refresh_product_list()
            messagebox.showinfo("提示", "商品已删除", parent=self)


class ShoppingSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("商场系统")
        self.geometry("1000x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._frame = None  # Initialize the _frame attribute
        self.switch_frame(MainApplication)
        load_data()

        # Create a menu bar
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Create a File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, font=('思源黑体', 12))
        self.menu_bar.add_cascade(label="User", menu=self.file_menu)
        self.file_menu.add_command(label="Logout", command=self.logout)

    def switch_frame(self, frame_class, *args):
        new_frame = frame_class(self, *args)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def on_closing(self):
        save_data()
        self.destroy()

    def logout(self):
        self.switch_frame(MainApplication)


if __name__ == "__main__":
    app = ShoppingSystem()
    app.mainloop()
