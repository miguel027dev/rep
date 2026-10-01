package com.rep.intelligence;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private static final String REP_URL = "https://rep-performance-studio.miguel2341321.chatgpt.site";
    private static final String REP_HOST = "rep-performance-studio.miguel2341321.chatgpt.site";
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTheme(R.style.Theme_REP);
        getWindow().setStatusBarColor(Color.BLACK);
        getWindow().setNavigationBarColor(Color.BLACK);
        getWindow().getDecorView().setSystemUiVisibility(0);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.BLACK);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        setContentView(webView);
        configureWebView();

        if (savedInstanceState == null) webView.loadUrl(REP_URL);
        else webView.restoreState(savedInstanceState);
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setUserAgentString(settings.getUserAgentString() + " REP-Android/1.0");
        if (android.os.Build.VERSION.SDK_INT >= 26) settings.setSafeBrowsingEnabled(true);

        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String scheme = uri.getScheme();
                if ("https".equals(scheme) && isTrustedWebFlow(uri)) return false;
                if ("http".equals(scheme) || "https".equals(scheme) || "mailto".equals(scheme) || "tel".equals(scheme)) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) { }
                    return true;
                }
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) showOfflinePage();
            }

            @Override
            public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                recreate();
                return true;
            }
        });
    }

    private boolean isTrustedWebFlow(Uri uri) {
        String host = uri.getHost();
        return REP_HOST.equals(host)
            || "accounts.google.com".equals(host)
            || (host != null && host.endsWith(".google.com"))
            || (host != null && host.endsWith(".googleusercontent.com"));
    }

    private boolean isOnline() {
        ConnectivityManager manager = getSystemService(ConnectivityManager.class);
        Network network = manager.getActiveNetwork();
        if (network == null) return false;
        NetworkCapabilities capabilities = manager.getNetworkCapabilities(network);
        return capabilities != null && capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private void showOfflinePage() {
        String detail = isOnline() ? "Não conseguimos abrir o REP agora." : "Parece que você está sem internet.";
        String html = "<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'>"
            + "<style>*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#090909;color:#f5f5f1;font:16px Arial;display:grid;place-items:center;padding:28px}"
            + "main{width:100%;max-width:420px;text-align:center}.logo{font-size:30px;font-weight:900;letter-spacing:-2px;margin-bottom:64px}"
            + "i{display:block;width:64px;height:64px;border-radius:22px;background:#eee;color:#111;margin:0 auto 22px;padding-top:19px;font-style:normal;font-weight:900}"
            + "h1{font-size:34px;line-height:1;margin:0 0 12px;letter-spacing:-2px}p{color:#888;line-height:1.5;margin:0 0 30px}"
            + "button{width:100%;height:58px;border:0;border-radius:18px;background:#eee;color:#111;font-weight:800;font-size:15px}</style>"
            + "<main><div class='logo'>R&nbsp;&nbsp; REP</div><i>R</i><h1>Voltamos em um instante.</h1><p>" + detail + " Confira sua conexão e tente novamente.</p>"
            + "<button onclick=\"location.href='" + REP_URL + "'\">Tentar novamente</button></main>";
        webView.loadDataWithBaseURL(REP_URL, html, "text/html", "UTF-8", null);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }
}
