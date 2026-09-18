package com.salesreport.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

import androidx.core.content.FileProvider;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * AppUpdateManager - Quản lý kiểm tra và cập nhật ứng dụng qua OTA cho Team Cẩm Giang.
 * 
 * Luồng hoạt động:
 * 1. Đọc version.json từ Server (Vercel / GitHub).
 * 2. So sánh latestVersionCode với versionCode hiện tại của thiết bị.
 * 3. Hiển thị Dialog thông báo cập nhật kèm releaseNotes.
 * 4. Tải APK qua DownloadManager.
 * 5. Tự động kiểm tra quyền REQUEST_INSTALL_PACKAGES và bật màn hình cài đặt của hệ điều hành.
 */
public class AppUpdateManager {

    private static final String TAG = "AppUpdateManager";

    // Danh sách Endpoint kiểm tra phiên bản (Primary: Vercel, Fallback: GitHub Raw)
    private static final String PRIMARY_VERSION_URL = "https://bcgiang.vercel.app/version.json";
    private static final String FALLBACK_VERSION_URL = "https://raw.githubusercontent.com/linshin6/sales-report-app/main/version.json";

    private final Activity mActivity;
    private final Handler mMainHandler = new Handler(Looper.getMainLooper());
    private final ExecutorService mExecutor = Executors.newSingleThreadExecutor();

    private long mDownloadId = -1;
    private File mDownloadedApkFile = null;
    private boolean mPendingInstall = false;
    private BroadcastReceiver mDownloadReceiver = null;

    private static AppUpdateManager sInstance;

    public static synchronized AppUpdateManager getInstance(Activity activity) {
        if (sInstance == null || sInstance.mActivity != activity) {
            sInstance = new AppUpdateManager(activity);
        }
        return sInstance;
    }

    private AppUpdateManager(Activity activity) {
        this.mActivity = activity;
    }

    /**
     * Kiểm tra phiên bản mới.
     * @param isManualCheck true nếu do người dùng chủ động bấm nút "Kiểm tra cập nhật" trên giao diện.
     */
    public void checkForUpdate(final boolean isManualCheck) {
        if (isManualCheck) {
            Toast.makeText(mActivity, "Đang kiểm tra bản cập nhật...", Toast.LENGTH_SHORT).show();
        }

        mExecutor.execute(() -> {
            try {
                String jsonStr = fetchVersionJson(PRIMARY_VERSION_URL);
                if (jsonStr == null || jsonStr.trim().isEmpty()) {
                    jsonStr = fetchVersionJson(FALLBACK_VERSION_URL);
                }

                if (jsonStr == null || jsonStr.trim().isEmpty()) {
                    if (isManualCheck) {
                        mMainHandler.post(() -> Toast.makeText(mActivity, "Không thể kết nối máy chủ cập nhật. Vui lòng kiểm tra mạng!", Toast.LENGTH_SHORT).show());
                    }
                    return;
                }

                JSONObject json = new JSONObject(jsonStr);
                final int latestVersionCode = json.optInt("latestVersionCode", 0);
                final String latestVersionName = json.optString("latestVersionName", "Mới nhất");
                final String releaseNotes = json.optString("releaseNotes", "Cải tiến hiệu năng và cập nhật dữ liệu mới.");
                final String apkDownloadUrl = json.optString("apkDownloadUrl", "");
                final boolean forceUpdate = json.optBoolean("forceUpdate", false);

                final long currentVersionCode = getCurrentVersionCode();
                final String currentVersionName = getCurrentVersionName();

                Log.d(TAG, "Current Version: " + currentVersionCode + " (" + currentVersionName + "), Latest: " + latestVersionCode + " (" + latestVersionName + ")");

                mMainHandler.post(() -> {
                    if (mActivity.isFinishing() || mActivity.isDestroyed()) return;

                    // Không bao giờ hiện popup nếu tên phiên bản trùng nhau (đã cài đặt bản mới nhất)
                    boolean isSameVersion = latestVersionName.equalsIgnoreCase(currentVersionName) 
                            || ("v" + latestVersionName).equalsIgnoreCase(currentVersionName)
                            || latestVersionName.equalsIgnoreCase("v" + currentVersionName);

                    // Chỉ hiện popup Native nếu do người dùng chủ động bấm kiểm tra (isManualCheck == true).
                    // Khi tự động kiểm tra, để giao diện Web HTML Modal đảm nhiệm, tuyệt đối không hiện đè popup Native.
                    if (isManualCheck && !isSameVersion && latestVersionCode > currentVersionCode) {
                        showUpdateDialog(latestVersionName, releaseNotes, apkDownloadUrl, forceUpdate);
                    } else {
                        if (isManualCheck) {
                            Toast.makeText(mActivity, "Ứng dụng đang ở phiên bản mới nhất (" + currentVersionName + ")", Toast.LENGTH_SHORT).show();
                        }
                    }
                });

            } catch (Exception e) {
                Log.e(TAG, "Lỗi kiểm tra cập nhật", e);
                if (isManualCheck) {
                    mMainHandler.post(() -> Toast.makeText(mActivity, "Lỗi kiểm tra bản cập nhật: " + e.getMessage(), Toast.LENGTH_SHORT).show());
                }
            }
        });
    }

    private void showUpdateDialog(final String latestVersionName, final String releaseNotes, final String apkDownloadUrl, final boolean forceUpdate) {
        AlertDialog.Builder builder = new AlertDialog.Builder(mActivity)
                .setTitle("🚀 Có bản cập nhật mới (v" + latestVersionName + ")")
                .setMessage(releaseNotes)
                .setCancelable(!forceUpdate)
                .setPositiveButton("Cập nhật ngay", (dialog, which) -> {
                    downloadAndInstall(apkDownloadUrl, latestVersionName);
                });

        if (!forceUpdate) {
            builder.setNegativeButton("Để sau", null);
        }

        builder.show();
    }

    private void downloadAndInstall(final String apkUrl, final String versionName) {
        if (apkUrl == null || apkUrl.trim().isEmpty()) {
            Toast.makeText(mActivity, "Đường dẫn tải file APK không hợp lệ!", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            File cacheDir = mActivity.getCacheDir();
            if (cacheDir != null && !cacheDir.exists()) {
                cacheDir.mkdirs();
            }

            mDownloadedApkFile = new File(cacheDir, "update.apk");

            if (mDownloadedApkFile.exists()) {
                mDownloadedApkFile.delete();
            }

            registerDownloadReceiver();

            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(apkUrl));
            request.setTitle("Cập nhật Báo Cáo Doanh Số");
            request.setDescription("Đang tải phiên bản v" + versionName + "...");
            request.setDestinationUri(Uri.fromFile(mDownloadedApkFile));
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setMimeType("application/vnd.android.package-archive");

            DownloadManager downloadManager = (DownloadManager) mActivity.getSystemService(Context.DOWNLOAD_SERVICE);
            if (downloadManager != null) {
                mDownloadId = downloadManager.enqueue(request);
                Toast.makeText(mActivity, "Đang tải bản cập nhật trong nền...", Toast.LENGTH_SHORT).show();
            } else {
                openBrowserDownload();
            }

        } catch (Exception e) {
            Log.e(TAG, "Lỗi bắt đầu tải APK", e);
            Toast.makeText(mActivity, "Lỗi tải APK: " + e.getMessage() + ". Đang mở trình duyệt...", Toast.LENGTH_LONG).show();
            openBrowserDownload();
        }
    }

    private void registerDownloadReceiver() {
        if (mDownloadReceiver != null) {
            try {
                mActivity.unregisterReceiver(mDownloadReceiver);
            } catch (Exception ignored) {}
        }

        mDownloadReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                long id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1);
                if (id == mDownloadId && mDownloadedApkFile != null && mDownloadedApkFile.exists()) {
                    unregisterDownloadReceiver();
                    Toast.makeText(mActivity, "Tải xong! Đang mở trình cài đặt...", Toast.LENGTH_SHORT).show();
                    installApk(mDownloadedApkFile);
                }
            }
        };

        IntentFilter filter = new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            mActivity.registerReceiver(mDownloadReceiver, filter, Context.RECEIVER_EXPORTED);
        } else {
            mActivity.registerReceiver(mDownloadReceiver, filter);
        }
    }

    private void unregisterDownloadReceiver() {
        if (mDownloadReceiver != null) {
            try {
                mActivity.unregisterReceiver(mDownloadReceiver);
            } catch (Exception ignored) {}
            mDownloadReceiver = null;
        }
    }

    /**
     * Kích hoạt Package Installer để cài đặt bản APK vừa tải.
     */
    public void installApk(File apkFile) {
        if (apkFile == null || !apkFile.exists() || apkFile.length() < 100000) {
            Toast.makeText(mActivity, "File cài đặt chưa hoàn tất hoặc bị hỏng. Đang mở trình duyệt...", Toast.LENGTH_SHORT).show();
            openBrowserDownload();
            return;
        }

        // Bắt lỗi quyền REQUEST_INSTALL_PACKAGES trên Android 8.0+ (API 26+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            boolean canInstall = mActivity.getPackageManager().canRequestPackageInstalls();
            if (!canInstall) {
                mPendingInstall = true;
                new AlertDialog.Builder(mActivity)
                        .setTitle("Cần cấp quyền cài đặt")
                        .setMessage("Để cài đặt bản cập nhật, bạn cần cho phép ứng dụng quyền 'Cài đặt ứng dụng không rõ nguồn gốc'.\n\nBấm 'Đi đến Cài đặt' và bật công tắc cho phép.")
                        .setPositiveButton("Đi đến Cài đặt", (dialog, which) -> {
                            try {
                                Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                        Uri.parse("package:" + mActivity.getPackageName()));
                                mActivity.startActivity(intent);
                            } catch (Exception e) {
                                Log.e(TAG, "Cannot open install permission settings", e);
                            }
                        })
                        .setNegativeButton("Hủy", (dialog, which) -> mPendingInstall = false)
                        .show();
                return;
            }
        }

        try {
            Uri apkUri = FileProvider.getUriForFile(mActivity, mActivity.getPackageName() + ".provider", apkFile);
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

            // Explicitly grant URI read permissions to all package installer components
            java.util.List<android.content.pm.ResolveInfo> resInfoList = mActivity.getPackageManager().queryIntentActivities(intent, PackageManager.MATCH_DEFAULT_ONLY);
            for (android.content.pm.ResolveInfo resolveInfo : resInfoList) {
                if (resolveInfo.activityInfo != null) {
                    mActivity.grantUriPermission(resolveInfo.activityInfo.packageName, apkUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                }
            }
            for (String pkg : new String[]{"com.google.android.packageinstaller", "com.android.packageinstaller"}) {
                try {
                    mActivity.grantUriPermission(pkg, apkUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                } catch (Exception ignored) {}
            }

            mActivity.startActivity(intent);
            mPendingInstall = false;
        } catch (Exception e) {
            Log.e(TAG, "Lỗi kích hoạt màn hình cài đặt", e);
            Toast.makeText(mActivity, "Không thể mở màn hình cài đặt tự động: " + e.getMessage() + ". Đang chuyển sang trình duyệt...", Toast.LENGTH_LONG).show();
            openBrowserDownload();
        }
    }

    public void openBrowserDownload() {
        try {
            String downloadUrl = "https://bcgiang.vercel.app/BaoCaoDoanhSo_TeamCamGiang.apk";
            Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(downloadUrl));
            browserIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            mActivity.startActivity(browserIntent);
        } catch (Exception ex) {
            Log.e(TAG, "Cannot open browser download", ex);
        }
    }

    /**
     * Gọi trong onResume() của MainActivity.
     * Khi người dùng vừa bật toggle cấp quyền cài đặt ở Settings quay lại app, tự động mở cài đặt APK ngay.
     */
    public void onResume() {
        if (mPendingInstall && mDownloadedApkFile != null && mDownloadedApkFile.exists()) {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O || mActivity.getPackageManager().canRequestPackageInstalls()) {
                mPendingInstall = false;
                installApk(mDownloadedApkFile);
            }
        }
    }

    public void onDestroy() {
        unregisterDownloadReceiver();
        mExecutor.shutdown();
    }

    private String fetchVersionJson(String urlString) {
        HttpURLConnection conn = null;
        BufferedReader reader = null;
        try {
            URL url = new URL(urlString + "?t=" + System.currentTimeMillis()); // Chống cache HTTP
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(8000);
            conn.setReadTimeout(8000);
            conn.setRequestProperty("Accept", "application/json");

            if (conn.getResponseCode() != HttpURLConnection.HTTP_OK) {
                return null;
            }

            reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            return sb.toString();
        } catch (Exception e) {
            Log.w(TAG, "fetchVersionJson failed for " + urlString + ": " + e.getMessage());
            return null;
        } finally {
            try {
                if (reader != null) reader.close();
                if (conn != null) conn.disconnect();
            } catch (Exception ignored) {}
        }
    }

    private long getCurrentVersionCode() {
        try {
            try (java.io.InputStream is = mActivity.getAssets().open("www/version.json");
                 BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }
                JSONObject obj = new JSONObject(sb.toString());
                long code = obj.optLong("latestVersionCode", -1);
                if (code > 0) return code;
            } catch (Exception ignored) {}

            PackageInfo pInfo = mActivity.getPackageManager().getPackageInfo(mActivity.getPackageName(), 0);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                return pInfo.getLongVersionCode();
            } else {
                return pInfo.versionCode;
            }
        } catch (Exception e) {
            return 1;
        }
    }

    private String getCurrentVersionName() {
        try {
            try (java.io.InputStream is = mActivity.getAssets().open("www/version.json");
                 BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }
                JSONObject obj = new JSONObject(sb.toString());
                String v = obj.optString("latestVersionName", "");
                if (!v.isEmpty()) return v;
            } catch (Exception ignored) {}

            PackageInfo pInfo = mActivity.getPackageManager().getPackageInfo(mActivity.getPackageName(), 0);
            return pInfo.versionName != null ? pInfo.versionName : "1.0.7";
        } catch (Exception e) {
            return "1.0.7";
        }
    }
}
