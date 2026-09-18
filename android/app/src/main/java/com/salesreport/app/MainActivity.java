package com.salesreport.app;

import android.app.Activity;
import android.content.ClipData;
import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.Toast;

import androidx.activity.OnBackPressedCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;
import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewClientCompat;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "SalesReportApp";
    private WebView mWebView;
    private ValueCallback<Uri[]> mFilePathCallback;
    private final ExecutorService mExecutor = Executors.newSingleThreadExecutor();

    private final ActivityResultLauncher<Intent> mFileChooserLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
                if (mFilePathCallback == null) return;

                Uri[] results = null;
                if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
                    Intent data = result.getData();
                    ClipData clipData = data.getClipData();
                    if (clipData != null) {
                        results = new Uri[clipData.getItemCount()];
                        for (int i = 0; i < clipData.getItemCount(); i++) {
                            results[i] = clipData.getItemAt(i).getUri();
                        }
                    } else if (data.getData() != null) {
                        results = new Uri[]{data.getData()};
                    }
                }

                mFilePathCallback.onReceiveValue(results);
                mFilePathCallback = null;
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mWebView = findViewById(R.id.webview);
        setupWebView();

        // Handle native back press
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (mWebView != null && mWebView.canGoBack()) {
                    mWebView.goBack();
                } else {
                    finish();
                }
            }
        });

        // Khởi tạo hoàn tất
    }

    private void setupWebView() {
        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);

        // Hardware acceleration
        mWebView.setLayerType(WebView.LAYER_TYPE_HARDWARE, null);

        // Setup AssetLoader for secure HTTPS origin
        final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        mWebView.setWebViewClient(new WebViewClientCompat() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }
        });

        // Setup file chooser & bridge
        mWebView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (mFilePathCallback != null) {
                    mFilePathCallback.onReceiveValue(null);
                }
                mFilePathCallback = filePathCallback;

                // Luôn mở bộ chọn tệp phổ quát (*/*) để Android không làm mờ file .xlsb (do Android thiếu định nghĩa MIME cho .xlsb)
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                if (fileChooserParams != null && fileChooserParams.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE) {
                    intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                }

                try {
                    mFileChooserLauncher.launch(intent);
                } catch (Exception e) {
                    Log.e(TAG, "Cannot launch file chooser", e);
                    mFilePathCallback.onReceiveValue(null);
                    mFilePathCallback = null;
                    return false;
                }
                return true;
            }
        });

        // Setup download listener to forward binary downloads
        mWebView.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
            try {
                Intent i = new Intent(Intent.ACTION_VIEW);
                i.setData(Uri.parse(url));
                startActivity(i);
            } catch (Exception e) {
                Log.e(TAG, "DownloadListener error", e);
            }
        });

        // Register AndroidBridge
        mWebView.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");

        // Load entry page via HTTPS asset loader
        mWebView.loadUrl("https://appassets.androidplatform.net/assets/www/index.html");
    }

    public class AndroidBridge {

        @JavascriptInterface
        public void installApkFromBase64(final String base64Data, final String filename) {
            mExecutor.execute(() -> {
                try {
                    byte[] fileBytes = Base64.decode(base64Data, Base64.DEFAULT);
                    File cacheDir = getCacheDir();
                    if (cacheDir != null && !cacheDir.exists()) {
                        cacheDir.mkdirs();
                    }
                    File apkFile = new File(cacheDir, filename != null ? filename : "BaoCaoDoanhSo_TeamCamGiang.apk");
                    if (apkFile.exists()) {
                        apkFile.delete();
                    }
                    try (FileOutputStream fos = new FileOutputStream(apkFile)) {
                        fos.write(fileBytes);
                        fos.flush();
                    }
                    if (!apkFile.exists() || apkFile.length() < 100000) {
                        throw new IllegalStateException("File APK không hợp lệ hoặc kích thước quá nhỏ (" + (apkFile.exists() ? apkFile.length() : 0) + " bytes)");
                    }
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Đang mở trình cài đặt bản mới...", Toast.LENGTH_SHORT).show();
                        AppUpdateManager.getInstance(MainActivity.this).installApk(apkFile);
                    });
                } catch (Exception e) {
                    Log.e(TAG, "installApkFromBase64 error", e);
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Lỗi cài đặt trực tiếp: " + e.getMessage() + ". Đang chuyển sang trình duyệt...", Toast.LENGTH_LONG).show();
                        AppUpdateManager.getInstance(MainActivity.this).openBrowserDownload();
                    });
                }
            });
        }

        @JavascriptInterface
        public void downloadAndInstallApk(final String downloadUrl) {
            final String urlToUse = (downloadUrl != null && !downloadUrl.trim().isEmpty())
                    ? downloadUrl.trim()
                    : "https://bcgiang.vercel.app/BaoCaoDoanhSo_TeamCamGiang.apk";
            mExecutor.execute(() -> {
                try {
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Đang tải bản cập nhật ngầm...", Toast.LENGTH_SHORT).show());
                    File cacheDir = getCacheDir();
                    if (cacheDir != null && !cacheDir.exists()) {
                        cacheDir.mkdirs();
                    }
                    File apkFile = new File(cacheDir, "BaoCaoDoanhSo_TeamCamGiang.apk");
                    if (apkFile.exists()) {
                        apkFile.delete();
                    }

                    java.net.URL url = new java.net.URL(urlToUse + (urlToUse.contains("?") ? "&" : "?") + "t=" + System.currentTimeMillis());
                    java.net.HttpURLConnection conn = (java.net.HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(10000);
                    conn.setReadTimeout(25000);
                    conn.connect();

                    if (conn.getResponseCode() != java.net.HttpURLConnection.HTTP_OK) {
                        throw new IllegalStateException("HTTP " + conn.getResponseCode() + " " + conn.getResponseMessage());
                    }

                    try (java.io.InputStream in = conn.getInputStream();
                         FileOutputStream out = new FileOutputStream(apkFile)) {
                        byte[] buffer = new byte[8192];
                        int bytesRead;
                        while ((bytesRead = in.read(buffer)) != -1) {
                            out.write(buffer, 0, bytesRead);
                        }
                        out.flush();
                    }

                    if (!apkFile.exists() || apkFile.length() < 100000) {
                        throw new IllegalStateException("Kích thước file tải về quá nhỏ: " + (apkFile.exists() ? apkFile.length() : 0) + " bytes");
                    }

                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Tải xong! Đang mở trình cài đặt...", Toast.LENGTH_SHORT).show();
                        AppUpdateManager.getInstance(MainActivity.this).installApk(apkFile);
                    });
                } catch (Exception e) {
                    Log.e(TAG, "downloadAndInstallApk error", e);
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Không thể cài tự động: " + e.getMessage() + ". Đang mở trình duyệt...", Toast.LENGTH_LONG).show();
                        AppUpdateManager.getInstance(MainActivity.this).openBrowserDownload();
                    });
                }
            });
        }

        @JavascriptInterface
        public void saveAndShare(final String base64Data, final String filename, final String mimeType) {
            mExecutor.execute(() -> {
                try {
                    byte[] fileBytes = Base64.decode(base64Data, Base64.DEFAULT);

                    // 1. Save to public Downloads directory
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        ContentValues values = new ContentValues();
                        values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename);
                        values.put(MediaStore.MediaColumns.MIME_TYPE, mimeType);
                        values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/BaoCaoDoanhSo");
                        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                        if (uri != null) {
                            try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                                if (os != null) {
                                    os.write(fileBytes);
                                }
                            }
                        }
                    } else {
                        File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "BaoCaoDoanhSo");
                        if (!dir.exists()) dir.mkdirs();
                        File dest = new File(dir, filename);
                        try (FileOutputStream fos = new FileOutputStream(dest)) {
                            fos.write(fileBytes);
                        }
                    }

                    // 2. Save to cache dir for sharing via FileProvider
                    File shareDir = new File(getCacheDir(), "shared_reports");
                    if (!shareDir.exists()) shareDir.mkdirs();
                    File shareFile = new File(shareDir, filename);
                    try (FileOutputStream fos = new FileOutputStream(shareFile)) {
                        fos.write(fileBytes);
                    }

                    Uri contentUri = FileProvider.getUriForFile(MainActivity.this, getPackageName() + ".provider", shareFile);

                    // 3. UI feedback & Share Dialog
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Đã lưu vào Tải về: " + filename, Toast.LENGTH_SHORT).show();

                        Intent shareIntent = new Intent(Intent.ACTION_SEND);
                        shareIntent.setType(mimeType);
                        shareIntent.putExtra(Intent.EXTRA_STREAM, contentUri);
                        shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivity(Intent.createChooser(shareIntent, "Chia sẻ báo cáo: " + filename));
                    });

                } catch (Exception e) {
                    Log.e(TAG, "Error in saveAndShare", e);
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Lỗi lưu file: " + e.getMessage(), Toast.LENGTH_LONG).show());
                }
            });
        }

        @JavascriptInterface
        public void shareToZalo(final String base64Data, final String filename) {
            mExecutor.execute(() -> {
                try {
                    byte[] fileBytes = Base64.decode(base64Data, Base64.DEFAULT);

                    // 1. Save to Downloads
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        ContentValues values = new ContentValues();
                        values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename);
                        values.put(MediaStore.MediaColumns.MIME_TYPE, "image/png");
                        values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/BaoCaoDoanhSo");
                        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                        if (uri != null) {
                            try (OutputStream os = getContentResolver().openOutputStream(uri)) {
                                if (os != null) {
                                    os.write(fileBytes);
                                }
                            }
                        }
                    } else {
                        File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "BaoCaoDoanhSo");
                        if (!dir.exists()) dir.mkdirs();
                        File dest = new File(dir, filename);
                        try (FileOutputStream fos = new FileOutputStream(dest)) {
                            fos.write(fileBytes);
                        }
                    }

                    // 2. Save to cache dir for sharing via FileProvider
                    File shareDir = new File(getCacheDir(), "shared_reports");
                    if (!shareDir.exists()) shareDir.mkdirs();
                    File shareFile = new File(shareDir, filename);
                    try (FileOutputStream fos = new FileOutputStream(shareFile)) {
                        fos.write(fileBytes);
                    }

                    Uri contentUri = FileProvider.getUriForFile(MainActivity.this, getPackageName() + ".provider", shareFile);

                    // 3. UI feedback & direct Zalo or Share Chooser
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Đang mở Zalo gửi báo cáo...", Toast.LENGTH_SHORT).show();

                        Intent shareIntent = new Intent(Intent.ACTION_SEND);
                        shareIntent.setType("image/png");
                        shareIntent.putExtra(Intent.EXTRA_STREAM, contentUri);
                        shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

                        // Cố gắng mở trực tiếp Zalo
                        Intent zaloIntent = new Intent(shareIntent);
                        zaloIntent.setPackage("com.zing.zalo");

                        try {
                            if (getPackageManager().getLaunchIntentForPackage("com.zing.zalo") != null) {
                                startActivity(zaloIntent);
                                return;
                            }
                        } catch (Exception ignored) { }

                        // Nếu không có Zalo hoặc lỗi, mở bộ chọn ứng dụng
                        startActivity(Intent.createChooser(shareIntent, "Gửi báo cáo qua Zalo / Tin nhắn"));
                    });

                } catch (Exception e) {
                    Log.e(TAG, "Error in shareToZalo", e);
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Lỗi gửi Zalo: " + e.getMessage(), Toast.LENGTH_LONG).show());
                }
            });
        }

        @JavascriptInterface
        public void copyToClipboard(final String text) {
            runOnUiThread(() -> {
                try {
                    android.content.ClipboardManager clipboard = (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                    android.content.ClipData clip = android.content.ClipData.newPlainText("Link Báo Cáo", text);
                    if (clipboard != null) {
                        clipboard.setPrimaryClip(clip);
                        Toast.makeText(MainActivity.this, "✅ Đã sao chép link báo cáo!", Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception e) {
                    Log.e(TAG, "copyToClipboard error", e);
                }
            });
        }

        @JavascriptInterface
        public void shareText(final String text, final String title) {
            runOnUiThread(() -> {
                try {
                    Intent sendIntent = new Intent();
                    sendIntent.setAction(Intent.ACTION_SEND);
                    sendIntent.putExtra(Intent.EXTRA_TEXT, text);
                    sendIntent.setType("text/plain");
                    Intent shareIntent = Intent.createChooser(sendIntent, title != null ? title : "Chia sẻ link báo cáo");
                    startActivity(shareIntent);
                } catch (Exception e) {
                    Log.e(TAG, "shareText error", e);
                }
            });
        }

        @JavascriptInterface
        public void checkForUpdate() {
            runOnUiThread(() -> {
                AppUpdateManager.getInstance(MainActivity.this).checkForUpdate(true);
            });
        }

        @JavascriptInterface
        public String getAppVersionInfo() {
            try {
                String vName = "1.0.7";
                long vCode = 8;
                try (java.io.InputStream is = getAssets().open("www/version.json");
                     java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(is))) {
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) {
                        sb.append(line);
                    }
                    org.json.JSONObject obj = new org.json.JSONObject(sb.toString());
                    vName = obj.optString("latestVersionName", "1.0.7");
                    vCode = obj.optLong("latestVersionCode", 8);
                } catch (Exception ignored) {}

                long lastUpdateTime = System.currentTimeMillis();
                try {
                    android.content.pm.PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
                    lastUpdateTime = pInfo.lastUpdateTime;
                } catch (Exception ignored) {}

                java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("HH:mm - dd/MM/yyyy", java.util.Locale.getDefault());
                String dateStr = sdf.format(new java.util.Date(lastUpdateTime));
                return "{\"versionName\":\"" + vName + "\",\"versionCode\":" + vCode + ",\"buildDate\":\"" + dateStr + "\"}";
            } catch (Exception e) {
                return "{}";
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        AppUpdateManager.getInstance(this).onResume();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        AppUpdateManager.getInstance(this).onDestroy();
        mExecutor.shutdown();
        if (mWebView != null) {
            mWebView.destroy();
        }
    }
}
