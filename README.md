**Python程序设计**

**项目报告**

|                |                                   |
| -------------- | --------------------------------- |
| **项目名称：** | **基于Tkinter的在线商城购物系统** |
| **班 级：**    | **计科2211**                      |
| **小组编号：** | **1**                             |


**2024年6月7日**

# 概述

## 项目的意义

本项目旨在构建一个基于Python和Tkinter的图形用户界面（GUI）购物系统。项目综合了用户登录、注册、商品展示、购物车、商品结算等功能，此外，管理员还能够进行用户和商品管理。本项目对学习和掌握GUI编程、异步编程以及面向对象设计有重要意义。

## 项目任务和要求

用户管理功能：用户可以注册和登录，管理员可以增加和删除用户。

商品管理功能：管理员可以添加、删除和清空商品，并通过关键字搜索商品。

购物车功能：用户可以浏览商品、选择商品并添加到购物车，查看和清空购物车及结算。

异步数据处理：提高数据获取和图片处理的效率。

数据持久化：保存用户和商品数据，实现关闭后数据依然保留。

# 系统设计

## 系统架构图

## 系统运行流程图

## 模块功能说明

### MainApplication

功能: 处理用户的登录和注册功能。

输入: 用户名、密码。

输出: 用户/管理员Panel界面切换。

### UserPanel

功能: 提供用户添加商品到购物车，查看购物车，清空购物车和结算的功能。

输入: 商品选择，购物车操作。

输出: 商品被加入购物车，购物车信息展示，结算金额显示。

### AdminPanel

功能: 管理员可以进行用户管理和商品管理。

输入: 用户和商品操作。

输出: 用户和商品列表更新。

## 运行流程图

### MainApplication

### UserPanel

### AdminPanel

# 系统实现

## 各模块的运行界面和运行结果

### 用户登录界面

运行界面：显示用户名和密码的输入框，以及登录和注册按钮。

### 用户面板界面

商品展示界面：显示商品列表及商品添加到购物车的按钮。

购物车界面：显示已选商品列表及清空购物车和结算按钮。

### 管理员面板界面

用户管理界面：显示用户列表及增加和删除用户的按钮。

商品管理界面：显示商品列表及关键字搜索框、添加和删除商品的按钮。

## 关键代码分析

### 异步图片加载功能

第一个函数load_image_async的作用是从指定URL异步加载图片并调整其尺寸。首先，函数接受一个图片URL作为参数，然后使用httpx.AsyncClient创建一个异步HTTP客户端发送GET请求，以获取图片的二进制内容。随后，使用PIL.Image将二进制数据加载为图片对象，并获取其原始尺寸。为了保证图片宽度不超过100像素，函数重新计算图片的高度以保持宽高比，最后将调整后的图片返回。

第二个函数get_product_data用于从京东根据关键词搜索获取商品数据。该函数接受一个关键词参数，并构建搜索请求的URL。使用httpx.AsyncClient创建一个异步HTTP客户端发送GET请求，获取搜索结果页面，并使用BeautifulSoup解析HTML内容。接着，从解析的HTML中提取JavaScript脚本内容，解析出页面数据。如果请求成功，函数提取并解析商品数据为字典形式返回，否则，触发错误提示框并返回一个空列表。

### 数据持久化功能

# 总结与展望

## 总结

在本项目中，我们成功构建了一个基于Python和Tkinter的在线商城购物系统，系统实现了用户管理、商品管理、购物车、商品结算以及数据持久化功能。

系统运行效果：用户可以通过一个简单直观的GUI进行商品浏览、购物车操作和结算。管理员能够有效地管理用户和商品数据，确保系统的有序运行。

## 展望

尽管本项目已经实现了预定的功能，但仍存在一些可以改进和扩展的空间：

1. 异步数据处理： 进一步优化异步数据处理，如增加并发任务数和提高异步I/O的执行效率。

2. 图像缓存： 引入图像缓存机制，减少重复加载，提升系统响应速度。

3. 界面美化： 引入更为现代化的UI设计，提升用户界面的美观度和使用体验。

4. 用户提示与错误处理： 增加用户操作提示和更详细的错误处理机制，帮助用户更顺利地使用系统。

5. 多语言支持： 为界面添加多语言支持，以适应不同语言背景的用户需求。

6. 商品推荐系统： 开发基于用户行为的推荐系统，提高用户黏性和购买率。

7. 用户数据加密： 提高用户数据安全性，采用加密技术保护用户的个人信息和交易记录。

8. 安全认证： 引入多因子认证方式，提高系统的安全性。

9. 模块化代码结构： 进一步模块化代码，提升代码的可维护性和可读性。

10. 增加单元测试与集成测试： 构建全面的测试机制，确保系统的稳定性与可靠性。

通过以上的优化和扩展，我们相信该购物系统在性能、用户体验、安全性和功能性方面将得到显著提升，更加契合用户需求，成为一个功能完备、高效稳定的在线购物平台。
