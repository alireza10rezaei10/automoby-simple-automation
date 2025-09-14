FROM nginx:alpine

# حذف کانفیگ پیش‌فرض
RUN rm /etc/nginx/conf.d/default.conf

# کپی کانفیگ جدید
COPY nginx.conf /etc/nginx/conf.d/default.conf

# کپی کل پروژه
COPY . /usr/share/nginx/html

# expose پورت
EXPOSE 80

# اجرا
CMD ["nginx", "-g", "daemon off;"]
