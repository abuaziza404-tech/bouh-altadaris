# Abuaziza AI — Android integration module

## Delivered in this iteration

- Multi-purpose Arabic assistant screen.
- Offline intent routing for general, software, analysis, creative, and prospecting requests.
- Prospecting screen with transparent surface-indicator scoring.
- Evidence and missing-data reporting.
- No claim of confirmed gold.
- No API key or secret embedded in the application.

## Build integration

Copy these Java files into the generated Android project:

```text
android-engine/app/src/main/java/com/abuaziza/ai/AbuazizaAIEngine.java
android-engine/app/src/main/java/com/abuaziza/ai/MainActivity.java
```

The generated project must define:

```text
com.abuaziza.ai.R.id.root_container
com.abuaziza.ai.R.drawable.bg_card
com.abuaziza.ai.R.drawable.bg_input
```

The existing clean-project workflow can generate the resource files and then compile the module.

## Release status

This commit contains the application module and product specification. A signed APK release requires running the repository's Android Actions workflow; this API session cannot execute Actions or publish a GitHub Release directly.
