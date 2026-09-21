package com.abuaziza.ai;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Offline-first domain engine for Abuaziza AI.
 * It combines Arabic intent detection, field notes, and surface-indicator scoring.
 * It deliberately reports field priorities, never confirmed gold.
 */
public final class AbuazizaAIEngine {
    public static final class Reply {
        public final String text;
        public final String intent;
        public final double confidence;
        public Reply(String text, String intent, double confidence) {
            this.text = text;
            this.intent = intent;
            this.confidence = confidence;
        }
    }

    public static final class ProspectingResult {
        public final double score;
        public final String level;
        public final String decision;
        public final List<String> evidence;
        public final List<String> missing;

        ProspectingResult(double score, String level, String decision,
                          List<String> evidence, List<String> missing) {
            this.score = score;
            this.level = level;
            this.decision = decision;
            this.evidence = evidence;
            this.missing = missing;
        }
    }

    private AbuazizaAIEngine() {}

    public static Reply respond(String prompt) {
        String p = prompt == null ? "" : prompt.trim().toLowerCase(Locale.ROOT);
        if (p.isEmpty()) return new Reply("اكتب سؤالك أو وصف الهدف الميداني أولاً.", "empty", 1.0);
        if (containsAny(p, "ذهب", "تنقيب", "جوسان", "كوارتز", "gpz", "مؤشر")) {
            return new Reply("سأحوّل وصفك الميداني إلى مؤشرات قابلة للفحص. اذكر الإحداثيات، البنية، الكوارتز، الجوسان، الطين، الأودية، وتكرار الإشارة. النتيجة أولوية فحص وليست إثباتاً للذهب.", "prospecting", 0.94);
        }
        if (containsAny(p, "كود", "برمج", "تطبيق", "خطأ", "android")) {
            return new Reply("أستطيع مساعدتك في تصميم التطبيق، تحليل الخطأ، وتنظيم مراحل البناء. أرسل الملف أو رسالة الخطأ كما هي.", "software", 0.92);
        }
        if (containsAny(p, "حلل", "تحليل", "لخص", "ملخص")) {
            return new Reply("أرسل النص أو البيانات كاملة، وسأعيدها في صورة ملخص وقرارات وخطوات عملية.", "analysis", 0.90);
        }
        if (containsAny(p, "قصيدة", "شعر", "قافية")) {
            return new Reply("أرسل الموضوع والقافية والأسلوب المطلوب، وسأكتب نصاً منظماً.", "creative", 0.91);
        }
        return new Reply("تم استلام طلبك. هذه النسخة تعمل محلياً دون إرسال بياناتك. يمكنك طلب تحليل، برمجة، كتابة، أو تقييم مؤشرات تنقيب.", "general", 0.72);
    }

    public static ProspectingResult scoreProspect(String note, boolean structure,
                                                    boolean faultContact, boolean quartz,
                                                    boolean silica, boolean clay,
                                                    boolean wadi, boolean darkRegolith,
                                                    boolean oldWork, boolean repeatedSignal,
                                                    boolean labSample) {
        String p = note == null ? "" : note.toLowerCase(Locale.ROOT);
        List<String> evidence = new ArrayList<>();
        List<String> missing = new ArrayList<>();
        double score = 0;
        if (structure || containsAny(p, "بنية", "خطية", "shear", "structure")) { score += 18; evidence.add("بنية/خطيات"); } else missing.add("بنية جيولوجية واضحة");
        if (faultContact || containsAny(p, "فالق", "قص", "تماس", "fault")) { score += 15; evidence.add("فالق أو تماس"); } else missing.add("فالق أو تماس صخري");
        if (quartz || containsAny(p, "كوارتز", "quartz")) { score += 14; evidence.add("كوارتز"); } else missing.add("كوارتز موثق");
        if (silica || containsAny(p, "سيليكا", "silica")) { score += 12; evidence.add("سيليكا"); } else missing.add("مؤشر سيليكا");
        if (clay || containsAny(p, "طين", "تحول", "clay")) { score += 10; evidence.add("طين/تحول"); } else missing.add("تحول طيني");
        if (wadi || containsAny(p, "وادي", "مجرى", "wadi")) { score += 8; evidence.add("تصريف أو وادٍ"); }
        if (darkRegolith || containsAny(p, "داكن", "أسود", "regolith")) { score += 8; evidence.add("غطاء سطحي داكن"); }
        if (oldWork || containsAny(p, "حفر قديمة", "تعدين أهلي", "لودر")) { score += 7; evidence.add("أعمال قديمة"); }
        if (repeatedSignal || containsAny(p, "متكرر", "تكرار", "إشارة ثابتة")) { score += 12; evidence.add("إشارة متكررة"); } else missing.add("تكرار القياس من اتجاهات متعددة");
        if (labSample) { score += 20; evidence.add("عينة/تحليل مخبري"); } else missing.add("عينة وتحليل مخبري");
        score = Math.min(100, score);
        String level;
        String decision;
        if (labSample && score >= 75) { level = "Priority 1"; decision = "أولوية فحص مع توثيق العينة؛ لا تُعد إثباتاً نهائياً"; }
        else if (score >= 65) { level = "Candidate"; decision = "فحص ميداني منظم وجمع عينة"; }
        else if (score >= 45) { level = "Monitoring"; decision = "مراقبة وجمع بيانات إضافية"; }
        else { level = "Low"; decision = "لا توجد مؤشرات كافية حالياً"; }
        return new ProspectingResult(score, level, decision, evidence, missing);
    }

    private static boolean containsAny(String text, String... terms) {
        for (String term : terms) if (text.contains(term)) return true;
        return false;
    }
}
