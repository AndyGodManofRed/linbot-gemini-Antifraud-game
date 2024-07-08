FROM python:3.9

# 將專案複製到容器中
COPY . /app
WORKDIR /app

# set environment variables
ENV LINE_CHANNEL_ACCESS_TOKEN rfcdkNv0WpGywAxWBHBhExYwE8h+y88nJo35ng6Ip/UCcNR9SaGU48bZGBWzF+L/HKJ22HFoVLLTTC9OY2iyO3gSid8BWdy9Zl9Lx/lAdu5Oa8QidcMomk8JyzN3tLOx7tc2mDIDOlAixCfH2uji2QdB04t89/1O/w1cDnyilFU=
ENV LINE_CHANNEL_SECRET 0afd066a3c53649eb747a3e7bd2a1745
ENV API_ENV production
ENV PORT 8080
ENV LOG INFO
ENV GEMINI_API_KEY AIzaSyDj6ET_xzBgNcwsHJ3RzXxOqbRClCJPzws
ENV FIREBASE_URL https://sitcon-5934e-default-rtdb.asia-southeast1.firebasedatabase.app/
ENV OPEN_API_KEY CWA-F4EF5E09-170E-4374-9D51-AEB9D452A284

# 安裝必要的套件
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8080
CMD uvicorn main:app --host=0.0.0.0 --port=%PORT%
