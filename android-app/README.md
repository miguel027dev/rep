# TYVON Android

Aplicativo Android WebView do TYVON. Ele abre a versão publicada em `rep-kky9.onrender.com`, preserva a sessão da conta, bloqueia conteúdo HTTP e envia links externos ao navegador.

## Compilar

Defina `ANDROID_HOME` para um Android SDK com API 35 e execute:

```bash
gradle :app:assembleDebug
```

O APK instalável fica em `app/build/outputs/apk/debug/app-debug.apk`. Para publicar na Play Store, gere uma chave de assinatura definitiva da empresa e um Android App Bundle de release.
