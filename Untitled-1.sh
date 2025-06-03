#!/bin/bash

# اسم المستخدم والبريد
git config --global user.name "00kais00"
git config --global user.email "00kais00@gmail.com"

# تهيئة المستودع
git init

# إضافة كل الملفات
git add .

# أول Commit
git commit -m "Initial commit"

# ربط المستودع بالرابط (غيّر الرابط بالرابط الحقيقي لمستودعك على GitHub)
git remote add origin https://github.com/00kais00/facebook.git

# تغيير اسم الفرع (اختياري إذا احتجت إلى main)
git branch -M main

# رفع الملفات إلى GitHub
git push -u origin main
