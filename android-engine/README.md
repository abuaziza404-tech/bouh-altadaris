# Abuaziza AI — نموذج خاص قابل للتطوير

هذا المجلد يحتوي على محرك محلي قابل للدمج في مشروع Android الذي يبنيه Workflow الخاص بك.

## ما يقدمه المحرك

- فهم نوايا عربية أساسي دون إنترنت.
- مسار مخصص لتحليل طلبات التنقيب.
- تقييم أولوية الهدف عبر مؤشرات سطحية وميدانية.
- قائمة بالأدلة الموجودة والمؤشرات الناقصة.
- لا يعلن وجود الذهب؛ يعرض أولوية الفحص فقط.

## الدمج مع Workflow

انسخ الملف:

```text
android-engine/app/src/main/java/com/abuaziza/ai/AbuazizaAIEngine.java
```

إلى:

```text
app/src/main/java/com/abuaziza/ai/AbuazizaAIEngine.java
```

ثم عدّل `MainActivity` ليستدعي:

```java
AbuazizaAIEngine.Reply reply = AbuazizaAIEngine.respond(prompt);
```

ولتقييم هدف ميداني:

```java
AbuazizaAIEngine.ProspectingResult result =
    AbuazizaAIEngine.scoreProspect(
        note,
        structure,
        faultContact,
        quartz,
        silica,
        clay,
        wadi,
        darkRegolith,
        oldWork,
        repeatedSignal,
        labSample
    );
```

## المرحلة التالية

لتحويله إلى نموذج AI فعلي، أضف Backend خاصاً بك خلف HTTPS، مع مصادقة ومحددات استخدام. لا تضع مفاتيح API أو كلمات مرور داخل APK أو GitHub Actions.
