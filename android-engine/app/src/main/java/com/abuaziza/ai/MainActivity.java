package com.abuaziza.ai;

import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

/** Multi-purpose offline-first Abuaziza AI screen. */
public final class MainActivity extends AppCompatActivity {
    private LinearLayout messages;
    private EditText prompt;
    private EditText fieldNote;
    private TextView prospectResult;

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density);
    }

    private TextView bubble(String text, boolean user) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextSize(16);
        view.setTextColor(user ? Color.BLACK : Color.WHITE);
        view.setGravity(Gravity.RIGHT);
        view.setPadding(dp(14), dp(12), dp(14), dp(12));
        view.setBackgroundResource(user ? android.R.color.holo_orange_light : R.drawable.bg_card);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.setMargins(dp(6), dp(5), dp(6), dp(5));
        view.setLayoutParams(params);
        return view;
    }

    private void addMessage(String text, boolean user) {
        messages.addView(bubble(text, user));
        ((ScrollView) messages.getParent()).post(() ->
                ((ScrollView) messages.getParent()).fullScroll(ScrollView.FOCUS_DOWN));
    }

    private TextView label(String text) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextColor(Color.WHITE);
        view.setTextSize(15);
        view.setGravity(Gravity.RIGHT);
        view.setPadding(dp(4), dp(8), dp(4), dp(4));
        return view;
    }

    private CheckBox option(LinearLayout parent, String text) {
        CheckBox box = new CheckBox(this);
        box.setText(text);
        box.setTextColor(Color.WHITE);
        box.setGravity(Gravity.RIGHT);
        parent.addView(box, new LinearLayout.LayoutParams(-1, -2));
        return box;
    }

    private void buildChat(LinearLayout root) {
        ScrollView scroll = new ScrollView(this);
        messages = new LinearLayout(this);
        messages.setOrientation(LinearLayout.VERTICAL);
        messages.setPadding(dp(8), dp(8), dp(8), dp(8));
        scroll.addView(messages);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

        LinearLayout composer = new LinearLayout(this);
        composer.setPadding(dp(8), dp(8), dp(8), dp(8));
        prompt = new EditText(this);
        prompt.setHint("اكتب سؤالاً أو وصفاً...");
        prompt.setTextColor(Color.WHITE);
        prompt.setHintTextColor(Color.GRAY);
        prompt.setGravity(Gravity.RIGHT);
        prompt.setBackgroundResource(R.drawable.bg_input);
        composer.addView(prompt, new LinearLayout.LayoutParams(0, dp(58), 1));
        Button send = new Button(this);
        send.setText("إرسال");
        composer.addView(send, new LinearLayout.LayoutParams(dp(90), dp(58)));
        send.setOnClickListener(v -> {
            String value = prompt.getText().toString();
            if (!value.trim().isEmpty()) {
                addMessage(value, true);
                prompt.setText("");
                AbuazizaAIEngine.Reply reply = AbuazizaAIEngine.respond(value);
                addMessage(reply.text + "\nالنية: " + reply.intent, false);
            }
        });
        root.addView(composer, new LinearLayout.LayoutParams(-1, -2));
        addMessage("مرحباً بك في أبو عزيزة AI. اختر الاستخدام أو اكتب طلبك.", false);
    }

    private void buildProspecting(LinearLayout root) {
        ScrollView scroll = new ScrollView(this);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(12), dp(8), dp(12), dp(8));
        content.addView(label("تحليل أولوية هدف سطحي — النتيجة ليست إثباتاً للذهب"));
        fieldNote = new EditText(this);
        fieldNote.setHint("ملاحظات: كوارتز، جوسان، وادي، طين، فالق...");
        fieldNote.setTextColor(Color.WHITE);
        fieldNote.setHintTextColor(Color.GRAY);
        fieldNote.setGravity(Gravity.RIGHT);
        fieldNote.setMinLines(3);
        fieldNote.setBackgroundResource(R.drawable.bg_input);
        content.addView(fieldNote, new LinearLayout.LayoutParams(-1, dp(100)));
        CheckBox structure = option(content, "بنية / خطيات واضحة");
        CheckBox fault = option(content, "فالق أو تماس");
        CheckBox quartz = option(content, "كوارتز");
        CheckBox silica = option(content, "سيليكا");
        CheckBox clay = option(content, "طين أو تحول");
        CheckBox wadi = option(content, "وادي أو تصريف");
        CheckBox dark = option(content, "غطاء سطحي داكن");
        CheckBox oldWork = option(content, "أعمال قديمة");
        CheckBox repeated = option(content, "إشارة متكررة");
        CheckBox lab = option(content, "عينة وتحليل مخبري");
        Button score = new Button(this);
        score.setText("احسب أولوية الفحص");
        content.addView(score, new LinearLayout.LayoutParams(-1, dp(56)));
        prospectResult = label("النتيجة: لم يتم التحليل");
        content.addView(prospectResult);
        score.setOnClickListener(v -> {
            AbuazizaAIEngine.ProspectingResult result = AbuazizaAIEngine.scoreProspect(
                    fieldNote.getText().toString(), structure.isChecked(), fault.isChecked(),
                    quartz.isChecked(), silica.isChecked(), clay.isChecked(), wadi.isChecked(),
                    dark.isChecked(), oldWork.isChecked(), repeated.isChecked(), lab.isChecked());
            prospectResult.setText("الدرجة: " + result.score + "\nالمستوى: " + result.level
                    + "\nالقرار: " + result.decision + "\nالأدلة: " + result.evidence
                    + "\nالناقص: " + result.missing);
        });
        scroll.addView(content);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
    }

    private void buildAbout(LinearLayout root) {
        root.addView(label("أبو عزيزة AI\n\nنسخة متعددة الاستخدام تعمل محلياً أولاً:\n• مساعد عربي\n• تحليل برمجي ومشاريع\n• تقييم مؤشرات التنقيب السطحي\n• سياسة نتائج شفافة\n• لا يتم إرسال البيانات دون ربط Backend وموافقة المستخدم\n\nلتحسين النموذج: احفظ الإحداثيات، مصدر الصورة، القياسات المتكررة، والعينات المخبرية، ثم عاير الأوزان على نتائج واقعية."));
    }

    private void show(String mode) {
        LinearLayout root = (LinearLayout) findViewById(R.id.root_container);
        root.removeAllViews();
        TextView title = label("أبوعزيزة AI — " + mode);
        title.setTextSize(22);
        title.setTextColor(Color.rgb(212, 175, 55));
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(62)));
        if (mode.equals("المحادثة")) buildChat(root);
        else if (mode.equals("التنقيب")) buildProspecting(root);
        else buildAbout(root);
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setId(R.id.root_container);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(18, 18, 18));
        root.setLayoutDirection(ViewGroup.LAYOUT_DIRECTION_RTL);
        setContentView(root);
        LinearLayout nav = new LinearLayout(this);
        Button chat = new Button(this); chat.setText("المحادثة");
        Button prospect = new Button(this); prospect.setText("التنقيب");
        Button about = new Button(this); about.setText("حول التطبيق");
        nav.addView(chat, new LinearLayout.LayoutParams(0, dp(54), 1));
        nav.addView(prospect, new LinearLayout.LayoutParams(0, dp(54), 1));
        nav.addView(about, new LinearLayout.LayoutParams(0, dp(54), 1));
        root.addView(nav);
        chat.setOnClickListener(v -> show("المحادثة"));
        prospect.setOnClickListener(v -> show("التنقيب"));
        about.setOnClickListener(v -> show("حول التطبيق"));
        show("المحادثة");
    }
}
