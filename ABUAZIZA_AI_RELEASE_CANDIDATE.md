# Abuaziza AI v1.1.0

## Integrated release candidate

تم دمج وحدة Android كاملة داخل `android-engine`:

- مساعد عربي محلي.
- تحليل عام وبرمجي وكتابي.
- شاشة تقييم مؤشرات التنقيب السطحي.
- محرك شفاف يعرض الأدلة والمؤشرات الناقصة.
- Android project مستقل قابل للبناء.

## بناء APK

من جهاز يحتوي Android SDK وJDK 17 وGradle:

```bash
cd android-engine
gradle wrapper --gradle-version 8.10.2 --distribution-type bin
./gradlew :app:assembleDebug
```

سيكون الملف هنا:

```text
android-engine/app/build/outputs/apk/debug/app-debug.apk
```

لنسخة release:

```bash
./gradlew :app:assembleRelease
```

## ملاحظة الإصدار

هذه نسخة Release Candidate رقم `1.1.0`. لا يمكن لهذه الجلسة تشغيل GitHub Actions أو تثبيت APK على جهازك فعليًا؛ بعد تشغيل البناء نزّل APK من Artifacts وثبّته على Android. لا تضع مفاتيح API أو كلمات مرور التوقيع داخل المستودع.
