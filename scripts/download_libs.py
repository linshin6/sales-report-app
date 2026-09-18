import os
import urllib.request
import zipfile

LIBS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'android_libs')
os.makedirs(LIBS_DIR, exist_ok=True)

deps = [
    ('https://dl.google.com/android/maven2/androidx/annotation/annotation-jvm/1.6.0/annotation-jvm-1.6.0.jar', 'annotation.jar'),
    ('https://dl.google.com/android/maven2/androidx/appcompat/appcompat/1.6.1/appcompat-1.6.1.aar', 'appcompat.aar'),
    ('https://dl.google.com/android/maven2/androidx/core/core/1.9.0/core-1.9.0.aar', 'core.aar'),
    ('https://dl.google.com/android/maven2/androidx/activity/activity/1.6.0/activity-1.6.0.aar', 'activity.aar'),
    ('https://dl.google.com/android/maven2/androidx/webkit/webkit/1.6.0/webkit-1.6.0.aar', 'webkit.aar'),
    ('https://dl.google.com/android/maven2/androidx/lifecycle/lifecycle-common/2.5.1/lifecycle-common-2.5.1.jar', 'lifecycle-common.jar'),
    ('https://dl.google.com/android/maven2/androidx/lifecycle/lifecycle-viewmodel/2.5.1/lifecycle-viewmodel-2.5.1.aar', 'lifecycle-viewmodel.aar'),
    ('https://dl.google.com/android/maven2/androidx/savedstate/savedstate/1.2.0/savedstate-1.2.0.aar', 'savedstate.aar'),
    ('https://dl.google.com/android/maven2/androidx/fragment/fragment/1.5.0/fragment-1.5.0.aar', 'fragment.aar'),
    ('https://dl.google.com/android/maven2/androidx/drawerlayout/drawerlayout/1.1.1/drawerlayout-1.1.1.aar', 'drawerlayout.aar'),
    ('https://dl.google.com/android/maven2/androidx/customview/customview/1.1.0/customview-1.1.0.aar', 'customview.aar'),
]

for url, fname in deps:
    target = os.path.join(LIBS_DIR, fname)
    if not os.path.exists(target):
        print(f"Downloading {fname}...")
        urllib.request.urlretrieve(url, target)
    if fname.endswith('.aar'):
        jar_target = os.path.join(LIBS_DIR, fname.replace('.aar', '.jar'))
        if not os.path.exists(jar_target):
            with zipfile.ZipFile(target, 'r') as z:
                with open(jar_target, 'wb') as f:
                    f.write(z.read('classes.jar'))
            print(f"Extracted classes.jar -> {os.path.basename(jar_target)}")

print("All AndroidX libraries ready!")
