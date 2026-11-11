import os, re, shutil, sys

base = 'android/app/src/main'
pkgdir = os.path.join(base, 'java', 'uz', 'sanalar', 'app')
os.makedirs(pkgdir, exist_ok=True)
src = 'native'
for f in os.listdir(src):
    if f.endswith('.java'):
        shutil.copy(os.path.join(src, f), os.path.join(pkgdir, f))
shutil.copytree(os.path.join(src, 'res'), os.path.join(base, 'res'), dirs_exist_ok=True)

mf = os.path.join(base, 'AndroidManifest.xml')
s = open(mf, encoding='utf8').read()
perms = ''.join('    <uses-permission android:name="android.permission.%s"/>\n' % p for p in [
    'POST_NOTIFICATIONS', 'SCHEDULE_EXACT_ALARM', 'USE_EXACT_ALARM', 'USE_FULL_SCREEN_INTENT',
    'SYSTEM_ALERT_WINDOW', 'FOREGROUND_SERVICE', 'FOREGROUND_SERVICE_MEDIA_PLAYBACK', 'WAKE_LOCK',
    'VIBRATE', 'WRITE_SECURE_SETTINGS', 'USE_BIOMETRIC', 'QUERY_ALL_PACKAGES', 'RECEIVE_BOOT_COMPLETED', 'REQUEST_IGNORE_BATTERY_OPTIMIZATIONS', 'SET_WALLPAPER', 'KILL_BACKGROUND_PROCESSES'])
comps = '''
        <activity android:name=".AlarmActivity" android:exported="false" android:directBootAware="true" android:launchMode="singleInstance"
            android:taskAffinity="" android:excludeFromRecents="true" android:showWhenLocked="true"
            android:turnScreenOn="true" android:theme="@android:style/Theme.Material.NoActionBar"/>
        <service android:name=".AlarmService" android:exported="false" android:directBootAware="true" android:foregroundServiceType="mediaPlayback"/>
        <activity android:name=".BlockActivity" android:exported="false" android:launchMode="singleTask"
            android:taskAffinity="" android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Material.NoActionBar"/>
        <service android:name=".BlkService" android:exported="true" android:label="17-32 bloklash"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/blk_service"/>
        </service>
        <activity android:name=".AskActivity" android:exported="false" android:launchMode="singleTask"
            android:taskAffinity="" android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Material.NoActionBar"/>
        <service android:name=".NotifFilter" android:exported="true" android:label="17-32 bildirishnoma filtri"
            android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE">
            <intent-filter>
                <action android:name="android.service.notification.NotificationListenerService"/>
            </intent-filter>
        </service>
        <receiver android:name=".FocusEndReceiver" android:exported="false"/>
        <receiver android:name=".AlarmReceiver" android:exported="false" android:directBootAware="true"/>
        <receiver android:name=".NotifReceiver" android:exported="false" android:directBootAware="true"/>
        <receiver android:name=".BootReceiver" android:exported="true" android:directBootAware="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.LOCKED_BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON"/>
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
                <action android:name="android.intent.action.TIME_SET"/>
                <action android:name="android.intent.action.TIMEZONE_CHANGED"/>
                <action android:name="android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED"/>
            </intent-filter>
        </receiver>
        <receiver android:name=".TrackerWidget" android:exported="false">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE"/>
            </intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/tracker_widget_info"/>
        </receiver>
'''
if 'AlarmActivity' not in s:
    i = s.index('<application')
    s = s[:i] + perms.lstrip() + '\n    ' + s[i:]
    j = s.rindex('</application>')
    s = s[:j] + comps + '    ' + s[j:]
open(mf, 'w', encoding='utf8').write(s)
print('inject ok')

# ---- minSdk 23 ----
vg = 'android/variables.gradle'
if os.path.exists(vg):
    v = open(vg, encoding='utf8').read()
    v = re.sub(r'minSdkVersion\s*=\s*\d+', 'minSdkVersion = 23', v)
    open(vg, 'w', encoding='utf8').write(v)
    print('minSdk 23 ok')

# ---- yiqilish oynasi ----
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
if 'CrashApp' not in s:
    s = s.replace('<application', '<application android:name=".CrashApp"', 1)
    j = s.rindex('</application>')
    s = s[:j] + '        <activity android:name=".CrashActivity" android:exported="false" android:process=":crash" android:excludeFromRecents="true" android:theme="@android:style/Theme.Material.Light.NoActionBar"/>\n    ' + s[j:]
    open(mf, 'w', encoding='utf8').write(s)
    print('crash screen ok')

# ---- barmoq izi kutubxonasi ----
bg = 'android/app/build.gradle'
g = open(bg, encoding='utf8').read()
if 'androidx.biometric' not in g:
    g += '\n\ndependencies {\n    implementation "androidx.biometric:biometric:1.1.0"\n}\n'
    open(bg, 'w', encoding='utf8').write(g)
    print('biometric dep ok')

# ---- MainActivity bir nusxada ochilsin (HOME/launcher rejimi bu ilovada yo'q) ----
import re as _re
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
m = _re.search(r'<activity[^>]*\.MainActivity[^>]*>', s)
if m and 'launchMode' not in m.group(0):
    s = s[:m.end() - 1] + ' android:launchMode="singleTask"' + s[m.end() - 1:]
    open(mf, 'w', encoding='utf8').write(s)
    print('main singleTask ok')

# ---- tizim wallpaperini o'rnatish ruxsati (yashil fon hamma joyda bir xil bo'lishi uchun) ----
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
if 'SET_WALLPAPER' not in s:
    i = s.index('<application')
    s = s[:i] + '<uses-permission android:name="android.permission.SET_WALLPAPER"/>\n    ' + s[i:]
    open(mf, 'w', encoding='utf8').write(s)
    print('wallpaper perm ok')

# ---- kamera chuqurchasi (notch): ko'ndalang holatda chetda "ajralgan" yo'l qolmasligi uchun (Oppo/Realme, Huawei, Xiaomi) ----
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
if 'android.notch_support' not in s:
    import re as _re2
    m = _re2.search(r'<application[^>]*>', s)
    if m:
        meta = '\n        <meta-data android:name="android.notch_support" android:value="true"/>' \
               '\n        <meta-data android:name="notch.config" android:value="portrait|landscape"/>'
        s = s[:m.end()] + meta + s[m.end():]
        open(mf, 'w', encoding='utf8').write(s)
        print('notch meta ok')

# ---- taymer: qabul qiluvchi + jonli bildirishnoma ruxsati ----
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
if 'TimerReceiver' not in s:
    j = s.rindex('</application>')
    s = s[:j] + '        <receiver android:name=".TimerReceiver" android:exported="false" android:directBootAware="true"/>\n    ' + s[j:]
    if 'POST_PROMOTED_NOTIFICATIONS' not in s:
        k = s.index('<application')
        s = s[:k] + '<uses-permission android:name="android.permission.POST_PROMOTED_NOTIFICATIONS"/>\n    ' + s[k:]
    open(mf, 'w', encoding='utf8').write(s)
    print('timer receiver ok')

# ---- sayt bloklash: lokal VPN (DNS filtr) xizmati + tarmoq holati ruxsati ----
mf = 'android/app/src/main/AndroidManifest.xml'
s = open(mf, encoding='utf8').read()
if 'SiteVpn' not in s:
    for pm in ['INTERNET', 'ACCESS_NETWORK_STATE']:
        if ('android.permission.' + pm) not in s:
            k = s.index('<application')
            s = s[:k] + '<uses-permission android:name="android.permission.%s"/>\n    ' % pm + s[k:]
    j = s.rindex('</application>')
    s = s[:j] + '''        <service android:name=".SiteVpn" android:exported="false" android:permission="android.permission.BIND_VPN_SERVICE">
            <intent-filter>
                <action android:name="android.net.VpnService"/>
            </intent-filter>
        </service>
    ''' + s[j:]
    open(mf, 'w', encoding='utf8').write(s)
    print('site vpn service ok')
