package com.salesreport.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInstaller;
import android.os.Build;
import android.util.Log;
import android.widget.Toast;

/**
 * InstallStatusReceiver - Nhận phản hồi trạng thái từ PackageInstaller.Session.
 * Khi hệ thống trả về STATUS_PENDING_USER_ACTION, bắt buộc phải khởi chạy Intent.EXTRA_INTENT
 * để hiển thị hộp thoại xác nhận cài đặt cho người dùng.
 */
public class InstallStatusReceiver extends BroadcastReceiver {

    private static final String TAG = "InstallStatusReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;

        int status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, -1);
        Log.d(TAG, "PackageInstaller Status Callback: " + status);

        switch (status) {
            case PackageInstaller.STATUS_PENDING_USER_ACTION:
                Log.d(TAG, "STATUS_PENDING_USER_ACTION: Đang mở màn hình xác nhận cài đặt...");
                Intent confirmationIntent;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    confirmationIntent = intent.getParcelableExtra(Intent.EXTRA_INTENT, Intent.class);
                } else {
                    confirmationIntent = intent.getParcelableExtra(Intent.EXTRA_INTENT);
                }
                if (confirmationIntent != null) {
                    confirmationIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    try {
                        context.startActivity(confirmationIntent);
                    } catch (Exception e) {
                        Log.e(TAG, "Lỗi khi startActivity confirmationIntent", e);
                    }
                } else {
                    Log.e(TAG, "confirmationIntent is NULL!");
                }
                break;

            case PackageInstaller.STATUS_SUCCESS:
                Log.d(TAG, "STATUS_SUCCESS: Cập nhật thành công!");
                Toast.makeText(context, "✅ Cập nhật ứng dụng thành công!", Toast.LENGTH_SHORT).show();
                break;

            default:
                String message = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE);
                Log.w(TAG, "PackageInstaller status " + status + ": " + message);
                break;
        }
    }
}
