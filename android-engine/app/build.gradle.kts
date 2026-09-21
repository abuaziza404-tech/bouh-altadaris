plugins { id("com.android.application") }

android {
    namespace = "com.abuaziza.ai"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.abuaziza.ai"
        minSdk = 23
        targetSdk = 35
        versionCode = 11
        versionName = "1.1.0"
    }
    buildTypes {
        getByName("debug") { applicationIdSuffix = ".debug" }
        getByName("release") { isMinifyEnabled = false }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
}
